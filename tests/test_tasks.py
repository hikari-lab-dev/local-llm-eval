import json
from pathlib import Path

from eval_lib.tasks import load_tasks

TASKS_ROOT = Path(__file__).resolve().parent.parent / "tasks"


def _write_task_json(task_dir: Path, **overrides: object) -> None:
    """最小限の task.json を作る。overrides で editable/protected 等を追加できる。"""
    task_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "id": "python/01-sample",
        "lang": "python",
        "difficulty": "easy",
        "verify": "true",
        "grade": "true",
        **overrides,
    }
    (task_dir / "task.json").write_text(json.dumps(data), encoding="utf-8")


def test_load_tasks_finds_all_python_task_directories() -> None:
    tasks = load_tasks(TASKS_ROOT)
    python_tasks = [task for task in tasks if task.lang == "python"]
    expected = sum(
        1
        for path in (TASKS_ROOT / "python").iterdir()
        if (path / "task.json").is_file()
    )
    assert len(python_tasks) == expected


def test_load_tasks_each_has_verify_and_grade() -> None:
    tasks = load_tasks(TASKS_ROOT)
    assert all(task.verify and task.grade for task in tasks)


def test_load_tasks_filters_by_pattern() -> None:
    tasks = load_tasks(TASKS_ROOT, ["python/01-*"])
    assert [task.id for task in tasks] == ["python/01-interval-merge"]


def test_load_tasks_dir_points_to_task_directory() -> None:
    tasks = load_tasks(TASKS_ROOT, ["python/01-*"])
    assert (tasks[0].dir / "spec.md").exists()


def test_load_tasks_reads_editable(tmp_path: Path) -> None:
    """task.json の editable（glob 配列）を読み込む。"""
    _write_task_json(
        tmp_path / "python" / "01-sample",
        editable=["a.py"],
        protected=["tests/test_a.py"],
    )

    tasks = load_tasks(tmp_path)

    assert tasks[0].editable == ["a.py"]


def test_load_tasks_reads_protected(tmp_path: Path) -> None:
    """task.json の protected（glob 配列）を読み込む。"""
    _write_task_json(
        tmp_path / "python" / "01-sample",
        editable=["a.py"],
        protected=["tests/test_a.py"],
    )

    tasks = load_tasks(tmp_path)

    assert tasks[0].protected == ["tests/test_a.py"]


def test_load_tasks_editable_defaults_to_none(tmp_path: Path) -> None:
    """editable が無い task.json では None のままにする。"""
    _write_task_json(tmp_path / "python" / "01-sample")

    tasks = load_tasks(tmp_path)

    assert tasks[0].editable is None


def test_load_tasks_protected_defaults_to_none(tmp_path: Path) -> None:
    """protected が無い task.json では None のままにする。"""
    _write_task_json(tmp_path / "python" / "01-sample")

    tasks = load_tasks(tmp_path)

    assert tasks[0].protected is None
