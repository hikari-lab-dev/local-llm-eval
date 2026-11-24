# 課題: TODO CLI へのフィルタ・ソート機能追加

既存の TODO 管理ライブラリ（`todo/model.py`, `todo/store.py`, `todo/cli.py`）に、
以下の機能を追加してください。

## 追加する機能

1. `TaskStore.filter_by(done: bool | None = None, priority: str | None = None) -> list[Task]`
   - `done` / `priority` を指定した場合はそれぞれの条件でタスクを絞り込む。
   - どちらも `None`（未指定）の場合は `list_all()` と同じ全件を返す。
   - 戻り値は優先度順（`high` > `medium` > `low`）でソートする。同じ優先度内では追加順を保つ。

2. CLI の `list` サブコマンドに以下のオプションを追加する。
   - `--priority {high,medium,low}`: 指定した優先度のタスクのみ表示する。
   - `--done`: 完了済みタスクのみ表示する（指定なしなら全件、指定ありなら完了済みのみ）。
   - 出力は `TaskStore.filter_by` の結果を使い、優先度順で表示する。

## 制約

- `tests/test_store.py` は既存のテストです。実装がこれを壊さないようにしてください。
- `Task` を完了済みにする新規APIの追加は不要です（既存の `done` フィールドのみ利用）。
- 標準ライブラリのみ使用可能。
