# 課題: 日割り課金ストラテジーの追加

`Billing/` は、サブスクリプションの月額課金を計算するライブラリです。
`SubscriptionBiller` は `IProrationStrategy` を実装したストラテジーに課金計算を委譲します
（Strategyパターン）。既存の `FullMonthProrationStrategy` は常に満額を返すだけの実装です。

利用開始日・終了日に応じて日割り計算する `CalendarDayProrationStrategy` を実装してください。

## 仕様

- 新しいクラス `Billing.CalendarDayProrationStrategy` を実装し、`IProrationStrategy` を実装すること。
- `CalculateCharge(BillingRequest request)` は次の手順で金額を計算する。
  1. その請求対象月の総日数を `CalendarMath.DaysInMonth(request.ActiveStart.Year, request.ActiveStart.Month)`
     で取得する（**うるう年を含め、月ごとの日数をハードコードしないこと**。`ActiveStart` と
     `ActiveEnd` は必ず同じ年月内にある前提でよい）。
  2. 利用日数を `request.ActiveEnd.DayNumber - request.ActiveStart.DayNumber + 1`
     （両端を含む日数）で求める。
  3. `1日あたりの金額 = request.MonthlyFee / 総日数` を計算する。
  4. `請求額 = 1日あたりの金額 × 利用日数` を、小数点以下2桁に「四捨五入（0.5は必ず切り上げる）」
     で丸めて返す。**C# の `Math.Round` は既定では「0.5は偶数側に丸める」銀行丸めのため、
     必ず `MidpointRounding.AwayFromZero` を明示的に指定すること。**

## 制約

- `tests/SubscriptionBillerTests.cs` は既存のテストです。実装がこれを壊さないようにしてください。
- `Billing/CalendarMath.cs` の中身は変更しないでください。
- 既存の public メンバー（`IProrationStrategy`, `BillingRequest`, `FullMonthProrationStrategy`,
  `SubscriptionBiller`）のシグネチャは変更しないこと。
- 外部 NuGet パッケージの追加は不要です。
