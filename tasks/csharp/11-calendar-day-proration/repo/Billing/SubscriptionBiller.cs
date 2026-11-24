namespace Billing;

public sealed class SubscriptionBiller
{
    private readonly IProrationStrategy _strategy;

    public SubscriptionBiller(IProrationStrategy strategy)
    {
        _strategy = strategy;
    }

    public decimal CalculateMonthlyCharge(BillingRequest request)
    {
        return _strategy.CalculateCharge(request);
    }
}
