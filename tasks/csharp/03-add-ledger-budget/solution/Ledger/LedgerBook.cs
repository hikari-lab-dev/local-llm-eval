namespace Ledger;

public sealed class LedgerBook
{
    private readonly List<Transaction> _transactions = [];
    private readonly Dictionary<string, decimal> _budgets = [];

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

    public void SetBudget(string category, decimal limit)
    {
        _budgets[category] = limit;
    }

    public decimal GetRemainingBudget(string category)
    {
        if (!_budgets.TryGetValue(category, out var limit))
        {
            throw new InvalidOperationException($"カテゴリ '{category}' の予算が設定されていません。");
        }

        return limit - GetTotalByCategory(category);
    }

    public bool IsOverBudget(string category)
    {
        return GetRemainingBudget(category) < 0m;
    }
}
