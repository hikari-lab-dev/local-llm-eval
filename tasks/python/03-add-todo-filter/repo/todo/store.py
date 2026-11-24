"""タスクの永続化と一覧管理。"""

from __future__ import annotations

import json
from pathlib import Path

from todo.model import Task


class TaskStore:
    """タスク一覧をJSONファイルへ永続化するストア。"""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.tasks: list[Task] = []
        if path.exists():
            self.tasks = self._load()

    def _load(self) -> list[Task]:
        """JSONファイルからタスク一覧を読み込む。"""
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [Task.from_dict(item) for item in raw]

    def save(self) -> None:
        """タスク一覧をJSONファイルへ書き出す。"""
        raw = [task.to_dict() for task in self.tasks]
        self.path.write_text(
            json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def add(self, title: str, priority: str) -> Task:
        """タスクを追加して保存する。"""
        task = Task(title=title, priority=priority)
        self.tasks.append(task)
        self.save()
        return task

    def list_all(self) -> list[Task]:
        """全タスクを返す。"""
        return list(self.tasks)
