namespace Reservations.Tests;

public class ReservationCacheTests
{
    private static readonly SkuKey Key = new("wh-1", "sku-42");

    private static ReservationCache CreateFilledCache()
    {
        var cache = new ReservationCache(capacityPerSlot: 10);
        cache.TryReserve(Key, 4);
        cache.TryReserve(Key, 6);
        return cache;
    }

    [Fact]
    public void ZeroQuantityReservationAtFullCapacityIsAccepted()
    {
        var cache = CreateFilledCache();

        var accepted = cache.TryReserve(Key, 0);

        Assert.True(accepted);
    }

    [Fact]
    public void ExceedingCapacityIsRejected()
    {
        var cache = CreateFilledCache();

        var accepted = cache.TryReserve(Key, 1);

        Assert.False(accepted);
    }

    [Fact]
    public void ReservedQuantityReflectsAccumulatedTotal()
    {
        var cache = CreateFilledCache();

        Assert.Equal(10, cache.GetReservedQuantity(Key));
    }
}
