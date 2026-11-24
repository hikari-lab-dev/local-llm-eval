namespace Billing;

public sealed record BillingRequest(decimal MonthlyFee, DateOnly ActiveStart, DateOnly ActiveEnd);

public interface IProrationStrategy
{
    decimal CalculateCharge(BillingRequest request);
}
