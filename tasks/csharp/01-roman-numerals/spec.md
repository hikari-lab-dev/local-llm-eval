# 課題: ローマ数字変換

`RomanNumerals/RomanConverter.cs` の `RomanConverter.ToRoman` メソッドを実装してください。

## 仕様

- 引数 `value`（1〜3999 の整数）を対応するローマ数字表記の文字列に変換して返す。
- 減算記法（例: 4 は `IV`、9 は `IX`、40 は `XL`、90 は `XC`、400 は `CD`、900 は `CM`）を使う。
- `value` が 1〜3999 の範囲外の場合は `ArgumentOutOfRangeException` を送出する。

## 制約

- `tests/RomanConverterTests.cs` は既存のテストです。実装がこれを壊さないようにしてください。
- 外部 NuGet パッケージの追加は不要です。
