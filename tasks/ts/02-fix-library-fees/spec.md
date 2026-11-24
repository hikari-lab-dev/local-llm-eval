# 課題: 図書館蔵書・延滞料金モジュールのバグ修正

`library/catalog.ts` と `library/lending.ts` にまたがるバグを修正してください。

## 仕様

- `Catalog.checkOut(isbn)` は在庫（利用可能な冊数）が0の場合 `Error` を送出し、在庫を変更しない。
  在庫が1以上ある場合のみ1冊減らす。
- `calculateLateFee(daysBorrowed)` は延滞料金を次のルールで計算する。
  - 借用日数がグレース期間（`GRACE_DAYS` = 7日）以内なら延滞料金は0円。
  - 7日を超えた日数 × `LATE_FEE_PER_DAY`（20円）が基本延滞料金。
  - 借用日数が `LONG_OVERDUE_DAYS`（14日）**以上**（14日を含む）の場合、基本延滞料金を2倍にする。
- `borrowBook(catalog, isbn)` は `catalog.checkOut(isbn)` を呼び出すだけの薄いラッパーで、
  在庫不足時のエラーはそのまま呼び出し元に伝播する。

## 制約

- `tests/catalog.test.ts` と `tests/lending.test.ts` は既存のテストです。実装がこれを壊さないようにしてください。
- 標準ライブラリのみ使用可能。
