expenses.csv は経費の一覧です。次の規則で集計し、summary.json に書いてください。

- tax が「税抜」の行は、amount に 1.1 を掛けて 1 円未満を切り捨てた額を税込額とする。「税込」の行は amount のまま
- memo に「取消」とある行は除外する
- date・item・amount がすべて同じ行が複数ある場合は、重複として 1 件だけ数える

```json
{"by_category": {"交通費": 0, "消耗品": 0, "会議費": 0, "通信費": 0, "書籍": 0}, "total": 0, "max_month": "YYYY-MM"}
```

`max_month` は税込合計が最も大きい月です。
