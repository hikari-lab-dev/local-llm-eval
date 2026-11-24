"""eval_lib.runner のコマンド組み立て・cleanup 順序のテスト。"""

from pathlib import Path

import pytest

from eval_lib import runner
from eval_lib.runner import RunContext, Trial
from eval_lib.tasks import Task


AGENT = Path("/tmp/agent/local_agent.py")


def _make_task(**overrides: object) -> Task:
    """テスト用の最小限の Task を作る。"""
    defaults: dict = {
        "id": "python/01-sample",
        "lang": "python",
        "difficulty": "easy",
        "verify": "true",
        "grade": "true",
        "timeout": None,
        "dir": Path("/tmp/does-not-matter"),
    }
    defaults.update(overrides)
    return Task(**defaults)


def test_build_local_agent_command_includes_editable_flags() -> None:
    """task.editable の各パターンが --editable として1つずつ渡される。"""
    task = _make_task(editable=["a.py", "tests/test_new_*.py"])
    trial = Trial(task=task, model="m1", trial=1)
    ctx = RunContext(out_dir=Path("/tmp/out"), local_agent_script=AGENT)

    command = runner._build_local_agent_command(trial, Path("/tmp/repo"), ctx)

    assert command.count("--editable") == 2
    assert "a.py" in command
    assert "tests/test_new_*.py" in command


def test_build_local_agent_command_includes_protected_flags() -> None:
    """task.protected の各パターンが --protected として1つずつ渡される。"""
    task = _make_task(protected=["tests/test_core.py"])
    trial = Trial(task=task, model="m1", trial=1)
    ctx = RunContext(out_dir=Path("/tmp/out"), local_agent_script=AGENT)

    command = runner._build_local_agent_command(trial, Path("/tmp/repo"), ctx)

    assert command.count("--protected") == 1
    assert "tests/test_core.py" in command


def test_build_local_agent_command_omits_flags_when_not_set() -> None:
    """editable/protected が未設定（None）なら --editable/--protected を渡さない。"""
    task = _make_task()
    trial = Trial(task=task, model="m1", trial=1)
    ctx = RunContext(out_dir=Path("/tmp/out"), local_agent_script=AGENT)

    command = runner._build_local_agent_command(trial, Path("/tmp/repo"), ctx)

    assert "--editable" not in command
    assert "--protected" not in command


def test_grade_and_cleanup_runs_cleanup_even_if_grading_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """採点中に例外が起きても cleanup（_cleanup_job）は必ず実行する。

    一時リポジトリが削除される前に worktree 側の git worktree remove を
    終わらせておかないと、worktree が実行役の作業場所に残留するため。
    """
    cleanup_calls: list[dict] = []
    monkeypatch.setattr(
        runner, "_cleanup_job", lambda summary, _ctx: cleanup_calls.append(summary)
    )
    monkeypatch.setattr(
        runner,
        "compute_lint_pass",
        lambda _s: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    task = _make_task()
    trial = Trial(task=task, model="m1", trial=1)
    ctx = RunContext(out_dir=Path("/tmp/out"), local_agent_script=AGENT)
    summary = {"branch": "local/job1", "worktree": "/tmp/worktree"}

    with pytest.raises(RuntimeError):
        runner._grade_and_cleanup(trial, summary, ctx)

    assert cleanup_calls == [summary]


def _summary(**extra: object) -> dict:
    return {"status": "success", "attempts": [], **extra}


def _trial() -> Trial:
    task = Task(
        id="python/x",
        lang="python",
        difficulty="easy",
        verify="v",
        grade="g",
        timeout=None,
        dir=Path("."),
    )
    return Trial(task=task, model="m", trial=1)


def test_build_record_copies_usage_fields() -> None:
    summary = _summary(
        tokens={"input": 1, "output": 2, "reasoning": 3, "cache_read": 4},
        length_stop_count=5,
        max_repeat_tool_streak=6,
    )
    record = runner._build_record(_trial(), summary, True, True)
    usage = {
        key: record[key]
        for key in (
            "input_tokens",
            "output_tokens",
            "reasoning_tokens",
            "length_stop_count",
            "max_repeat_tool_streak",
        )
    }
    assert usage == {
        "input_tokens": 1,
        "output_tokens": 2,
        "reasoning_tokens": 3,
        "length_stop_count": 5,
        "max_repeat_tool_streak": 6,
    }


def test_build_record_tolerates_legacy_summary_without_usage() -> None:
    record = runner._build_record(_trial(), _summary(), True, None)
    assert record["output_tokens"] is None


def test_child_env_points_claude_biome_at_installed_binary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    biome = tmp_path / "biome"
    biome.write_text("")
    monkeypatch.setattr(runner, "BIOME_BIN", biome)
    assert runner._child_env()["CLAUDE_BIOME"] == str(biome)


def test_child_env_leaves_env_untouched_when_biome_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CLAUDE_BIOME", raising=False)
    monkeypatch.setattr(runner, "BIOME_BIN", tmp_path / "missing")
    assert "CLAUDE_BIOME" not in runner._child_env()


def test_build_local_agent_command_ctx_timeout_overrides_task_timeout() -> None:
    """ctx.timeout があれば課題の timeout より優先して --timeout に渡す。"""
    trial = Trial(task=_make_task(timeout=900), model="m1", trial=1)

    overridden = runner._build_local_agent_command(
        trial, Path("/tmp/repo"), RunContext(out_dir=Path("/tmp/out"), timeout=300, local_agent_script=AGENT)
    )
    default = runner._build_local_agent_command(
        trial, Path("/tmp/repo"), RunContext(out_dir=Path("/tmp/out"), local_agent_script=AGENT)
    )

    assert overridden[overridden.index("--timeout") + 1] == "300"
    assert default[default.index("--timeout") + 1] == "900"


def test_missing_local_agent_fails_with_clear_message() -> None:
    """実行役が未指定のまま run に進むと、指定方法を示して失敗する。"""
    trial = Trial(task=_make_task(), model="m1", trial=1)
    ctx = RunContext(out_dir=Path("/tmp/out"), local_agent_script=None)
    with pytest.raises(RuntimeError, match="LOCAL_AGENT_SCRIPT"):
        runner._build_local_agent_command(trial, Path("/tmp/repo"), ctx)
