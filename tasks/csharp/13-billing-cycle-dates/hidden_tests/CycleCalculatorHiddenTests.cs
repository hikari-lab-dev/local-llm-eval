namespace BillingCycle.Tests;

public class CycleCalculatorHiddenTests
{
    [Fact]
    public void ClampedMonthDoesNotCarryOverToLaterMonths()
    {
        var dates = CycleCalculator.GenerateBillingDates(
            anchorDay: 31,
            startMonth: new DateOnly(2024, 1, 1),
            count: 5);

        Assert.Equal(
            [
                new DateOnly(2024, 1, 31),
                new DateOnly(2024, 2, 29),
                new DateOnly(2024, 3, 31),
                new DateOnly(2024, 4, 30),
                new DateOnly(2024, 5, 31),
            ],
            dates);
    }

    [Fact]
    public void NonLeapFebruaryClampsToTwentyEight()
    {
        var dates = CycleCalculator.GenerateBillingDates(
            anchorDay: 29,
            startMonth: new DateOnly(2023, 1, 1),
            count: 3);

        Assert.Equal(
            [
                new DateOnly(2023, 1, 29),
                new DateOnly(2023, 2, 28),
                new DateOnly(2023, 3, 29),
            ],
            dates);
    }

    [Fact]
    public void SequenceRollsOverIntoTheNextYear()
    {
        var dates = CycleCalculator.GenerateBillingDates(
            anchorDay: 31,
            startMonth: new DateOnly(2024, 11, 1),
            count: 4);

        Assert.Equal(
            [
                new DateOnly(2024, 11, 30),
                new DateOnly(2024, 12, 31),
                new DateOnly(2025, 1, 31),
                new DateOnly(2025, 2, 28),
            ],
            dates);
    }
}
