# 課題: 在庫予約キャッシュが容量を超えて予約を受け付けてしまう

`Reservations.ReservationCache` は、倉庫ID・SKU（`SkuKey`）ごとに予約数量を積み上げ、
`capacityPerSlot` を超える予約を `TryReserve` で拒否する仕組みです。運用チームから
次の不具合報告がありました。

## 再現手順

実運用では、予約リクエストが届くたびに（例えば HTTP リクエストのボディなどから）
その都度 `new SkuKey(warehouseId, sku)` を作って `TryReserve` / `GetReservedQuantity`
を呼び出します。つまり、同じ倉庫・SKUの組み合わせでも呼び出しごとに**別のインスタンス**の
`SkuKey` が渡されます。

```csharp
var cache = new ReservationCache(capacityPerSlot: 10);

cache.TryReserve(new SkuKey("wh-1", "sku-42"), 4); // true になるべき
cache.TryReserve(new SkuKey("wh-1", "sku-42"), 6); // true になるべき（累計10）
cache.TryReserve(new SkuKey("wh-1", "sku-42"), 1); // 容量超過なので false になるべき

cache.GetReservedQuantity(new SkuKey("wh-1", "sku-42")); // 10 になるべき
```

しかし実際には、**2回目以降の呼び出しが「初めての予約」として扱われてしまい**、
`TryReserve` が3回とも `true` を返し、`GetReservedQuantity` も直前の1回分（1）しか
返しません（同じ倉庫・SKUのはずなのに、別々のスロットとして扱われている）。

同じ `SkuKey` インスタンスを使い回すテスト（`tests/ReservationCacheTests.cs`）は、
この不具合を検出できていません。

## 求めること

- 上記の再現手順の通り、`WarehouseId` と `Sku` の値が同じであれば、別インスタンスの
  `SkuKey` を渡しても同じ予約スロットとして扱われるように修正してください。
- 原因を `ReservationCache.TryReserve` / `GetReservedQuantity` の容量判定・積算ロジック
  自体に限定して探さないこと。同じインスタンスを使い回す限りは正しく動作しており、
  容量判定の計算式自体に誤りはありません。

## 制約

- `tests/ReservationCacheTests.cs` は既存のテストです。実装がこれを壊さないようにしてください。
- `ReservationCache` の public メンバーのシグネチャ（`TryReserve`, `GetReservedQuantity`,
  コンストラクタ）は変更しないこと。
- 外部 NuGet パッケージの追加は不要です。
