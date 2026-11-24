from dataclasses import replace
from pathlib import Path

from todo.cli import run
from todo.store import TaskStore


def test_filter_by_priority(tmp_path: Path) -> None:
    store = TaskStore(tmp_path / "todo.json")
    store.add("A", "low")
    store.add("B", "high")
    store.add("C", "high")
    result = [task.title for task in store.filter_by(priority="high")]
    assert result == ["B", "C"]


def test_filter_by_done(tmp_path: Path) -> None:
    store = TaskStore(tmp_path / "todo.json")
    store.add("A", "medium")
    store.tasks[0] = replace(store.tasks[0], done=True)
    store.save()
    result = [task.title for task in store.filter_by(done=True)]
    assert result == ["A"]


def test_filter_by_no_args_sorted_by_priority(tmp_path: Path) -> None:
    store = TaskStore(tmp_path / "todo.json")
    store.add("low-task", "low")
    store.add("high-task", "high")
    store.add("medium-task", "medium")
    result = [task.title for task in store.filter_by()]
    assert result == ["high-task", "medium-task", "low-task"]


def test_cli_list_with_priority_filter(tmp_path: Path) -> None:
    db_path = tmp_path / "todo.json"
    run(["add", "A", "--priority", "low"], db_path)
    run(["add", "B", "--priority", "high"], db_path)
    output = run(["list", "--priority", "high"], db_path)
    assert output == ["[ ] B (high)"]


def test_cli_list_with_done_filter(tmp_path: Path) -> None:
    db_path = tmp_path / "todo.json"
    run(["add", "A", "--priority", "medium"], db_path)
    store = TaskStore(db_path)
    store.tasks[0] = replace(store.tasks[0], done=True)
    store.save()
    output = run(["list", "--done"], db_path)
    assert output == ["[x] A (medium)"]
