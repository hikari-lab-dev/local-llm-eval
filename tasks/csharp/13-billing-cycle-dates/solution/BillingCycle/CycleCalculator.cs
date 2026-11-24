namespace BillingCycle;

public static class CycleCalculator
{
    public static List<DateOnly> GenerateBillingDates(int anchorDay, DateOnly startMonth, int count)
    {
        var dates = new List<DateOnly>(count);
        var startIndex = (startMonth.Year * 12) + (startMonth.Month - 1);
        for (var offset = 0; offset < count; offset++)
        {
            var monthIndex = startIndex + offset;
            var year = monthIndex / 12;
            var month = (monthIndex % 12) + 1;
            var day = Math.Min(anchorDay, CalendarMath.DaysInMonth(year, month));
            dates.Add(new DateOnly(year, month, day));
        }
        return dates;
    }
}
