namespace Reservations;

public sealed class ReservationCache
{
    private readonly Dictionary<SkuKey, int> _reserved = [];
    private readonly int _capacityPerSlot;

    public ReservationCache(int capacityPerSlot)
    {
        _capacityPerSlot = capacityPerSlot;
    }

    public bool TryReserve(SkuKey key, int quantity)
    {
        var current = GetReservedQuantity(key);
        if (current + quantity > _capacityPerSlot)
        {
            return false;
        }
        _reserved[key] = current + quantity;
        return true;
    }

    public int GetReservedQuantity(SkuKey key)
    {
        return _reserved.TryGetValue(key, out var existing) ? existing : 0;
    }
}
