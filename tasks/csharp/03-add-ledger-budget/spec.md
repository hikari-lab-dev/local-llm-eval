# 課題: 家計簿ライブラリへの予算管理機能追加

既存の家計簿ライブラリ（`Ledger/Transaction.cs`, `Ledger/LedgerBook.cs`）に、
カテゴリ別の予算管理機能を追加してください。

## 追加する機能（`LedgerBook`）

1. `void SetBudget(string category, decimal limit)`
   - 指定したカテゴリの予算上限を設定する。同じカテゴリに再設定した場合は上書きする。

2. `decimal GetRemainingBudget(string category)`
   - 設定した予算上限から、そのカテゴリの支出合計（`GetTotalByCategory` と同じ集計）を引いた残額を返す。
   - 予算が設定されていないカテゴリを指定した場合は `InvalidOperationException` を送出する。

3. `bool IsOverBudget(string category)`
   - `GetRemainingBudget(category)` が負の値の場合に `true` を返す。ちょうど0（予算ぴったり）は `false`。
   - 予算が設定されていないカテゴリを指定した場合は `GetRemainingBudget` と同様に例外を送出する。

## 制約

- `tests/LedgerBookTests.cs` は既存のテストです。実装がこれを壊さないようにしてください。
- 既存の public メンバー（`AddTransaction`, `GetTotalByCategory`, `GetAllTransactions`）のシグネチャは変更しないこと。
- 外部 NuGet パッケージの追加は不要です。
