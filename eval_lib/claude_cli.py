"""Claude Code CLI（`claude -p`）のヘッドレス実行。コードスイートと汎用スイートで共用する。

個人設定（CLAUDE.md・rules・hooks・プラグイン・MCP・自動メモリ）が評価に混ざらないよう、
設定の読み込み元を空にして起動する。認証は CLI 自身の OAuth（サブスクリプション）を使う。
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

CLAUDE_BIN = Path(os.environ.get("CLAUDE_BIN") or Path.home() / ".local/bin/claude")
CLAUDE_MODEL_PREFIX = "claude-"
# 親の Claude Code セッションの変数と API キー（OAuth ではなく従量課金に切り替わる）を子へ渡さない
_SCRUBBED_ENV_PREFIXES = ("CLAUDE", "ANTHROPIC")
# 設定の読み込み元を空にし、MCP・スキルも無効化。権限確認で止まらないよう dontAsk + 許可ツール明示
_ISOLATION_FLAGS = (
    "--output-format",
    "json",
    "--setting-sources",
    "",
    "--settings",
    json.dumps({"autoMemoryEnabled": False}),
    "--strict-mcp-config",
    "--disable-slash-commands",
    "--permission-mode",
    "dontAsk",
)
_RESULT_STATUS = {"success": "completed", "error_max_turns": "step_limit"}


def is_claude_model(model: str) -> bool:
    """claude- で始まるモデル名なら Claude CLI 経路を通す。"""
    return model.startswith(CLAUDE_MODEL_PREFIX)


@dataclass(frozen=True)
class ClaudeCall:
    """`claude -p` 1 回ぶんの起動条件。"""

    prompt: str
    model: str
    cwd: Path
    tools: tuple[str, ...]
    max_turns: int
    timeout: float
    system_prompt: str | None = None
    resume: str | None = None
    persist_session: bool = False


@dataclass(frozen=True)
class ClaudeResult:
    """`claude -p --output-format json` の出力を、評価レコード向けに畳んだもの。"""

    status: str
    returncode: int
    duration_seconds: float
    text: str = ""
    session_id: str | None = None
    num_turns: int = 0
    cost_usd: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    cache_read_tokens: int = 0
    models_used: tuple[str, ...] = ()
    tool_counts: dict[str, int] = field(default_factory=dict)
    tool_errors: int = 0
    max_repeat_tool_streak: int = 0
    raw_stdout: str = ""
    error_tail: str = ""


def build_command(call: ClaudeCall) -> list[str]:
    """隔離フラグ付きの起動コマンドを組み立てる。プロンプトは標準入力で渡す。"""
    tools = ",".join(call.tools)
    command = [
        str(CLAUDE_BIN),
        "-p",
        "--model",
        call.model,
        *_ISOLATION_FLAGS,
        "--tools",
        tools,
        "--allowedTools",
        tools,
        "--max-turns",
        str(call.max_turns),
    ]
    if not call.persist_session:
        command.append("--no-session-persistence")
    if call.system_prompt:
        command.extend(["--append-system-prompt", call.system_prompt])
    if call.resume:
        command.extend(["--resume", call.resume])
    return command


def _child_env() -> dict[str, str]:
    return {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(_SCRUBBED_ENV_PREFIXES)
    }


class _Output(NamedTuple):
    stdout: str
    stderr: str
    timed_out: bool


def _communicate(process: subprocess.Popen, call: ClaudeCall) -> _Output:
    """プロンプトを渡して出力を待つ。時間切れはプロセスグループごと止める。"""
    try:
        stdout, stderr = process.communicate(call.prompt, timeout=call.timeout)
        return _Output(stdout, stderr, False)
    except subprocess.TimeoutExpired as exc:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        return _Output("", f"timeout after {exc.timeout}s", True)


def run_claude(call: ClaudeCall) -> ClaudeResult:
    """claude -p を実行して結果を返す。時間切れは status="timeout"、出力なしは "crash"。"""
    started = time.monotonic()
    process = subprocess.Popen(
        build_command(call),
        cwd=call.cwd,
        env=_child_env(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        start_new_session=True,
    )
    output = _communicate(process, call)
    elapsed = round(time.monotonic() - started, 1)
    if output.timed_out:
        return ClaudeResult("timeout", -1, elapsed, error_tail=output.stderr)
    return parse_output(output.stdout, output.stderr, process.returncode, elapsed)


def parse_output(
    stdout: str, stderr: str, returncode: int, duration_seconds: float
) -> ClaudeResult:
    """--output-format json の配列から type=="result" を取り出して ClaudeResult にする。"""
    events = _load_events(stdout)
    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    if result is None:
        tail = (stderr or stdout)[-500:]
        return ClaudeResult(
            "crash", returncode, duration_seconds, raw_stdout=stdout, error_tail=tail
        )
    return ClaudeResult(
        returncode=returncode,
        duration_seconds=duration_seconds,
        raw_stdout=stdout,
        **_result_fields(events, result),
    )


def _load_events(stdout: str) -> list[dict]:
    try:
        parsed = json.loads(stdout)
        return (
            [e for e in parsed if isinstance(e, dict)]
            if isinstance(parsed, list)
            else []
        )
    except ValueError as exc:
        return [{"type": "parse_error", "message": str(exc)}]


def _result_fields(events: list[dict], result: dict) -> dict:
    usage = result.get("usage") or {}
    status = _RESULT_STATUS.get(str(result.get("subtype")), "crash")
    if status == "completed" and result.get("is_error"):
        status = "crash"
    counts, errors, streak = _tool_stats(events)
    return {
        "status": status,
        "text": result.get("result") or "",
        "session_id": result.get("session_id"),
        "num_turns": int(result.get("num_turns") or 0),
        "cost_usd": float(result.get("total_cost_usd") or 0.0),
        "input_tokens": _input_tokens(usage),
        "output_tokens": int(usage.get("output_tokens") or 0),
        "reasoning_tokens": int(
            (usage.get("output_tokens_details") or {}).get("thinking_tokens") or 0
        ),
        "cache_read_tokens": int(usage.get("cache_read_input_tokens") or 0),
        "models_used": tuple((result.get("modelUsage") or {}).keys()),
        "tool_counts": counts,
        "tool_errors": errors,
        "max_repeat_tool_streak": streak,
        "error_tail": ""
        if status == "completed"
        else str(result.get("subtype"))[-500:],
    }


def _input_tokens(usage: dict) -> int:
    keys = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    return sum(int(usage.get(key) or 0) for key in keys)


def _tool_stats(events: list[dict]) -> tuple[dict[str, int], int, int]:
    """ツール別呼び出し数・ツールエラー数・同一呼び出しの最大連続回数を数える。"""
    counts: dict[str, int] = {}
    errors = streak = best = 0
    previous = None
    for event in events:
        for block in _content_blocks(event):
            if block.get("type") == "tool_result" and block.get("is_error"):
                errors += 1
            if block.get("type") != "tool_use":
                continue
            counts[block["name"]] = counts.get(block["name"], 0) + 1
            signature = (block["name"], json.dumps(block.get("input"), sort_keys=True))
            streak = streak + 1 if signature == previous else 1
            previous = signature
            best = max(best, streak)
    return counts, errors, best


def _content_blocks(event: dict) -> list[dict]:
    if event.get("type") not in ("assistant", "user"):
        return []
    content = (event.get("message") or {}).get("content")
    return (
        [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []
    )
