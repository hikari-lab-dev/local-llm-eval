namespace BillingCycle.Tests;

public class CycleCalculatorTests
{
    [Fact]
    public void NoClampingNeededReturnsSameDayEachMonth()
    {
        var dates = CycleCalculator.GenerateBillingDates(
            anchorDay: 5,
            startMonth: new DateOnly(2024, 1, 1),
            count: 3);

        Assert.Equal(
            [new DateOnly(2024, 1, 5), new DateOnly(2024, 2, 5), new DateOnly(2024, 3, 5)],
            dates);
    }
}
