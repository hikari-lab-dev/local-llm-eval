# 課題: 駐車場管理モジュールのバグ修正

`ParkingFees/ParkingLot.cs` と `ParkingFees/FeeCalculator.cs` にまたがるバグを修正してください。

## 仕様

- `ParkingLot.Park()` は満車（`OccupiedSpots == TotalSpots`）の場合 `InvalidOperationException` を送出し、
  `OccupiedSpots` を変更しない。
- `FeeCalculator.CalculateFee(hours)` は `hours` 時間ぶんの駐車料金（`300円 * hours`）を返す。
  - 駐車時間が5時間**以上**（5時間を含む）の場合、合計金額から20%割引する。

## 制約

- `tests/ParkingLotTests.cs` と `tests/FeeCalculatorTests.cs` は既存のテストです。
  実装がこれらを壊さないようにしてください。
- 外部 NuGet パッケージの追加は不要です。
