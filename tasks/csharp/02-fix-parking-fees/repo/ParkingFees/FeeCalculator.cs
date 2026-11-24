namespace ParkingFees;

public static class FeeCalculator
{
    private const decimal HourlyRate = 300m;
    private const int LongStayThresholdHours = 5;
    private const decimal LongStayDiscountRate = 0.2m;

    public static decimal CalculateFee(int hours)
    {
        var total = HourlyRate * hours;
        if (hours > LongStayThresholdHours)
        {
            return total * (1 - LongStayDiscountRate);
        }

        return total;
    }
}
