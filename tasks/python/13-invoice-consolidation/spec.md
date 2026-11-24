# 課題: 請求書明細の統合ロジックの実装

`invoice/builder.py`（新規ファイル）に、明細行のリストを受け取って統合済みの請求書を組み立てる
関数 `build_invoice(raw_items: list[LineItem]) -> list[InvoiceLine]` を実装してください
（`LineItem` / `InvoiceLine` / `InvalidInvoiceError` は `invoice/models.py` に定義済みです）。

## 仕様

### 1. 名寄せ（マージ）

- 同じ商品とみなす条件は、`invoice.normalize.normalize_name(name)` の結果が一致し、
  かつ `category` が完全一致すること（`normalize_name` は全角/半角・大文字小文字・前後空白の
  違いを吸収する。実装の詳細は変更せず、既存のものをそのまま使うこと）。
- マージした行の `quantity` は合算する。`unit_price` と `tax_rate` は最初に出現した行の値を使う
  （同一商品なら価格は同じである前提でよい。異なる場合の検証は不要）。
- 出力の `name`（表示名）は、統合前の**最初に出現した行の元の文字列**をそのまま使う
  （`normalize_name` した結果を表示名にしない）。

### 2. 検証（全件成功 or 全件失敗）

- マージ後の `quantity` が **0以下** になった商品が1つでもあれば、`InvalidInvoiceError` を送出し、
  他の商品が正常でも結果を一切返さないこと（部分的に成功した結果を返さない）。
  - 呼び出し側の `raw_items`（入力）は関数内で変更・破壊しないこと。

### 3. 金額計算

- 1行の `subtotal = unit_price * quantity`。
- 1行の `tax` は `subtotal * tax_rate` を「四捨五入（0.5は切り上げ）」で**整数円**
  （小数点以下0桁）に丸めたもの。`Decimal.quantize` を `ROUND_HALF_UP` で使うこと
  （Python 標準の `round()` は使わない）。
- 1行の `total = subtotal + tax`（`subtotal` は元々整数円である前提なので丸め不要）。

### 4. 並び順

- 出力は次のキーで昇順ソートする。
  1. カテゴリ: `invoice/categories.py` の `CATEGORY_ORDER` に載っている順。
     載っていないカテゴリは、載っているどのカテゴリより後ろに、
     カテゴリ名の文字コード順（昇順）で並べる。
  2. 同じカテゴリ内では、`normalize_name(name)` の昇順。
- 上記1・2のキーが完全に同じ行が複数存在することは無い前提でよい
  （同じカテゴリ・同じ正規化名の行は上記1でマージ済みのため）。

## 制約

- `tests/test_builder_basic.py` は既存のテストです。実装がこれを壊さないようにしてください。
- `invoice/normalize.py` と `invoice/categories.py` の中身は変更しないでください。
- 標準ライブラリのみ使用可能。金額計算は `Decimal` で行うこと。
