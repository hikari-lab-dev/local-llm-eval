namespace ParkingFees.HiddenTests;

public class FeeCalculatorHiddenTests
{
    [Fact]
    public void DiscountAppliesExactlyAtThreshold()
    {
        Assert.Equal(1200m, FeeCalculator.CalculateFee(hours: 5));
    }

    [Fact]
    public void NoDiscountJustBelowThreshold()
    {
        Assert.Equal(1200m, FeeCalculator.CalculateFee(hours: 4));
    }
}
