namespace ShippingFee.HiddenTests;

public class ShippingCalculatorBehaviorHiddenTests
{
    [Fact]
    public void WeightExactlyAtSurchargeBoundaryHasNoSurcharge()
    {
        Assert.Equal(500m, ShippingCalculator.CalculateFee(20m, "domestic", express: false));
    }

    [Fact]
    public void WeightExactlyAtHeavyBoundaryHasNoFlatSurcharge()
    {
        Assert.Equal(2000m, ShippingCalculator.CalculateFee(50m, "domestic", express: false));
    }

    [Fact]
    public void InternationalHeavyExpressCombinesAllSurcharges()
    {
        Assert.Equal(8250m, ShippingCalculator.CalculateFee(60m, "international", express: true));
    }
}
