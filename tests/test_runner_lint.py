"""eval_lib.runner の compute_lint_pass のテスト。

実 git リポジトリ＋偽の lint スクリプトを使い、exit code の扱い
（0=合格 / 1=不合格 / 2=検証不能=None）と、worktree/base_commit 欠落時の
挙動を確認する。
"""

import subprocess
from pathlib import Path

import pytest

from eval_lib import runner


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _init_repo(repo: Path) -> str:
    """1ファイルをコミットした最小リポジトリを作り、base_commit のハッシュを返す。"""
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "test")
    (repo / "a.py").write_text("x = 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    return subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()


def _write_fake_lint_script(path: Path, exit_code: int, message: str) -> None:
    """指定した exit code を返す偽の lint-changed.sh を作る。"""
    path.write_text(
        f"#!/usr/bin/env bash\necho '{message}'\nexit {exit_code}\n", encoding="utf-8"
    )
    path.chmod(0o755)


def test_compute_lint_pass_returns_true_on_exit_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    base_commit = _init_repo(repo)
    (repo / "a.py").write_text("x = 2\n", encoding="utf-8")
    fake_script = tmp_path / "fake-lint.sh"
    _write_fake_lint_script(fake_script, 0, "ok")
    monkeypatch.setattr(runner, "LINT_SCRIPT", fake_script)

    result = runner.compute_lint_pass(
        {"worktree": str(repo), "base_commit": base_commit}
    )

    assert result is True


def test_compute_lint_pass_returns_false_on_exit_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    base_commit = _init_repo(repo)
    (repo / "a.py").write_text("x = 2\n", encoding="utf-8")
    fake_script = tmp_path / "fake-lint.sh"
    _write_fake_lint_script(fake_script, 1, "violation")
    monkeypatch.setattr(runner, "LINT_SCRIPT", fake_script)

    result = runner.compute_lint_pass(
        {"worktree": str(repo), "base_commit": base_commit}
    )

    assert result is False


def test_compute_lint_pass_returns_none_on_exit_two(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    base_commit = _init_repo(repo)
    (repo / "a.py").write_text("x = 2\n", encoding="utf-8")
    fake_script = tmp_path / "fake-lint.sh"
    _write_fake_lint_script(fake_script, 2, "unverifiable")
    monkeypatch.setattr(runner, "LINT_SCRIPT", fake_script)

    result = runner.compute_lint_pass(
        {"worktree": str(repo), "base_commit": base_commit}
    )

    assert result is None


def test_compute_lint_pass_returns_none_when_worktree_missing() -> None:
    assert runner.compute_lint_pass({"base_commit": "abc"}) is None


def test_compute_lint_pass_skips_script_when_no_changed_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """base_commit から変更が無ければ、lint スクリプトを起動せず合格扱いにする。"""
    repo = tmp_path / "repo"
    base_commit = _init_repo(repo)

    real_run = subprocess.run

    def _fail_if_lint_script(command, *args, **kwargs):
        if command[0] == "bash":
            raise AssertionError("lint スクリプトは呼ばれないはず")
        return real_run(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", _fail_if_lint_script)

    result = runner.compute_lint_pass(
        {"worktree": str(repo), "base_commit": base_commit}
    )

    assert result is True
