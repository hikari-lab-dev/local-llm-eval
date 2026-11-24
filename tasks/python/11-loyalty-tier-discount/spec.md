# 課題: ロイヤルティティア割引の追加

`cart/` パッケージは、カートの小計（`subtotal`）に対して割引を順番に適用する価格計算パイプラインです。
`cart/pricing.py` の `price_cart(subtotal, discounts)` が `discounts` リストの各要素の
`apply(amount)` を先頭から順に呼び出し、その戻り値を次の割引の入力にします
（`cart/discounts.py` の `Discount` 抽象基底クラスを参照）。

顧客の累計購入額（`lifetime_spend`）に応じたロイヤルティ割引を、この既存パイプラインに
追加してください。

## 仕様

- 新しいクラス `LoyaltyTierDiscount` を実装し、`cart.discounts.Discount` を継承すること。
  - コンストラクタは `lifetime_spend: Decimal` を受け取る。
  - `apply(amount)` は、**そのクラスにティア判定を再実装するのではなく**
    `cart/loyalty.py` の `compute_tier(lifetime_spend)` を呼び出してティア名と割引率(%)を取得し、
    `amount` にその割引率を適用した金額を `cart.money.round_money` で丸めて返す。
  - `compute_tier` は `apply` が呼ばれるたびに呼び出すこと（コンストラクタ内で1回だけ
    計算してキャッシュしない）。`cart/loyalty.py` のしきい値テーブルは将来変更されうるため、
    `LoyaltyTierDiscount` 側で数値をハードコードしてはいけない。
- `LoyaltyTierDiscount` は他の `Discount` 実装（`PercentageDiscount` / `FixedAmountDiscount`）と
  自由に組み合わせて `price_cart` のリストに渡せること（既存の連鎖適用の契約——
  「渡された `amount`（＝そのステップまでの累積結果）に対して割引を適用し、丸めて返す」——
  を守ること）。
- 配置場所は `cart/loyalty_discount.py`（新規ファイル）とする。

## 制約

- `tests/test_pricing.py` は既存のテストです。実装がこれを壊さないようにしてください。
- 標準ライブラリのみ使用可能。`Decimal` 以外の型（`float` 等）で金額計算をしないこと。
