namespace Reservations;

public sealed class SkuKey : IEquatable<SkuKey>
{
    public string WarehouseId { get; }
    public string Sku { get; }

    public SkuKey(string warehouseId, string sku)
    {
        WarehouseId = warehouseId;
        Sku = sku;
    }

    public bool Equals(SkuKey? other)
    {
        if (other is null)
        {
            return false;
        }
        return WarehouseId == other.WarehouseId && Sku == other.Sku;
    }

    public override bool Equals(object? obj) => Equals(obj as SkuKey);

    public override int GetHashCode() => HashCode.Combine(WarehouseId, Sku);
}
