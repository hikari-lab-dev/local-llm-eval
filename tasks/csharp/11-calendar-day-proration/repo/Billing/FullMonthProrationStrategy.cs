namespace Billing;

public sealed class FullMonthProrationStrategy : IProrationStrategy
{
    public decimal CalculateCharge(BillingRequest request)
    {
        return request.MonthlyFee;
    }
}
