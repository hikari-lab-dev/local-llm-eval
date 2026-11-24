# 課題: 団体割引ルールの追加

`pricing/` は、注文金額（`subtotal`）に割引ルールを順番に適用する価格計算パイプラインです。
`pricing/pipeline.ts` の `priceOrder(subtotal, rules)` が `rules` 配列の各要素の
`apply(amount)` を先頭から順に呼び出し、その戻り値を次のルールの入力にします
（`pricing/rule.ts` の `PriceRule` インターフェースを参照）。

参加人数（`groupSize`）に応じた団体割引を、この既存パイプラインに追加してください。

## 仕様

- 新しいクラス `GroupSizeDiscountRule` を実装し、`pricing.rule.PriceRule` を実装すること。
  - コンストラクタは `groupSize: number` を受け取る。
  - `apply(amount)` は、**割引率をこのクラスに再実装するのではなく**
    `pricing/groupTiers.ts` の `computeGroupRate(groupSize)` を呼び出して割引率(%)を取得し、
    `amount` にその割引率を適用した金額を `pricing/roundYen.ts` の `roundYen` で丸めて返す。
  - `computeGroupRate` は `apply` が呼ばれるたびに呼び出すこと（コンストラクタ内で1回だけ
    計算してキャッシュしない）。`pricing/groupTiers.ts` のしきい値テーブルは将来変更されうるため、
    `GroupSizeDiscountRule` 側で数値をハードコードしてはいけない。
- `GroupSizeDiscountRule` は他のルール（`PercentOffRule` / `FlatOffRule`）と自由に組み合わせて
  `priceOrder` のルール配列に渡せること（既存の連鎖適用の契約——「渡された `amount`
  （＝そのステップまでの累積結果）に割引を適用し、丸めて返す」——を守ること）。
- 配置場所は `pricing/groupSizeDiscountRule.ts`（新規ファイル）とする。

## 制約

- `tests/pipeline.test.ts` は既存のテストです。実装がこれを壊さないようにしてください。
- コンストラクタのパラメータプロパティ（`constructor(private x: T)`）は使わないこと
  （フィールドを別途宣言し、コンストラクタ内で代入すること）。
- 外部ライブラリは使用しないこと。
