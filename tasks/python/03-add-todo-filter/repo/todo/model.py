"""タスクのデータモデル。"""

from __future__ import annotations

from dataclasses import dataclass

PRIORITIES = ("high", "medium", "low")


@dataclass(frozen=True)
class Task:
    """1件のTODOタスク。"""

    title: str
    priority: str
    done: bool = False

    def to_dict(self) -> dict:
        """JSONシリアライズ用の辞書に変換する。"""
        return {"title": self.title, "priority": self.priority, "done": self.done}

    @staticmethod
    def from_dict(data: dict) -> Task:
        """辞書からTaskを復元する。"""
        return Task(title=data["title"], priority=data["priority"], done=data["done"])
