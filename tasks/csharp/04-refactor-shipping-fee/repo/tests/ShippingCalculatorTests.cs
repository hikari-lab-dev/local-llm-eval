namespace ShippingFee.Tests;

public class ShippingCalculatorTests
{
    [Fact]
    public void DomesticLightWeightHasNoSurcharge()
    {
        Assert.Equal(500m, ShippingCalculator.CalculateFee(5m, "domestic", express: false));
    }

    [Fact]
    public void DomesticOverweightAddsPerKilogramSurcharge()
    {
        Assert.Equal(750m, ShippingCalculator.CalculateFee(25m, "domestic", express: false));
    }

    [Fact]
    public void DomesticHeavyWeightAddsFlatSurcharge()
    {
        Assert.Equal(3250m, ShippingCalculator.CalculateFee(55m, "domestic", express: false));
    }

    [Fact]
    public void AsiaExpressAppliesMultiplier()
    {
        Assert.Equal(1800m, ShippingCalculator.CalculateFee(10m, "asia", express: true));
    }

    [Fact]
    public void UnknownRegionThrows()
    {
        Assert.Throws<ArgumentException>(
            () => ShippingCalculator.CalculateFee(5m, "moon", express: false));
    }
}
