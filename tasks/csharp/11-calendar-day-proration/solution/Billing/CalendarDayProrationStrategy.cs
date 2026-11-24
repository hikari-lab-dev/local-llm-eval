namespace Billing;

public sealed class CalendarDayProrationStrategy : IProrationStrategy
{
    public decimal CalculateCharge(BillingRequest request)
    {
        var totalDays = CalendarMath.DaysInMonth(request.ActiveStart.Year, request.ActiveStart.Month);
        var activeDays = request.ActiveEnd.DayNumber - request.ActiveStart.DayNumber + 1;
        var perDay = request.MonthlyFee / totalDays;
        return Math.Round(perDay * activeDays, 2, MidpointRounding.AwayFromZero);
    }
}
