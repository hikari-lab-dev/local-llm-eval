namespace Ledger.HiddenTests;

public class LedgerBookBudgetHiddenTests
{
    [Fact]
    public void GetRemainingBudgetSubtractsSpentAmount()
    {
        var book = new LedgerBook();
        book.SetBudget("food", 5000m);
        book.AddTransaction("food", 1200m);

        Assert.Equal(3800m, book.GetRemainingBudget("food"));
    }

    [Fact]
    public void GetRemainingBudgetIgnoresOtherCategories()
    {
        var book = new LedgerBook();
        book.SetBudget("food", 5000m);
        book.AddTransaction("transport", 4000m);

        Assert.Equal(5000m, book.GetRemainingBudget("food"));
    }

    [Fact]
    public void GetRemainingBudgetThrowsWhenBudgetNotSet()
    {
        var book = new LedgerBook();

        Assert.Throws<InvalidOperationException>(() => book.GetRemainingBudget("food"));
    }

    [Fact]
    public void IsOverBudgetIsFalseWhenWithinLimit()
    {
        var book = new LedgerBook();
        book.SetBudget("food", 5000m);
        book.AddTransaction("food", 1200m);

        Assert.False(book.IsOverBudget("food"));
    }

    [Fact]
    public void IsOverBudgetIsTrueWhenExceedingLimit()
    {
        var book = new LedgerBook();
        book.SetBudget("food", 1000m);
        book.AddTransaction("food", 1200m);

        Assert.True(book.IsOverBudget("food"));
    }

    [Fact]
    public void IsOverBudgetIsFalseWhenExactlyAtLimit()
    {
        var book = new LedgerBook();
        book.SetBudget("food", 1200m);
        book.AddTransaction("food", 1200m);

        Assert.False(book.IsOverBudget("food"));
    }
}
