namespace Billing.Tests;

public class SubscriptionBillerTests
{
    [Fact]
    public void FullMonthStrategyAlwaysChargesFullFee()
    {
        var biller = new SubscriptionBiller(new FullMonthProrationStrategy());
        var request = new BillingRequest(
            MonthlyFee: 980m,
            ActiveStart: new DateOnly(2024, 3, 1),
            ActiveEnd: new DateOnly(2024, 3, 10));

        var charge = biller.CalculateMonthlyCharge(request);

        Assert.Equal(980m, charge);
    }
}
