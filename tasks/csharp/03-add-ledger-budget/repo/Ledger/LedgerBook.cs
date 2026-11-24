namespace Ledger;

public sealed class LedgerBook
{
    private readonly List<Transaction> _transactions = [];

    public void AddTransaction(string category, decimal amount)
    {
        _transactions.Add(new Transaction(category, amount));
    }

    public decimal GetTotalByCategory(string category)
    {
        return _transactions
            .Where(transaction => transaction.Category == category)
            .Sum(transaction => transaction.Amount);
    }

    public IReadOnlyList<Transaction> GetAllTransactions()
    {
        return _transactions;
    }
}
