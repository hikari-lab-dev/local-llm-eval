"""タスクの永続化と一覧管理。"""

from __future__ import annotations

import json
from pathlib import Path

from todo.model import PRIORITIES, Task

_PRIORITY_ORDER = {priority: index for index, priority in enumerate(PRIORITIES)}


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

    def filter_by(
        self, done: bool | None = None, priority: str | None = None
    ) -> list[Task]:
        """条件でタスクを絞り込み、優先度順でソートして返す。"""
        matched = [task for task in self.tasks if self._matches(task, done, priority)]
        return sorted(matched, key=lambda task: _PRIORITY_ORDER[task.priority])

    @staticmethod
    def _matches(task: Task, done: bool | None, priority: str | None) -> bool:
        """1件のタスクが絞り込み条件に合致するかを判定する。"""
        done_mismatch = done is not None and task.done != done
        priority_mismatch = priority is not None and task.priority != priority
        return not (done_mismatch or priority_mismatch)
