# 課題: 地域別レポートの集計結果がおかしい

`reports` パッケージは地域・月ごとの売上合計を返す `reports.summary.monthly_region_report`
を提供しています。運用チームから次の不具合報告がありました。

## 再現手順

```python
from reports.summary import monthly_region_report

print(monthly_region_report(region="east", month="2024-01"))
print(monthly_region_report(region="west", month="2024-01"))
print(monthly_region_report(region="east", month="2024-02"))
```

期待する出力（`reports/data.py` の生データから手計算した金額）:

```text
{'region': 'east', 'month': '2024-01', 'total': Decimal('1500')}
{'region': 'west', 'month': '2024-01', 'total': Decimal('600')}
{'region': 'east', 'month': '2024-02', 'total': Decimal('700')}
```

しかし実際には、2件目・3件目の呼び出しが **1件目と同じ `Decimal('1500')` を返してしまいます**
（`region` や `month` を変えても結果が変わらない）。1件だけ呼び出す分には正しい値が返るため、
既存のテスト（`tests/test_summary.py`）はこの不具合を検出できていません。

## 求めること

- 上記の再現手順で、呼び出しごとに正しい合計金額が返るように修正してください。
- 原因を `reports/summary.py` や `reports/aggregate.py` の集計ロジックに限定して探さないこと。
  合計金額を計算するロジック自体（`SALES` のフィルタ処理）は正しく、再現手順の1回目の呼び出しが
  正しい値を返すことからも分かる通り、集計式そのものに誤りはありません。

## 制約

- `tests/test_summary.py` は既存のテストです。実装がこれを壊さないようにしてください。
- `reports/data.py` の内容（サンプルデータ）は変更しないでください。
- 標準ライブラリのみ使用可能。
