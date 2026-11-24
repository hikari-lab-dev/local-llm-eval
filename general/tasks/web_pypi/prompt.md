requirements.txt の各パッケージについて、PyPI で公開されている最新の安定版（プレリリースを除く）を調べ、outdated.json に書いてください。パッケージのインストールはしないでください。

```json
{"requests": {"current": "2.28.0", "latest": "x.y.z", "major_update": true}}
```

`major_update` は、メジャーバージョン（先頭の数字）が上がっていれば true にしてください。
