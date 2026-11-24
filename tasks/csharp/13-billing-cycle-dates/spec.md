# 課題: 定期課金日の計算

`BillingCycle/CycleCalculator.cs`（新規ファイル）に、次の静的メソッドを実装してください。

```csharp
public static List<DateOnly> GenerateBillingDates(int anchorDay, DateOnly startMonth, int count)
```

## 仕様

- `anchorDay` は契約時に決まった「毎月の課金日」（1〜31）。
- `startMonth` の年月を1件目の対象月とし、そこから1か月ずつ進めた `count` か月ぶんの
  課金日リストを、月の昇順で返す。
- 対象月の日数が `anchorDay` に満たない場合（例: `anchorDay = 31` で対象月が2月）は、
  その月の**末日**に丸める（`BillingCycle/CalendarMath.cs` の
  `CalendarMath.DaysInMonth(year, month)` を使うこと。うるう年を含め、月の日数を
  ハードコードしないこと）。
- **重要**: 月をまたいで丸めが発生しても、その丸めた日付を次の月の計算の起点にしないこと。
  各月の課金日は、必ず**元の `anchorDay`** と「その月の日数」から独立に計算すること。
  - 例: `anchorDay = 31` で1月から5か月ぶん生成すると、
    `[1/31, 2/29（うるう年）, 3/31, 4/30, 5/31]` となる。2月に29日へ丸められたことが
    3月以降に引き継がれて「28」や「29」に固定され続けてはいけない
    （`DateOnly.AddMonths` を単純に繰り返し適用すると、.NET の `AddMonths` は
    「前回の日付のDay」を基準に丸めるため、この引き継ぎ不具合が起きる。年月から
    毎回 `anchorDay` を使って計算し直すこと）。
- 年をまたぐ場合（例: 11月から4か月ぶん生成すると翌年2月まで届く）も正しく年が進むこと。

## 制約

- `tests/CycleCalculatorTests.cs` は既存のテストです。実装がこれを壊さないようにしてください。
- `BillingCycle/CalendarMath.cs` の中身は変更しないでください。
- 外部 NuGet パッケージの追加は不要です。
