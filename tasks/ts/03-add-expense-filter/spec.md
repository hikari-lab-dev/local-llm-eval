# 課題: 経費記録への絞り込み・整形機能追加

既存の経費記録ライブラリ（`expense/model.ts`, `expense/store.ts`, `expense/format.ts`）に、
以下の機能を追加してください。

## 追加する機能

1. `ExpenseStore` に次のメソッドを追加する。

   ```ts
   filterBy(options?: { paid?: boolean; category?: Category }): Expense[]
   ```

   - `options` 省略時、または `paid` / `category` の両方が未指定の場合は、登録済みの全件が対象。
   - `paid` を指定した場合は `paid` の値が一致するものだけに絞り込む。
   - `category` を指定した場合はその `category` と一致するものだけに絞り込む。
   - 両方指定した場合はAND条件（両方を満たすもの）で絞り込む。
   - 戻り値は常に **金額（`amount`）の降順** でソートする。同額の場合は登録順を保つ（安定ソート）。

2. `format.ts` に次の関数を追加する。

   ```ts
   formatFilteredExpenses(store: ExpenseStore, options?: { paid?: boolean; category?: Category }): string[]
   ```

   - `store.filterBy(options)` の結果（絞り込み・ソート済み）を、既存の `formatExpenses` と同じ整形ルールで
     文字列の配列に変換して返す。

## 制約

- `expense/model.ts` の型定義（`Category`, `Expense`）は変更しないこと。
- `tests/store.test.ts` は既存のテストです。実装がこれを壊さないようにしてください。
- 標準ライブラリのみ使用可能。
