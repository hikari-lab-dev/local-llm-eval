namespace Billing.Tests;

public class CalendarDayProrationStrategyHiddenTests
{
    private static readonly CalendarDayProrationStrategy Strategy = new();

    [Fact]
    public void FullNonLeapFebruaryChargesFullFee()
    {
        var request = new BillingRequest(
            MonthlyFee: 280m,
            ActiveStart: new DateOnly(2023, 2, 1),
            ActiveEnd: new DateOnly(2023, 2, 28));

        Assert.Equal(280m, Strategy.CalculateCharge(request));
    }

    [Fact]
    public void FullLeapFebruaryUsesTwentyNineDays()
    {
        var request = new BillingRequest(
            MonthlyFee: 290m,
            ActiveStart: new DateOnly(2024, 2, 1),
            ActiveEnd: new DateOnly(2024, 2, 29));

        Assert.Equal(290m, Strategy.CalculateCharge(request));
    }

    [Fact]
    public void FullThirtyOneDayMonthUsesInclusiveDayCount()
    {
        var request = new BillingRequest(
            MonthlyFee: 310m,
            ActiveStart: new DateOnly(2024, 1, 1),
            ActiveEnd: new DateOnly(2024, 1, 31));

        Assert.Equal(310m, Strategy.CalculateCharge(request));
    }

    [Fact]
    public void ExactHalfCentRoundsAwayFromZeroNotToEven()
    {
        var request = new BillingRequest(
            MonthlyFee: 3.5m,
            ActiveStart: new DateOnly(2023, 2, 1),
            ActiveEnd: new DateOnly(2023, 2, 1));

        Assert.Equal(0.13m, Strategy.CalculateCharge(request));
    }

    [Fact]
    public void PartialMonthChargesProportionalAmount()
    {
        var request = new BillingRequest(
            MonthlyFee: 300m,
            ActiveStart: new DateOnly(2024, 4, 1),
            ActiveEnd: new DateOnly(2024, 4, 15));

        Assert.Equal(150m, Strategy.CalculateCharge(request));
    }
}
