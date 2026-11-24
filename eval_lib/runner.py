"""local_agent.py 互換の実行役への委譲実行と、grade / selfcheck の実行。"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from eval_lib.claude_cli import is_claude_model
from eval_lib.claude_worker import run_claude_agent
from eval_lib.tasks import Task

# 実行役（local_agent.py 互換の CLI）のパス。このリポジトリには同梱していない。
# 環境変数 LOCAL_AGENT_SCRIPT か `eval.py run --local-agent-script` で指定する（契約は README を参照）。
LOCAL_AGENT_SCRIPT: Path | None = (
    Path(os.environ["LOCAL_AGENT_SCRIPT"])
    if os.environ.get("LOCAL_AGENT_SCRIPT")
    else None
)
# 採点用の lint を実行するスクリプト（`--repo <dir> <files...>` を受け取り、
# 0=合格 / 2=検証不能 / それ以外=不合格 を返す）。未設定なら lint_pass は None になる。
LINT_SCRIPT: Path | None = (
    Path(os.environ["LINT_SCRIPT"]) if os.environ.get("LINT_SCRIPT") else None
)
# TS 課題の lint（biome）用。課題の repo/ には node_modules を置かないため、
# 導入先を環境変数 CLAUDE_BIOME で指す（未設定なら下の既定の場所を見る）。
BIOME_BIN = Path(
    os.environ.get("CLAUDE_BIOME")
    or Path.home() / ".local/share/local-llm-eval-tools/node_modules/.bin/biome"
)
DEFAULT_GRADE_TIMEOUT_SECONDS = 300.0
_DIFF_STAT_SUMMARY_RE = re.compile(
    r"(\d+) files? changed(?:, (\d+) insertions?\(\+\))?(?:, (\d+) deletions?\(-\))?"
)


@dataclass(frozen=True)
class Trial:
    """1回の試行の識別子（課題・モデル・試行番号・タグ）。"""

    task: Task
    model: str
    trial: int
    tag: str = "baseline"


@dataclass(frozen=True)
class RunContext:
    """実行環境の設定（出力先・opencode を起動する Python コマンド・lint/profile 有無）。"""

    out_dir: Path
    python_cmd: str = "python3"
    lint: bool = False
    profile: str | None = None
    # 1 試行（attempt）の上限秒。課題の timeout を上書きする
    timeout: float | None = None
    local_agent_script: Path | None = field(default_factory=lambda: LOCAL_AGENT_SCRIPT)


@dataclass(frozen=True)
class SelfcheckResult:
    """1課題ぶんの selfcheck 結果。"""

    task_id: str
    initial_fails: bool
    solved_passes: bool

    @property
    def ok(self) -> bool:
        """初期状態では隠しテストが失敗し、solution 適用後は成功したか。"""
        return self.initial_fails and self.solved_passes


def run_grade(
    workdir: Path, grade_cmd: str, timeout: float = DEFAULT_GRADE_TIMEOUT_SECONDS
) -> int:
    """workdir で grade コマンドを実行し、exit code を返す。"""
    try:
        result = subprocess.run(
            grade_cmd,
            shell=True,
            cwd=workdir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return result.returncode
    except subprocess.TimeoutExpired:
        return 124


def selfcheck_task(task: Task) -> SelfcheckResult:
    """課題1件の selfcheck（初期失敗・solution適用後成功）を確認する。"""
    with tempfile.TemporaryDirectory(prefix="llm-eval-selfcheck-") as tmp:
        workdir = Path(tmp)
        _copy_tree(task.dir / "repo", workdir)
        _copy_tree(task.dir / "hidden_tests", workdir / "hidden_tests")
        initial_exit = run_grade(workdir, task.grade)
        _copy_tree(task.dir / "solution", workdir)
        solved_exit = run_grade(workdir, task.grade)
    return SelfcheckResult(
        task_id=task.id,
        initial_fails=initial_exit != 0,
        solved_passes=solved_exit == 0,
    )


def run_one(trial: Trial, ctx: RunContext) -> dict:
    """1回の試行を local_agent.py に委譲し、results.jsonl 用のレコードを作る。"""
    with tempfile.TemporaryDirectory(prefix="llm-eval-repo-") as tmp:
        repo_path = Path(tmp) / "repo"
        _copy_tree(trial.task.dir / "repo", repo_path)
        _init_git_repo(repo_path)
        summary = _run_local_agent(trial, repo_path, ctx)
        hidden_pass, lint_pass = _grade_and_cleanup(trial, summary, ctx)
    return _build_record(trial, summary, hidden_pass, lint_pass)


def _child_env() -> dict[str, str]:
    """子プロセス（local_agent → opencode → lint プラグイン、採点側 lint）へ渡す環境変数。"""
    env = os.environ.copy()
    if BIOME_BIN.exists():
        env["CLAUDE_BIOME"] = str(BIOME_BIN)
    return env


def _grade_and_cleanup(
    trial: Trial, summary: dict, ctx: RunContext
) -> tuple[bool, bool | None]:
    """採点（lint_pass は worker の --lint 有無に関係なく独立して求める）と cleanup。

    採点中に例外が起きても cleanup は必ず実行する。一時リポジトリ（repo_path）が
    削除される前に worktree 側の git worktree remove を終わらせておかないと、
    元リポジトリを失った worktree が実行役の作業場所に残留するため。
    """
    try:
        lint_pass = compute_lint_pass(summary)
        hidden_pass = _grade_summary(trial.task, summary)
        return hidden_pass, lint_pass
    finally:
        _cleanup_job(summary, ctx)


def _copy_tree(src: Path, dst: Path) -> None:
    """src の中身を dst へ再帰的にコピーする（既存ファイルは上書き）。"""
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)


def _init_git_repo(path: Path) -> None:
    """path を git リポジトリとして初期化し、1コミットを作る。"""
    _run_git(path, "init", "-q")
    _run_git(path, "config", "user.email", "eval@local")
    _run_git(path, "config", "user.name", "local-llm-eval")
    _run_git(path, "add", "-A")
    _run_git(path, "commit", "-q", "-m", "initial")


def _run_git(path: Path, *args: str) -> None:
    """path 上で git コマンドを実行する（失敗時は例外を送出する）。"""
    subprocess.run(
        ["git", "-C", str(path), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )


class LocalAgentNotConfiguredError(RuntimeError):
    """実行役（local_agent.py 互換の CLI）が指定されていない。"""


def require_local_agent(ctx: RunContext) -> Path:
    """実行役のパスを返す。未指定ならどう指定するかを添えて失敗する。"""
    if ctx.local_agent_script is None:
        raise LocalAgentNotConfiguredError(
            "実行役（local_agent.py 互換の CLI）が未指定です。環境変数 LOCAL_AGENT_SCRIPT か "
            "--local-agent-script で指定してください（契約は README を参照）"
        )
    return ctx.local_agent_script


def _build_local_agent_command(
    trial: Trial, repo_path: Path, ctx: RunContext
) -> list[str]:
    """local_agent.py run に渡すコマンドライン引数を組み立てる。"""
    command = [
        ctx.python_cmd,
        str(require_local_agent(ctx)),
        "run",
        "--repo",
        str(repo_path),
        "--spec",
        str(trial.task.dir / "spec.md"),
        "--verify",
        trial.task.verify,
        "--agent",
        "worker",
        "--model",
        trial.model,
        "--out",
        str(ctx.out_dir),
    ]
    timeout = ctx.timeout if ctx.timeout is not None else trial.task.timeout
    if timeout is not None:
        command.extend(["--timeout", str(timeout)])
    if ctx.lint:
        command.append("--lint")
    if ctx.profile:
        command.extend(["--profile", ctx.profile])
    for pattern in trial.task.editable or []:
        command.extend(["--editable", pattern])
    for pattern in trial.task.protected or []:
        command.extend(["--protected", pattern])
    return command


def _run_local_agent(trial: Trial, repo_path: Path, ctx: RunContext) -> dict:
    """local_agent.py run を呼び出し、summary.json をパースして返す。claude- モデルは Claude CLI 経路。"""
    if is_claude_model(trial.model):
        return run_claude_agent(trial, repo_path, ctx)
    command = _build_local_agent_command(trial, repo_path, ctx)
    subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_child_env(),
        check=False,
    )
    return json.loads((ctx.out_dir / "summary.json").read_text(encoding="utf-8"))


def _grade_summary(task: Task, summary: dict) -> bool:
    """summary の worktree に hidden_tests をコピーし、grade を実行して合否を返す。"""
    worktree = summary.get("worktree")
    if worktree is None:
        return False
    workdir = Path(worktree)
    _copy_tree(task.dir / "hidden_tests", workdir / "hidden_tests")
    return run_grade(workdir, task.grade) == 0


def _cleanup_job(summary: dict, ctx: RunContext) -> None:
    """local_agent.py cleanup でジョブの worktree とブランチを削除する。"""
    branch = summary.get("branch")
    if branch is None:
        return
    job_id = branch.removeprefix("local/")
    subprocess.run(
        [ctx.python_cmd, str(require_local_agent(ctx)), "cleanup", job_id],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _tracked_changed_files(workdir: Path, base_commit: str) -> list[str]:
    """base_commit との追跡ファイル差分から、削除を除いたパス一覧を返す。"""
    result = subprocess.run(
        ["git", "-C", str(workdir), "diff", "--name-status", base_commit],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    files = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status, path = parts[0], parts[-1]
        if status.startswith("D"):
            continue
        files.append(path)
    return files


def _untracked_files(workdir: Path) -> list[str]:
    """未追跡ファイル（ディレクトリではなく個々のファイル）のパス一覧を返す。"""
    result = subprocess.run(
        [
            "git",
            "-C",
            str(workdir),
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return [line[3:] for line in result.stdout.splitlines() if line.startswith("??")]


def _changed_files_since(workdir: Path, base_commit: str) -> list[str]:
    """base_commit からの変更ファイル（追跡＋未追跡、削除は除く）を返す。"""
    tracked = _tracked_changed_files(workdir, base_commit)
    untracked = _untracked_files(workdir)
    return sorted(set(tracked) | set(untracked))


def compute_lint_pass(summary: dict) -> bool | None:
    """summary の worktree に対し、base_commit からの変更ファイルへ lint-changed.sh をかける。

    worker の --lint 有無に関係なく採点用に独立して求める。exit 2（検証不能）は None。
    hidden_tests をコピーする前に呼ぶこと（採点用の付随ファイルを lint 対象に混ぜないため）。
    """
    worktree = summary.get("worktree")
    base_commit = summary.get("base_commit")
    if worktree is None or base_commit is None:
        return None
    workdir = Path(worktree)
    files = _changed_files_since(workdir, base_commit)
    if not files:
        return True
    if LINT_SCRIPT is None or not LINT_SCRIPT.exists():
        return None
    result = subprocess.run(
        ["bash", str(LINT_SCRIPT), "--repo", str(workdir), *files],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_child_env(),
        check=False,
    )
    if result.returncode == 2:
        return None
    return result.returncode == 0


def _build_record(
    trial: Trial, summary: dict, hidden_pass: bool, lint_pass: bool | None
) -> dict:
    """1回の試行結果を results.jsonl 用のレコードに変換する。"""
    attempts = summary.get("attempts", [])
    cost = {"cost_usd": summary["cost_usd"]} if "cost_usd" in summary else {}
    return {
        "task": trial.task.id,
        "lang": trial.task.lang,
        "model": trial.model,
        "trial": trial.trial,
        "tag": trial.tag,
        "worker_status": summary["status"],
        "hidden_pass": hidden_pass,
        "lint_pass": lint_pass,
        "total_seconds": summary.get("total_seconds", 0.0),
        **_attempt_counts(attempts),
        "diff_lines": _count_diff_lines(summary.get("diff_stat")),
        **_usage_fields(summary),
        **cost,
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
    }


def _attempt_counts(attempts: list[dict]) -> dict:
    """全 attempt の step / ツール呼び出し系カウンタを合計する。"""
    keys = ("step_count", "tool_call_count", "tool_error_count", "tool_call_leak_count")
    return {key: sum(attempt.get(key, 0) for attempt in attempts) for key in keys}


def _usage_fields(summary: dict) -> dict:
    """summary のトークン使用量とループ兆候を記録用に取り出す。

    古い summary には無いキーがあるため、欠落は None（平均から除外する印）にする。
    """
    tokens = summary.get("tokens") or {}
    return {
        "input_tokens": tokens.get("input"),
        "output_tokens": tokens.get("output"),
        "reasoning_tokens": tokens.get("reasoning"),
        "length_stop_count": summary.get("length_stop_count"),
        "max_repeat_tool_streak": summary.get("max_repeat_tool_streak"),
    }


def _count_diff_lines(diff_stat_text: str | None) -> int:
    """`git diff --stat` の出力から追加+削除の行数を合計する。"""
    if not diff_stat_text:
        return 0
    match = _DIFF_STAT_SUMMARY_RE.search(diff_stat_text)
    if match is None:
        return 0
    insertions = int(match.group(2) or 0)
    deletions = int(match.group(3) or 0)
    return insertions + deletions
