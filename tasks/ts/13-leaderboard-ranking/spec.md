# 課題: ランキング表の実装

`leaderboard/rank.ts`（新規ファイル）に、以下の2つの関数を実装してください。

- `leaderboard/models.ts` の `PlayerScore` / `RankedEntry`
- `leaderboard/scoring.ts` の `roundScore(rawScore, bonusMultiplier)`（スコア計算。既存のまま使うこと）
- `leaderboard/textWidth.ts` の `displayWidth(text)` / `charWidth(char)`（表示幅計算。既存のまま使うこと）

## 1. `truncateForDisplay(name: string, maxWidth: number): string`

- `displayWidth(name) <= maxWidth` ならそのまま `name` を返す（省略記号は付けない）。
- 超える場合は、末尾に省略記号 `"…"`（表示幅1）を付けた結果の表示幅が `maxWidth` を
  超えないところまで、先頭から**1文字単位**で切り詰める。
  - 全角文字（表示幅2）を含める余地が半分（表示幅1）しか無い場合は、その文字を含めず
    そこで打ち切る（幅を超えてはいけない）。
  - 例: `maxWidth = 6` で `"たなかたろう"`（全角6文字、表示幅12）を渡すと、
    省略記号込みで表示幅6以内に収まる `"たな…"`（表示幅5）を返す。
  - 例: `maxWidth = 5` で `"Bob田中"`（表示幅7）を渡すと `"Bob…"`（表示幅4）を返す
    （`"Bob田"` は表示幅5になるが、省略記号を付けると表示幅6になり超過するため、
    `"田"` は含めない）。

## 2. `rankPlayers(entries: PlayerScore[], maxNameWidth: number): RankedEntry[]`

- 各エントリのスコアは `roundScore(entry.rawScore, entry.bonusMultiplier)` で計算する。
- スコアの降順で並べる。
- **同点の扱いは「競技順位（1224方式）」とする**: 同点のエントリは同じ順位になり、
  次に続く異なるスコアの順位は「同点だったエントリの人数ぶん」スキップする
  （例: 100点が2人なら両方1位、次のスコアの人は3位。ここでいわゆる「1223方式」
  ＝同点の人数に関係なく次を2位にする方式は使わないこと）。
- 同点内の並び順は、名前の Unicode コードポイント順（JavaScript の文字列比較演算子
  `<` の順序）の昇順とする。
- `RankedEntry.name` は元の名前をそのまま、`displayName` は
  `truncateForDisplay(name, maxNameWidth)` の結果を入れる
  （ソート・同点判定には常に元の `name` を使うこと。切り詰めた `displayName` を
  ソートキーに使わないこと）。

## 制約

- `tests/rank.test.ts` は既存のテストです。実装がこれを壊さないようにしてください。
- `leaderboard/scoring.ts` と `leaderboard/textWidth.ts` の中身は変更しないでください。
- コンストラクタのパラメータプロパティは使わないこと。外部ライブラリは使用しないこと。
