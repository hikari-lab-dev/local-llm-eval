"""claude- モデル用の経路（Claude CLI 起動・summary 生成）を、偽の CLI で確認する。"""

from __future__ import annotations

import json
import stat
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from eval_lib import claude_cli, claude_worker
from eval_lib.runner import (
    LOCAL_AGENT_SCRIPT,
    RunContext,
    Trial,
    _copy_tree,
    _init_git_repo,
)
from eval_lib.tasks import Task

FAKE_CLI = """#!/usr/bin/env python3
import json, os, sys
from pathlib import Path

log = Path(os.environ["FAKE_CLI_LOG"])
plans = json.loads(Path(os.environ["FAKE_CLI_PLAN"]).read_text())
calls = log.read_text().splitlines() if log.exists() else []
plan = plans[min(len(calls), len(plans) - 1)]
with log.open("a") as f:
    f.write(json.dumps({"argv": sys.argv[1:], "prompt": sys.stdin.read(), "cwd": os.getcwd()}) + "\\n")
for name, content in plan.get("write", {}).items():
    Path(name).write_text(content)
tool = {"type": "tool_use", "name": "Write", "input": {"file_path": "x"}}
events = [
    {"type": "assistant", "message": {"content": [tool, tool]}},
    {"type": "user", "message": {"content": [{"type": "tool_result", "is_error": True}]}},
    {
        "type": "result",
        "subtype": plan.get("subtype", "success"),
        "is_error": False,
        "result": "done",
        "session_id": "sess-%d" % len(calls),
        "num_turns": 3,
        "total_cost_usd": 0.01,
        "usage": {"input_tokens": 10, "cache_read_input_tokens": 5, "output_tokens": 7,
                  "output_tokens_details": {"thinking_tokens": 2}},
        "modelUsage": {"claude-haiku-5-5": {}},
    },
]
print(json.dumps(events))
"""

needs_local_agent = pytest.mark.skipif(
    LOCAL_AGENT_SCRIPT is None or not LOCAL_AGENT_SCRIPT.exists(), reason="local_agent.py が無い環境"
)


@pytest.fixture
def fake_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    script = tmp_path / "fake-claude"
    script.write_text(FAKE_CLI, encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setattr(claude_cli, "CLAUDE_BIN", script)
    monkeypatch.setenv("FAKE_CLI_LOG", str(tmp_path / "calls.jsonl"))
    plan_path = tmp_path / "plan.json"
    monkeypatch.setenv("FAKE_CLI_PLAN", str(plan_path))

    def configure(plans: list[dict]) -> Callable[[], list[dict]]:
        plan_path.write_text(json.dumps(plans), encoding="utf-8")
        log = tmp_path / "calls.jsonl"
        return lambda: [json.loads(line) for line in log.read_text().splitlines()]

    return configure


def _make_task(tmp_path: Path) -> Task:
    task_dir = tmp_path / "task"
    (task_dir / "repo").mkdir(parents=True)
    (task_dir / "repo" / "protected.txt").write_text("keep", encoding="utf-8")
    (task_dir / "spec.md").write_text("out.txt に ok と書く", encoding="utf-8")
    verify = f"{sys.executable} -c \"import sys; sys.exit(0 if open('out.txt').read() == 'ok' else 1)\""
    return Task(
        id="python/fake",
        lang="python",
        difficulty="easy",
        verify=verify,
        grade=verify,
        timeout=30,
        dir=task_dir,
        editable=["out.txt", "protected.txt"],
        protected=["protected.txt"],
    )


@pytest.fixture
def job_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    la = claude_worker.load_local_agent(LOCAL_AGENT_SCRIPT)
    monkeypatch.setattr(la, "WORKTREES_DIR", tmp_path / "worktrees")
    monkeypatch.setattr(la, "JOBS_DIR", tmp_path / "jobs")
    task = _make_task(tmp_path)
    repo = tmp_path / "repo"
    _copy_tree(task.dir / "repo", repo)
    _init_git_repo(repo)
    ctx = RunContext(out_dir=tmp_path / "out")
    return Trial(task=task, model="claude-haiku-5-5", trial=1, tag="t"), repo, ctx


def _run_fake(tmp_path: Path) -> claude_cli.ClaudeResult:
    call = claude_cli.ClaudeCall(
        "hi", "claude-haiku-5-5", tmp_path, ("Read", "Bash"), 5, 30
    )
    return claude_cli.run_claude(call)


def test_run_claude_isolates_settings(tmp_path: Path, fake_cli) -> None:
    calls = fake_cli([{}])
    _run_fake(tmp_path)
    argv = calls()[0]["argv"]
    picked = {
        "setting_sources": argv[argv.index("--setting-sources") + 1],
        "strict_mcp": "--strict-mcp-config" in argv,
        "tools": argv[argv.index("--tools") + 1],
    }
    assert picked == {"setting_sources": "", "strict_mcp": True, "tools": "Read,Bash"}


def test_run_claude_parses_result(tmp_path: Path, fake_cli) -> None:
    fake_cli([{}])
    result = _run_fake(tmp_path)
    parsed = {
        "status": result.status,
        "turns": result.num_turns,
        "cost": result.cost_usd,
        "tokens": (result.input_tokens, result.output_tokens, result.reasoning_tokens),
        "tools": (
            result.tool_counts,
            result.tool_errors,
            result.max_repeat_tool_streak,
        ),
        "models": result.models_used,
    }
    assert parsed == {
        "status": "completed",
        "turns": 3,
        "cost": 0.01,
        "tokens": (15, 7, 2),
        "tools": ({"Write": 2}, 1, 2),
        "models": ("claude-haiku-5-5",),
    }


@needs_local_agent
def test_code_path_retries_in_same_session_until_verify_passes(
    job_env, fake_cli
) -> None:
    calls = fake_cli([{"write": {"out.txt": "bad"}}, {"write": {"out.txt": "ok"}}])
    trial, repo, ctx = job_env
    summary = claude_worker.run_claude_agent(trial, repo, ctx)
    retry = calls()[1]
    resumed = retry["argv"][retry["argv"].index("--resume") + 1]
    observed = {
        "status": summary["status"],
        "attempts": len(summary["attempts"]),
        "resumed": resumed,
        "failure_in_prompt": "前回の試行は検証コマンドが失敗しました"
        in retry["prompt"],
        "output_tokens": summary["tokens"]["output"],
    }
    assert observed == {
        "status": "success",
        "attempts": 2,
        "resumed": "sess-0",
        "failure_in_prompt": True,
        "output_tokens": 14,
    }


@needs_local_agent
def test_code_path_aborts_on_scope_violation_without_retry(job_env, fake_cli) -> None:
    calls = fake_cli([{"write": {"protected.txt": "changed"}}])
    trial, repo, ctx = job_env
    summary = claude_worker.run_claude_agent(trial, repo, ctx)
    observed = (summary["status"], summary["scope_violation_files"], len(calls()))
    assert observed == ("scope_violation", ["protected.txt"], 1)


@needs_local_agent
def test_code_path_gives_up_after_retries_with_verify_failed(job_env, fake_cli) -> None:
    calls = fake_cli([{"write": {"out.txt": "bad"}}])
    trial, repo, ctx = job_env
    summary = claude_worker.run_claude_agent(trial, repo, ctx)
    observed = (summary["status"], len(calls()))
    assert observed == ("verify_failed", claude_worker.DEFAULT_RETRIES + 1)
