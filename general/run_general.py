"""汎用作業（Web 調査・文書・推論・データ処理）でローカルLLMを評価するランナー。

課題ごとに作業ディレクトリを新しく作り、OpenCode（websearch 有効）で実行して checks.py で採点する。
結果は results/<tag>.jsonl に 1 課題 1 行で追記する（同じ model と task の行があれば飛ばす）。
"""

from __future__ import annotations

import argparse
import fcntl
import io
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

from checks import CHECKS
from checks_hard import HARD_CHECKS

HERE = Path(__file__).resolve().parent
# 環境に合わせて環境変数で差し替える（既定値は括弧内）。
# OPENCODE_BIN（PATH 上の opencode）、OPENCODE_PROVIDER（local-llm: opencode.json の provider 名）、
# LLAMA_SWAP_URL（http://127.0.0.1:8080/v1/chat/completions）、
# EVAL_RUNS_DIR（~/.local-eval/general-runs: 課題ごとの作業ディレクトリ）、
# GPU_LOCK_FILE（~/.local-eval/gpu.lock: 同じ GPU を使う別の実行と取り合わないためのロック）
OPENCODE = Path(
    os.environ.get("OPENCODE_BIN")
    or shutil.which("opencode")
    or Path.home() / ".opencode/bin/opencode"
)
PROVIDER = os.environ.get("OPENCODE_PROVIDER", "local-llm")
RUNS = Path(
    os.environ.get("EVAL_RUNS_DIR") or Path.home() / ".local-eval/general-runs"
)
GPU_LOCK = Path(
    os.environ.get("GPU_LOCK_FILE") or Path.home() / ".local-eval/gpu.lock"
)
LLAMA_SWAP = os.environ.get(
    "LLAMA_SWAP_URL", "http://127.0.0.1:8080/v1/chat/completions"
)
FOOTER = (
    "\n\n---\n作業ディレクトリ内のファイルだけを使い、指定されたファイルを作業ディレクトリに保存してください。"
    "質問や確認はせず、最後まで自分で作業してください。"
)
WEB_TASKS = {
    "web_gemma",
    "web_release",
    "web_pypi",
    "web_report",
    "web_multi",
    "web_jp",
    "web_mtp",
}
# ローカル側（bash 不可・Web 検索可）に合わせて、Claude にも bash を使わせない
CLAUDE_TOOLS = ("Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch")
CLAUDE_MAX_TURNS = 40
SUITES = {"basic": CHECKS, "hard": HARD_CHECKS}
ALL_CHECKS = {**CHECKS, **HARD_CHECKS}


def _parse_part(line: str) -> dict[str, Any]:
    try:
        return json.loads(line).get("part") or {}
    except (ValueError, AttributeError):
        return {}


def _summarize_events(lines: list[str]) -> dict[str, object]:
    tools: Counter[str] = Counter()
    errors = steps = out_tokens = 0
    last_text = ""
    for part in map(_parse_part, lines):
        if part.get("type") == "tool":
            tools[part.get("tool", "?")] += 1
            errors += part.get("state", {}).get("status") == "error"
        if part.get("type") == "step-finish":
            steps += 1
            out_tokens += (part.get("tokens") or {}).get("output", 0)
        if part.get("type") == "text":
            last_text = part.get("text", "")
    return {
        "tools": dict(tools),
        "tool_errors": errors,
        "steps": steps,
        "output_tokens": out_tokens,
        "final_text": last_text[-500:],
    }


