"""results.jsonl の読み書き（追記・再開判定・集計用の読み込み）。"""

from __future__ import annotations

import json
from pathlib import Path

CompletedKey = tuple[str, str, int, str]


def load_completed_keys(results_path: Path) -> set[CompletedKey]:
    """完了済みの (task, model, trial) の組を返す。ファイルが無ければ空集合。"""
    if not results_path.exists():
        return set()
    return {_record_key(record) for record in load_records(results_path)}


def load_records(results_path: Path) -> list[dict]:
    """results.jsonl の全レコードを読み込む。ファイルが無ければ空リスト。"""
    if not results_path.exists():
        return []
    lines = results_path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def append_result(results_path: Path, record: dict) -> None:
    """1件のレコードを results.jsonl に追記する。"""
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with results_path.open("a", encoding="utf-8") as results_file:
        results_file.write(json.dumps(record, ensure_ascii=False))
        results_file.write("\n")


def _record_key(record: dict) -> CompletedKey:
    """レコードから再開判定用のキーを取り出す。

    tag が無い旧形式のレコード（評価ジョブが現在も追記している results.jsonl）は
    baseline として扱う後方互換を保つ。
    """
    return (
        record["task"],
        record["model"],
        record["trial"],
        record.get("tag", "baseline"),
    )
