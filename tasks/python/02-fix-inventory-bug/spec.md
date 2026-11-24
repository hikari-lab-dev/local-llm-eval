# 課題: 在庫・価格計算モジュールのバグ修正

`inventory/store.py` と `inventory/pricing.py` にまたがるバグを修正してください。

## 仕様

- `Store.remove_stock(item, quantity)` は在庫が不足している場合 `ValueError` を送出し、在庫を変更しない。
- `calculate_total(store, item, unit_price, quantity)` は指定数量ぶん在庫を減らし、割引後の合計金額を返す。
  - 在庫が不足している場合は `ValueError` が伝播し、在庫は変更されない。
  - 数量が10個**以上**（10個を含む）の場合、合計金額から10%割引する。

## 制約

- `tests/test_inventory.py` は既存のテストです。実装がこれを壊さないようにしてください。
- 標準ライブラリのみ使用可能。
