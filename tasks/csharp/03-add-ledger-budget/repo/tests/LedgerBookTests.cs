namespace Ledger.Tests;

public class LedgerBookTests
{
    [Fact]
    public void AddTransactionAppearsInAllTransactions()
    {
        var book = new LedgerBook();

        book.AddTransaction("food", 1200m);

        Assert.Single(book.GetAllTransactions());
    }

    [Fact]
    public void GetTotalByCategorySumsMatchingTransactions()
    {
        var book = new LedgerBook();
        book.AddTransaction("food", 1200m);
        book.AddTransaction("food", 800m);
        book.AddTransaction("transport", 500m);

        Assert.Equal(2000m, book.GetTotalByCategory("food"));
    }

    [Fact]
    public void GetTotalByCategoryReturnsZeroForUnknownCategory()
    {
        var book = new LedgerBook();

        Assert.Equal(0m, book.GetTotalByCategory("unknown"));
    }
}
