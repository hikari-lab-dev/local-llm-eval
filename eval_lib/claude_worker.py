"""Claude（claude- 始まりのモデル）を、local_agent.py run と同じ形の summary で実行する。

worktree 作成・scope 判定・検証・lint・コミット・ジョブ台帳は local_agent.py 側の関数を
import して使い、ローカル経路との判定差が出ないようにする。差し替えるのは「モデルを動かす部分」だけ。
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING

from eval_lib.claude_cli import ClaudeCall, ClaudeResult, run_claude

if TYPE_CHECKING:
    from eval_lib.runner import RunContext, Trial

CODE_TOOLS = ("Read", "Write", "Edit", "Glob", "Grep", "Bash")
DEFAULT_RETRIES = 2
DEFAULT_MAX_TURNS = 60
DEFAULT_ATTEMPT_TIMEOUT = 1200.0
CONTINUE_LEAD = "同じセッションの続きです。"


@dataclass(frozen=True)
class _Session:
    """1 試行（ジョブ）の間は変わらない実行条件。"""

    la: ModuleType
    trial: Trial
    ctx: RunContext
    worktree: Path
    base_commit: str
    system_prompt: str | None
    spec_text: str


@dataclass(frozen=True)
class _Cycle:
    """1 回の claude 実行と、その後の判定結果。"""

    record: dict
    verify_result: tuple[int, str]
    lint_result: tuple[int, str] | None
    terminal: bool
    diff_stat_text: str
    kind: str = "ran"
    status_override: str | None = None
    scope_violation_files: list[str] = field(default_factory=list)


def load_local_agent(script: Path) -> ModuleType:
    """local_agent.py を import する（兄弟モジュールを解決するため scripts ディレクトリを sys.path に足す）。"""
    scripts_dir = str(script.resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    return importlib.import_module(script.stem)


def rules_system_prompt(profile: str | None) -> str | None:
    """--profile の AGENTS.md と opencode.json の instructions を連結する（ローカルが読む規約と同じ文面）。"""
    if not profile:
        return None
    root = Path(profile).expanduser()
    config = json.loads((root / "opencode.json").read_text(encoding="utf-8"))
    paths = [
        root / "AGENTS.md",
        *(Path(p).expanduser() for p in config.get("instructions", [])),
    ]
    return "\n\n".join(p.read_text(encoding="utf-8-sig") for p in paths if p.is_file())


def _step_cap(profile: str | None) -> int:
    """worker エージェントの steps 上限（ローカルは opencode.json、無ければ既定の設定）。"""
    root = Path(profile).expanduser() if profile else Path.home() / ".config/opencode"
    path = root / "opencode.json"
    if not path.is_file():
        return DEFAULT_MAX_TURNS
    config = json.loads(path.read_text(encoding="utf-8"))
    steps = config.get("agent", {}).get("worker", {}).get("steps")
    return steps if isinstance(steps, int) and steps > 0 else DEFAULT_MAX_TURNS


def _attempt_timeout(trial: Trial, ctx: RunContext) -> float:
    if ctx.timeout is not None:
        return float(ctx.timeout)
    return float(trial.task.timeout or DEFAULT_ATTEMPT_TIMEOUT)


def _tokens(result: ClaudeResult) -> dict:
    return {
        "input": result.input_tokens,
        "output": result.output_tokens,
        "reasoning": result.reasoning_tokens,
        "cache_read": result.cache_read_tokens,
    }


def _attempt_record(
    result: ClaudeResult,
    verify_result: tuple[int, str] | None,
    lint_result: tuple[int, str] | None,
    no_diff: bool,
) -> dict:
    record = {
        "status": result.status,
        "duration_seconds": result.duration_seconds,
        "step_count": result.num_turns,
        "tool_call_count": sum(result.tool_counts.values()),
        "tool_error_count": result.tool_errors,
        "tool_call_leak_count": 0,
        "error_tail": result.error_tail,
        "tokens": _tokens(result),
        "length_stop_count": 0,
        "max_repeat_tool_streak": result.max_repeat_tool_streak,
        "cost_usd": result.cost_usd,
        "models_used": list(result.models_used),
        "no_diff": no_diff,
    }
    if verify_result is not None:
        record["verify_exit_code"] = verify_result[0]
    if lint_result is not None:
        record["lint_exit_code"] = lint_result[0]
    return record


def _early_cycle(result: ClaudeResult, diff: str, no_diff: bool, kind: str) -> _Cycle:
    """検証せず再試行の対象にする試行。no_run の最終 status は、正常終了扱いの 0 ターンなら crash。"""
    record = _attempt_record(result, None, None, no_diff)
    crashed = result.status in ("completed", "crash")
    override = ("crash" if crashed else result.status) if kind == "no_run" else kind
    return _Cycle(record, (1, ""), None, False, diff, kind, override)


def _process(session: _Session, result: ClaudeResult, previous_diff: str) -> _Cycle:
    """実行なし・変更なし・scope 違反・検証/lint の順で判定する（local_agent._process_attempt と同順）。"""
    la, worktree = session.la, session.worktree
    diff = la.diff_stat(worktree, session.base_commit)
    no_diff = diff == previous_diff
    if result.status == "crash" or result.num_turns == 0:
        return _early_cycle(result, diff, no_diff, "no_run")
    changes = la.path_changes_since(worktree, session.base_commit)
    if not changes:
        return _early_cycle(result, diff, no_diff, "no_change")
    task = session.trial.task
    violations = la.find_scope_violations(changes, task.editable, task.protected)
    if violations:
        record = _attempt_record(result, None, None, no_diff)
        return _Cycle(
            record, (1, ""), None, True, diff, "abort", "scope_violation", violations
        )
    return _verified_cycle(session, result, diff, no_diff)


def _verified_cycle(
    session: _Session, result: ClaudeResult, diff: str, no_diff: bool
) -> _Cycle:
    la = session.la
    verify_result = la.run_verify(session.worktree, session.trial.task.verify)
    run_lint = verify_result[0] == 0 and session.ctx.lint
    lint_result = (
        la.run_lint(session.worktree, session.base_commit) if run_lint else None
    )
    record = _attempt_record(result, verify_result, lint_result, no_diff)
    lint_ok = lint_result is None or lint_result[0] != 1
    terminal = verify_result[0] == 0 and lint_ok
    return _Cycle(record, verify_result, lint_result, terminal, diff)


def _next_prompt(
    session: _Session, cycle: _Cycle, result: ClaudeResult
) -> tuple[str, str | None]:
    """次の試行のプロンプトと resume 先。続行できるセッションがあれば失敗内容だけを渡す。"""
    la = session.la
    verify_cmd = session.trial.task.verify
    resume = result.session_id
    lead = CONTINUE_LEAD if resume else session.spec_text
    if cycle.kind == "no_run":
        return la.build_prompt(session.spec_text, verify_cmd, None), None
    if cycle.kind == "no_change":
        return la.build_prompt(lead, verify_cmd, la.NO_CHANGE_CONTEXT), resume
    if cycle.verify_result[0] != 0:
        context = la.build_failure_context(
            cycle.verify_result[1], la.diff_stat(session.worktree, "HEAD")
        )
        return la.build_prompt(lead, verify_cmd, context), resume
    context = la.build_lint_failure_context(
        la.LintResult(*(cycle.lint_result or (1, "")))
    )
    return la.build_prompt(lead, verify_cmd, context), resume


def _call(session: _Session, prompt: str, resume: str | None) -> ClaudeCall:
    return ClaudeCall(
        prompt=prompt,
        model=session.trial.model,
        cwd=session.worktree,
        tools=CODE_TOOLS,
        max_turns=_step_cap(session.ctx.profile),
        timeout=_attempt_timeout(session.trial, session.ctx),
        system_prompt=session.system_prompt,
        resume=resume,
        persist_session=True,
    )


def _run_attempts(session: _Session) -> tuple[list[_Cycle], list[ClaudeResult]]:
    """検証（有効なら lint も）が通るか再試行を使い切るまで、同じセッションで claude を繰り返す。"""
    la = session.la
    cycles: list[_Cycle] = []
    results: list[ClaudeResult] = []
    prompt, resume = (
        la.build_prompt(session.spec_text, session.trial.task.verify, None),
        None,
    )
    previous_diff = ""
    for index in range(DEFAULT_RETRIES + 1):
        result = run_claude(_call(session, prompt, resume))
        (session.ctx.out_dir / f"attempt-{index + 1}.json").write_text(
            result.raw_stdout, encoding="utf-8"
        )
        cycle = _process(session, result, previous_diff)
        cycles.append(cycle)
        results.append(result)
        previous_diff = cycle.diff_stat_text
        if cycle.terminal or index == DEFAULT_RETRIES:
            break
        prompt, resume = _next_prompt(session, cycle, result)
    return cycles, results


def _final_status(cycles: list[_Cycle]) -> str:
    last = cycles[-1]
    if last.status_override:
        return last.status_override
    if last.verify_result[0] != 0:
        status = last.record["status"]
        return "verify_failed" if status == "completed" else status
    lint_failed = last.lint_result is not None and last.lint_result[0] == 1
    return "lint_failed" if lint_failed else "success"


def _lint_summary(lint_result: tuple[int, str], la: ModuleType) -> dict:
    lint = la.LintResult(*lint_result)
    record: dict = {"exit_code": lint.exit_code, "output_tail": lint.output_tail}
    if lint.errors is not None:
        record["base_errors"] = lint.base_errors
        record["errors"] = lint.errors
    if lint.exit_code == 2:
        record["note"] = "unverifiable"
    return record


def _token_totals(results: list[ClaudeResult]) -> dict:
    totals = [_tokens(r) for r in results]
    return {key: sum(t[key] for t in totals) for key in totals[0]}


def _summary(
    session: _Session, cycles: list[_Cycle], results: list[ClaudeResult], branch: str
) -> dict:
    la = session.la
    status = _final_status(cycles)
    last = cycles[-1]
    summary = {
        "status": status,
        "attempts": [c.record for c in cycles],
        "verify": {
            "exit_code": last.verify_result[0],
            "output_tail": last.verify_result[1],
        },
        "branch": branch,
        "worktree": str(session.worktree),
        "base_commit": session.base_commit,
        "committed": la.commit_all(session.worktree, f"claude-worker: {branch}"),
        "total_seconds": round(sum(r.duration_seconds for r in results), 1),
        "escalate": status != "success",
        "tokens": _token_totals(results),
        "length_stop_count": 0,
        "max_repeat_tool_streak": max(r.max_repeat_tool_streak for r in results),
        "cost_usd": round(sum(r.cost_usd for r in results), 6),
    }
    summary["diff_stat"] = la.diff_stat(session.worktree, session.base_commit)
    if last.lint_result is not None:
        summary["lint"] = _lint_summary(last.lint_result, la)
    if last.scope_violation_files:
        summary["scope_violation_files"] = last.scope_violation_files
    return summary


def _crash_summary(session: _Session, branch: str, exc: BaseException) -> dict:
    """想定外の git / ファイル I/O 例外を internal_error にし、呼び出し側が cleanup できるよう worktree を残す。"""
    return {
        "status": "internal_error",
        "attempts": [],
        "verify": None,
        "branch": branch,
        "worktree": str(session.worktree),
        "base_commit": session.base_commit,
        "diff_stat": "",
        "committed": False,
        "total_seconds": 0.0,
        "escalate": True,
        "tokens": {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0},
        "length_stop_count": 0,
        "max_repeat_tool_streak": 0,
        "error": f"{type(exc).__name__}: {exc}",
    }


def _run_session(session: _Session, branch: str) -> dict:
    try:
        cycles, results = _run_attempts(session)
        return _summary(session, cycles, results, branch)
    except (subprocess.CalledProcessError, OSError) as exc:
        return _crash_summary(session, branch, exc)


def _start_session(
    trial: Trial, repo_path: Path, ctx: RunContext, spec_text: str | None
) -> tuple[_Session, str]:
    """worktree とジョブ台帳（cleanup が参照する）を作る。"""
    from eval_lib.runner import require_local_agent

    la = load_local_agent(require_local_agent(ctx))
    job_id = la.generate_job_id()
    worktree = la.WORKTREES_DIR / job_id
    branch = f"local/{job_id}"
    base_commit = la.create_worktree(repo_path, worktree, branch)
    now = datetime.now(UTC).isoformat()
    la.save_job(
        la.JOBS_DIR,
        la.JobRecord(job_id, str(repo_path), str(worktree), branch, "running", now),
    )
    spec = spec_text or (trial.task.dir / "spec.md").read_text(
        encoding="utf-8", errors="replace"
    )
    session = _Session(
        la, trial, ctx, worktree, base_commit, rules_system_prompt(ctx.profile), spec
    )
    return session, branch


def run_claude_agent(
    trial: Trial, repo_path: Path, ctx: RunContext, spec_text: str | None = None
) -> dict:
    """repo_path から worktree を切って claude を実行し、local_agent.py run と同形の summary を返す。

    spec_text を渡すと課題ディレクトリの spec.md の代わりに使う（イシュー直接投入用）。
    """
    ctx.out_dir.mkdir(parents=True, exist_ok=True)
    session, branch = _start_session(trial, repo_path, ctx, spec_text)
    summary = _run_session(session, branch)
    (ctx.out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary
