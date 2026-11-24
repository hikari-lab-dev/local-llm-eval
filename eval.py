"""local-llm-eval CLI。

課題（tasks/配下）を使い、ローカルLLMワーカーをモデル別に比較評価する。
評価者のトークンを使わず、隠しテストの exit code で機械採点する。
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from collections.abc import Iterator
from pathlib import Path

from eval_lib.reporting import aggregate, render_markdown
from eval_lib.results import (
    CompletedKey,
    append_result,
    load_completed_keys,
    load_records,
)
from eval_lib.runner import (
    LocalAgentNotConfiguredError,
    RunContext,
    SelfcheckResult,
    Trial,
    run_one,
    selfcheck_task,
)
from eval_lib.tasks import Task, load_tasks

REPO_ROOT = Path(__file__).resolve().parent
TASKS_ROOT = REPO_ROOT / "tasks"
# 結果ファイルは環境変数 EVAL_RESULTS_PATH で差し替えられる（同梱の測定結果を集計し直すときなど）。
# レポートと試行ログは、結果ファイルと同じフォルダに出る。
RESULTS_PATH = Path(
    os.environ.get("EVAL_RESULTS_PATH") or REPO_ROOT / "results" / "results.jsonl"
)
REPORT_PATH = RESULTS_PATH.parent / "report.md"
LOGS_ROOT = RESULTS_PATH.parent / "logs"


def cmd_selfcheck(args: argparse.Namespace) -> int:
    """selfcheck: 各課題が「初期失敗・solution適用後成功」であることを確認する。"""
    tasks = load_tasks(TASKS_ROOT, args.tasks)
    if not tasks:
        print("課題が見つかりませんでした。", file=sys.stderr)
        return 1
    results = [selfcheck_task(task) for task in tasks]
    _print_selfcheck_results(results)
    return 0 if all(result.ok for result in results) else 1


def _print_selfcheck_results(results: list[SelfcheckResult]) -> None:
    """selfcheck の結果を1課題1行で表示する。"""
    for result in results:
        mark = "OK" if result.ok else "NG"
        print(
            f"[{mark}] {result.task_id} "
            f"(initial_fails={result.initial_fails}, solved_passes={result.solved_passes})"
        )


def cmd_run(args: argparse.Namespace) -> int:
    """run: 課題×モデル×試行を直列に実行し、1件ごとに results.jsonl へ追記する。"""
    tasks = load_tasks(TASKS_ROOT, args.tasks)
    models = _parse_models(args.models)
    completed = load_completed_keys(RESULTS_PATH)
    for trial in _iter_trials(tasks, models, args, completed):
        record = _run_and_report(trial, args)
        append_result(RESULTS_PATH, record)
    return 0


def _parse_models(models_arg: str) -> list[str]:
    """カンマ区切りのモデル名文字列をリストへ分解する。"""
    return [model.strip() for model in models_arg.split(",") if model.strip()]


def _iter_trials(
    tasks: list[Task],
    models: list[str],
    args: argparse.Namespace,
    completed: set[CompletedKey],
) -> Iterator[Trial]:
    """未完了の (task, model, trial, tag) を Trial として順に生成する。"""
    for task in tasks:
        for model in models:
            for trial_number in range(1, args.trials + 1):
                if (task.id, model, trial_number, args.tag) in completed:
                    continue
                yield Trial(task=task, model=model, trial=trial_number, tag=args.tag)


def _run_and_report(trial: Trial, args: argparse.Namespace) -> dict:
    """1件を実行し、進捗を表示してレコードを返す。"""
    ctx_kwargs: dict = {
        "out_dir": _trial_out_dir(trial),
        "lint": args.lint,
        "profile": args.profile,
        "timeout": getattr(args, "timeout", None),
    }
    if args.local_agent_script:
        ctx_kwargs["local_agent_script"] = Path(args.local_agent_script)
    ctx = RunContext(**ctx_kwargs)
    record = run_one(trial, ctx)
    print(
        f"{trial.task.id} / {trial.model} / trial{trial.trial} [{trial.tag}]: "
        f"status={record['worker_status']} hidden_pass={record['hidden_pass']} "
        f"lint_pass={record['lint_pass']}"
    )
    return record


def _trial_out_dir(trial: Trial) -> Path:
    """1回の試行のログ出力先ディレクトリを組み立てる。"""
    task_dir_name = trial.task.id.replace("/", "_")
    return LOGS_ROOT / trial.tag / task_dir_name / trial.model / f"trial-{trial.trial}"


def cmd_report(args: argparse.Namespace) -> int:
    """report: results.jsonl を集計し、Markdown レポートを出す。--tag 指定時はその件のみ集計する。"""
    records = load_records(RESULTS_PATH)
    if args.tag:
        records = [
            record for record in records if record.get("tag", "baseline") == args.tag
        ]
    markdown = render_markdown(aggregate(records))
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(markdown, encoding="utf-8")
    print(markdown)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """コマンドラインパーサーを構築する。"""
    parser = argparse.ArgumentParser(prog="eval", description="local-llm-eval CLI")
    subparsers = parser.add_subparsers(dest="subcommand", metavar="SUBCOMMAND")
    subparsers.required = True

    _add_selfcheck_parser(subparsers)
    _add_run_parser(subparsers)

    p_report = subparsers.add_parser("report", help="results.jsonl を集計")
    p_report.add_argument(
        "--tag", default=None, help="指定タグのみ集計する（既定: 全件）"
    )
    p_report.set_defaults(func=cmd_report)

    return parser


def _add_selfcheck_parser(subparsers: argparse._SubParsersAction) -> None:
    """selfcheck サブコマンドの引数を定義する。"""
    p_selfcheck = subparsers.add_parser("selfcheck", help="課題の品質を自己検証")
    p_selfcheck.add_argument(
        "--tasks",
        nargs="*",
        default=None,
        help="課題IDの fnmatch パターン（例: python/*）",
    )
    p_selfcheck.set_defaults(func=cmd_selfcheck)


def _add_run_parser(subparsers: argparse._SubParsersAction) -> None:
    """run サブコマンドの引数を定義する。"""
    p_run = subparsers.add_parser("run", help="課題×モデル×試行を実行")
    p_run.add_argument("--models", required=True, help="カンマ区切りのモデル名")
    p_run.add_argument("--trials", type=int, default=1, help="課題ごとの試行回数")
    p_run.add_argument(
        "--tasks",
        nargs="*",
        default=None,
        help="課題IDの fnmatch パターン（例: python/*）",
    )
    p_run.add_argument(
        "--tag",
        default="baseline",
        help="results.jsonl に記録するタグ（既定: baseline）",
    )
    p_run.add_argument(
        "--lint",
        action="store_true",
        help="local_agent.py --lint を有効にする（既定: オフ）",
    )
    p_run.add_argument(
        "--profile",
        default=None,
        help="local_agent.py --profile に渡す設定プロファイルのディレクトリ",
    )
    p_run.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="1 attempt の上限秒（課題の timeout を上書き。既定: 課題の設定）",
    )
    p_run.add_argument(
        "--local-agent-script",
        default=None,
        help="local_agent.py 互換の実行役のパス（既定: LOCAL_AGENT_SCRIPT 環境変数。"
        "どちらも無ければ run は失敗する）",
    )
    p_run.set_defaults(func=cmd_run)


def main() -> int:
    """メインエントリポイント。"""
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except LocalAgentNotConfiguredError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
