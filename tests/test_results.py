from pathlib import Path

from eval_lib.results import append_result, load_completed_keys, load_records


def _make_record(task: str, model: str, trial: int) -> dict:
    """テスト用の最小限のレコードを作る。"""
    return {
        "task": task,
        "lang": "python",
        "model": model,
        "trial": trial,
        "worker_status": "success",
        "hidden_pass": True,
        "total_seconds": 12.3,
    }


def test_load_completed_keys_missing_file_returns_empty(tmp_path: Path) -> None:
    results_path = tmp_path / "results.jsonl"
    assert load_completed_keys(results_path) == set()


def test_append_result_creates_parent_dir(tmp_path: Path) -> None:
    results_path = tmp_path / "nested" / "results.jsonl"
    append_result(results_path, _make_record("python/01", "m1", 1))
    assert results_path.exists()


def test_append_and_load_records_roundtrip(tmp_path: Path) -> None:
    results_path = tmp_path / "results.jsonl"
    append_result(results_path, _make_record("python/01", "m1", 1))
    append_result(results_path, _make_record("python/02", "m1", 1))
    records = load_records(results_path)
    assert len(records) == 2


def test_load_completed_keys_reflects_appended_records(tmp_path: Path) -> None:
    results_path = tmp_path / "results.jsonl"
    append_result(results_path, _make_record("python/01", "m1", 1))
    completed = load_completed_keys(results_path)
    assert completed == {("python/01", "m1", 1, "baseline")}


def test_load_completed_keys_distinguishes_tags(tmp_path: Path) -> None:
    """異なる tag は別キーとして扱われ、再開判定で衝突しない。"""
    results_path = tmp_path / "results.jsonl"
    record = _make_record("python/01", "m1", 1)
    record["tag"] = "rules"
    append_result(results_path, record)
    completed = load_completed_keys(results_path)
    assert completed == {("python/01", "m1", 1, "rules")}


def test_load_completed_keys_reads_legacy_records_without_tag(tmp_path: Path) -> None:
    """tag フィールドの無い旧形式レコードは baseline として読む。"""
    results_path = tmp_path / "results.jsonl"
    append_result(results_path, _make_record("python/01", "m1", 1))
    completed = load_completed_keys(results_path)
    assert ("python/01", "m1", 1, "baseline") in completed
