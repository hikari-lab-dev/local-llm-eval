namespace Reservations;

public sealed class SkuKey
{
    public string WarehouseId { get; }
    public string Sku { get; }

    public SkuKey(string warehouseId, string sku)
    {
        WarehouseId = warehouseId;
        Sku = sku;
    }
}
