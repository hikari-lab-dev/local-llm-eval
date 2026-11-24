"""TODO管理CLI。"""

from __future__ import annotations

import argparse
from pathlib import Path

from todo.store import TaskStore

DEFAULT_DB_PATH = Path("todo.json")


def build_parser() -> argparse.ArgumentParser:
    """コマンドラインパーサーを構築する。"""
    parser = argparse.ArgumentParser(prog="todo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="タスクを追加")
    add_parser.add_argument("title")
    add_parser.add_argument(
        "--priority", default="medium", choices=["high", "medium", "low"]
    )

    subparsers.add_parser("list", help="タスク一覧を表示")

    return parser


def run(argv: list[str], db_path: Path = DEFAULT_DB_PATH) -> list[str]:
    """CLI引数を処理し、出力行のリストを返す。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    store = TaskStore(db_path)
    if args.command == "add":
        task = store.add(args.title, args.priority)
        return [f"追加しました: {task.title} ({task.priority})"]
    tasks = store.list_all()
    return [
        f"[{'x' if task.done else ' '}] {task.title} ({task.priority})"
        for task in tasks
    ]
