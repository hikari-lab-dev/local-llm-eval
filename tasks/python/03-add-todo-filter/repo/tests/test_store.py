from pathlib import Path

from todo.store import TaskStore


def test_add_and_list_all(tmp_path: Path) -> None:
    store = TaskStore(tmp_path / "todo.json")
    store.add("牛乳を買う", "medium")
    store.add("報告書を書く", "high")
    titles = [task.title for task in store.list_all()]
    assert titles == ["牛乳を買う", "報告書を書く"]


def test_persists_across_instances(tmp_path: Path) -> None:
    db_path = tmp_path / "todo.json"
    TaskStore(db_path).add("散歩", "low")
    reloaded = TaskStore(db_path)
    assert [task.title for task in reloaded.list_all()] == ["散歩"]
