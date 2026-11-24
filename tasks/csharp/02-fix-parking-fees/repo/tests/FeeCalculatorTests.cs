namespace ParkingFees.Tests;

public class FeeCalculatorTests
{
    [Fact]
    public void ShortStayHasNoDiscount()
    {
        Assert.Equal(600m, FeeCalculator.CalculateFee(hours: 2));
    }

    [Fact]
    public void LongStayAboveThresholdHasDiscount()
    {
        Assert.Equal(2400m, FeeCalculator.CalculateFee(hours: 10));
    }
}
