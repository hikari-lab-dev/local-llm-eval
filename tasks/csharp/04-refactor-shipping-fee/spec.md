# 課題: 配送料金計算のリファクタリング

`ShippingFee/ShippingCalculator.cs` の `ShippingCalculator.CalculateFee` メソッドは動作していますが、
地域ごとの基本料金判定・重量による割増計算・速達倍率の適用が1つの深くネストしたメソッドに
混在しており読みにくくなっています。**外部から見た振る舞いを変えずに**、読みやすく整理してください。

## 要求

- 公開メソッドのシグネチャ `CalculateFee(decimal weightKg, string region, bool express)` は変更しないこと。
- 責務ごとに小さなメソッドへ分割すること（1メソッド1責務）。
- `else` ブロックを使わないこと（early return、三項演算子、switch式などで書き換える）。
- 既存の挙動を保つこと。
  - 基本料金: `domestic` は500円、`asia` は1200円、`international` は2500円。
    それ以外の地域を指定した場合は `ArgumentException` を送出する。
  - 重量が20kgを**超える**場合、超過分1kgあたり50円を基本料金に加算する。
  - 重量が50kgを**超える**場合、さらに1000円を加算する（上記の超過分加算とは別に加算する）。
  - `express` が `true` の場合、ここまでの合計に1.5倍する。

## 制約

- `tests/ShippingCalculatorTests.cs` は既存のテストです。実装がこれを壊さないようにしてください。
- 外部 NuGet パッケージの追加は不要です。