def _invoke(prompt: str, model: str, work: Path, timeout: int) -> tuple[str, int, str]:
    """OpenCode を実行し (stdout, 終了コード, 状態) を返す。時間切れは終了コード -1。"""
    try:
        proc = subprocess.run(
            [
                str(OPENCODE),
                "run",
                "-m",
                f"{PROVIDER}/{model}",
                "--auto",
                "--format",
                "json",
                "--dir",
                str(work),
                prompt,
            ],
            cwd=work,
            env=dict(os.environ, OPENCODE_ENABLE_EXA="1", PWD=str(work)),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return proc.stdout, proc.returncode, "done"
    except subprocess.TimeoutExpired as exc:
        out = (
            exc.stdout.decode("utf-8", "replace")
            if isinstance(exc.stdout, bytes)
            else exc.stdout or ""
        )
        return out, -1, "timeout"


def _invoke_claude(
    prompt: str, model: str, work: Path, timeout: int
) -> tuple[str, int, str, dict[str, object]]:
    """Claude CLI を work で実行し (生の出力, 終了コード, 状態, 集計) を返す。"""
    # スクリプト実行では sys.path[0] が general/ になるため、リポジトリ直下を足してから共用モジュールを読む
    if str(HERE.parent) not in sys.path:
        sys.path.insert(0, str(HERE.parent))
    from eval_lib.claude_cli import ClaudeCall, run_claude

    result = run_claude(
        ClaudeCall(prompt, model, work, CLAUDE_TOOLS, CLAUDE_MAX_TURNS, float(timeout))
    )
    status = {"completed": "done", "step_limit": "done", "timeout": "timeout"}.get(
        result.status, "error"
    )
    return (
        result.raw_stdout,
        result.returncode,
        status,
        {
            "tools": result.tool_counts,
            "tool_errors": result.tool_errors,
            "steps": result.num_turns,
            "output_tokens": result.output_tokens,
            "final_text": result.text[-500:],
            "cost_usd": result.cost_usd,
        },
    )


def _execute(
    prompt: str, model: str, work: Path, timeout: int
) -> tuple[str, int, str, dict[str, object]]:
    if model.startswith("claude-"):
        return _invoke_claude(prompt, model, work, timeout)
    stdout, rc, status = _invoke(prompt, model, work, timeout)
    return stdout, rc, status, _summarize_events(stdout.splitlines())


def _prepare(task: str, model: str, tag: str) -> tuple[Path, str]:
    src = HERE / "tasks" / task
    work = RUNS / tag / model / task
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    if (src / "files").is_dir():
        shutil.copytree(src / "files", work, dirs_exist_ok=True)
    return work, (src / "prompt.md").read_text(encoding="utf-8") + FOOTER


def _warm_up(model: str) -> None:
    """モデルの読み込み時間を計測に含めないよう、短い要求で先に起動しておく。"""
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 1,
        }
    )
    req = urllib.request.Request(
        LLAMA_SWAP, body.encode(), {"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=900) as r:
        r.read()


def run_task(task: str, model: str, tag: str, timeout: int) -> dict[str, object]:
    """同じ GPU を使う別の実行と取り合わないよう、課題 1 件ごとに gpu.lock を取って実行する。

    claude- モデルは GPU を使わないためロックもウォームアップもしない。
    """
    if model.startswith("claude-"):
        return _run_locked(task, model, tag, timeout)
    GPU_LOCK.parent.mkdir(parents=True, exist_ok=True)
    with GPU_LOCK.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        _warm_up(model)
        return _run_locked(task, model, tag, timeout)


def _run_locked(task: str, model: str, tag: str, timeout: int) -> dict[str, object]:
    work, prompt = _prepare(task, model, tag)
    started = time.monotonic()
    stdout, rc, status, summary = _execute(prompt, model, work, timeout)
    elapsed = round(time.monotonic() - started, 1)
    (work.parent / f"{task}.events.jsonl").write_text(stdout, encoding="utf-8")
    score, full, notes = ALL_CHECKS[task](work)
    return {
        "tag": tag,
        "model": model,
        "task": task,
        "web": task in WEB_TASKS,
        "status": status,
        "rc": rc,
        "elapsed_s": elapsed,
        "score": score,
        "max": full,
        "ratio": round(score / full, 3),
        "notes": notes,
        **summary,
        "workdir": str(work),
    }


def _done_keys(path: Path) -> set[tuple[str, str]]:
    if not path.exists():
        return set()
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {(r["model"], r["task"]) for r in rows}


def main() -> int:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--model", action="append", required=True)
    ap.add_argument("--task", action="append", help="省略時は --suite の全課題")
    ap.add_argument("--suite", choices=list(SUITES), default="basic")
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()
    out = HERE / "results" / f"{args.tag}.jsonl"
    out.parent.mkdir(exist_ok=True)
    done = _done_keys(out)
    for model in args.model:
        for task in args.task or list(SUITES[args.suite]):
            if (model, task) in done:
                continue
            row = run_task(task, model, args.tag, args.timeout)
            with out.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(
                f"{model} {task}: {row['score']}/{row['max']} {row['status']} {row['elapsed_s']}s",
                flush=True,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
