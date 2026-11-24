# 課題: 注文集計処理のリファクタリング

`orders.ts` の `summarizeOrders` 関数は動作していますが、集計・平均計算・最大値抽出の
複数の責務が1つのループに混在しており読みにくくなっています。
**外部から見た振る舞いを変えずに**、読みやすく整理してください。

## 要求

- 関数シグネチャ `summarizeOrders(orders: OrderRecord[]): OrderSummary` は変更しないこと。
- `OrderRecord` / `OrderSummary` の型定義は変更しないこと。
- 責務ごとに小さな関数へ分割すること（`summarizeOrders` 自身を含め、ファイル内に4つ以上の関数があること）。
- `else`（`else if` を含む）を一切使わないこと（early return や条件式で書き換える）。
- 既存の挙動を保つこと。
  - `amount` が `null` または0以下のレコードは集計から除外する。
  - `category` が無い（`undefined`）レコードは `"unknown"` として扱う。
  - `topItem` / `topAmount` は最も金額の大きい1件（集計対象のレコードのみが対象）。
  - 対象レコードが1件も無い場合、`topItem` は `null`、`topAmount` は `0`、
    `byCategory` / `averageByCategory` は空オブジェクト。

## 制約

- `tests/orders.test.ts` は既存のテストです。実装がこれを壊さないようにしてください。
- 標準ライブラリのみ使用可能。
