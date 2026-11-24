namespace Reservations.Tests;

public class ReservationCacheHiddenTests
{
    [Fact]
    public void EquivalentKeysFromDifferentInstancesAccumulateTogether()
    {
        var cache = new ReservationCache(capacityPerSlot: 10);

        var first = cache.TryReserve(new SkuKey("wh-1", "sku-42"), 4);
        var second = cache.TryReserve(new SkuKey("wh-1", "sku-42"), 6);

        Assert.True(first && second);
    }

    [Fact]
    public void EquivalentKeysFromDifferentInstancesEnforceCapacity()
    {
        var cache = new ReservationCache(capacityPerSlot: 10);
        cache.TryReserve(new SkuKey("wh-1", "sku-42"), 4);
        cache.TryReserve(new SkuKey("wh-1", "sku-42"), 6);

        var overflow = cache.TryReserve(new SkuKey("wh-1", "sku-42"), 1);

        Assert.False(overflow);
    }

    [Fact]
    public void GetReservedQuantityAggregatesAcrossInstances()
    {
        var cache = new ReservationCache(capacityPerSlot: 10);
        cache.TryReserve(new SkuKey("wh-1", "sku-42"), 4);
        cache.TryReserve(new SkuKey("wh-1", "sku-42"), 6);

        Assert.Equal(10, cache.GetReservedQuantity(new SkuKey("wh-1", "sku-42")));
    }

    [Fact]
    public void DifferentSkuIsAnIndependentSlot()
    {
        var cache = new ReservationCache(capacityPerSlot: 5);
        cache.TryReserve(new SkuKey("wh-1", "sku-1"), 5);

        var accepted = cache.TryReserve(new SkuKey("wh-1", "sku-2"), 5);

        Assert.True(accepted);
    }

    [Fact]
    public void DifferentWarehouseIsAnIndependentSlot()
    {
        var cache = new ReservationCache(capacityPerSlot: 5);
        cache.TryReserve(new SkuKey("wh-1", "sku-1"), 5);

        var accepted = cache.TryReserve(new SkuKey("wh-2", "sku-1"), 5);

        Assert.True(accepted);
    }
}
