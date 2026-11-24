import argparse
from pathlib import Path

import eval as eval_cli
from eval_lib.results import load_records
from eval_lib.runner import RunContext, Trial


def _fake_run_one(trial: Trial, _ctx: RunContext) -> dict:
    """local_agent.py を実際には呼ばず、偽の summary から作ったレコードを返す。"""
    return {
        "task": trial.task.id,
        "lang": trial.task.lang,
        "model": trial.model,
        "trial": trial.trial,
        "tag": trial.tag,
        "worker_status": "success",
        "hidden_pass": True,
        "lint_pass": None,
        "total_seconds": 1.0,
        "step_count": 3,
        "tool_call_count": 5,
        "tool_error_count": 0,
        "diff_lines": 4,
        "timestamp": "2026-01-01T00:00:00+00:00",
    }


def _configure_paths(monkeypatch, tmp_path: Path) -> None:
    """RESULTS_PATH / LOGS_ROOT をテスト用の一時ディレクトリへ差し替える。"""
    monkeypatch.setattr(eval_cli, "RESULTS_PATH", tmp_path / "results.jsonl")
    monkeypatch.setattr(eval_cli, "LOGS_ROOT", tmp_path / "logs")
    monkeypatch.setattr(eval_cli, "run_one", _fake_run_one)


def _run_args(trials: int, tag: str = "baseline") -> argparse.Namespace:
    """cmd_run に渡す最小限の Namespace を作る。"""
    return argparse.Namespace(
        models="m1",
        trials=trials,
        tasks=["python/01-interval-merge"],
        tag=tag,
        lint=False,
        profile=None,
        local_agent_script=None,
    )


def test_cmd_run_appends_one_record(monkeypatch, tmp_path: Path) -> None:
    _configure_paths(monkeypatch, tmp_path)
    eval_cli.cmd_run(_run_args(trials=1))
    records = load_records(tmp_path / "results.jsonl")
    assert len(records) == 1


def test_cmd_run_is_resumable(monkeypatch, tmp_path: Path) -> None:
    _configure_paths(monkeypatch, tmp_path)
    eval_cli.cmd_run(_run_args(trials=1))
    eval_cli.cmd_run(_run_args(trials=1))
    records = load_records(tmp_path / "results.jsonl")
    assert len(records) == 1


def test_cmd_run_multiple_trials_appends_each(monkeypatch, tmp_path: Path) -> None:
    _configure_paths(monkeypatch, tmp_path)
    eval_cli.cmd_run(_run_args(trials=3))
    records = load_records(tmp_path / "results.jsonl")
    assert {record["trial"] for record in records} == {1, 2, 3}


def test_cmd_run_records_tag(monkeypatch, tmp_path: Path) -> None:
    """--tag で指定したタグが results.jsonl のレコードに残る。"""
    _configure_paths(monkeypatch, tmp_path)
    eval_cli.cmd_run(_run_args(trials=1, tag="rules"))
    records = load_records(tmp_path / "results.jsonl")
    assert records[0]["tag"] == "rules"


def test_cmd_run_different_tags_do_not_collide(monkeypatch, tmp_path: Path) -> None:
    """異なる tag は再開判定で別扱いになり、両方とも実行・記録される。"""
    _configure_paths(monkeypatch, tmp_path)
    eval_cli.cmd_run(_run_args(trials=1, tag="baseline"))
    eval_cli.cmd_run(_run_args(trials=1, tag="rules"))
    records = load_records(tmp_path / "results.jsonl")
    assert {record["tag"] for record in records} == {"baseline", "rules"}
