"""課題（tasks/配下）の読み込み。"""

from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Task:
    """1課題ぶんの定義。"""

    id: str
    lang: str
    difficulty: str
    verify: str
    grade: str
    timeout: float | None
    dir: Path
    editable: list[str] | None = None
    protected: list[str] | None = None


def load_tasks(tasks_root: Path, patterns: list[str] | None = None) -> list[Task]:
    """tasks_root 配下の task.json を読み込み、Task のリストを返す。

    Args:
        tasks_root: 課題定義の親ディレクトリ（例: `<repo>/tasks`）。
        patterns: `lang/*` 形式の fnmatch パターン。None または空リストなら全件。

    Returns:
        id の昇順でソートされた Task のリスト。
    """
    tasks = [_load_one(path) for path in sorted(tasks_root.glob("*/*/task.json"))]
    if not patterns:
        return tasks
    return [task for task in tasks if _matches_any(task.id, patterns)]


def _matches_any(task_id: str, patterns: list[str]) -> bool:
    """task_id がいずれかの fnmatch パターンに合致するかを判定する。"""
    return any(fnmatch.fnmatch(task_id, pattern) for pattern in patterns)


def _load_one(task_json_path: Path) -> Task:
    """1件の task.json を読み込む。"""
    data = json.loads(task_json_path.read_text(encoding="utf-8"))
    task_dir = task_json_path.parent
    return Task(
        id=data["id"],
        lang=data["lang"],
        difficulty=data["difficulty"],
        verify=data["verify"],
        grade=data["grade"],
        timeout=data.get("timeout"),
        dir=task_dir,
        editable=data.get("editable"),
        protected=data.get("protected"),
    )
