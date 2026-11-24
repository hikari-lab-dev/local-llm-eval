/** 経費記録の保持と一覧管理。 */

import type { Category, Expense } from "./model.ts";

export class ExpenseStore {
  private expenses: Expense[] = [];

  add(title: string, amount: number, category: Category, paid = false): Expense {
    const expense: Expense = { title, amount, category, paid };
    this.expenses.push(expense);
    return expense;
  }

  listAll(): Expense[] {
    return [...this.expenses];
  }

  filterBy(options?: { paid?: boolean; category?: Category }): Expense[] {
    const filtered = this.expenses.filter((expense) => {
      if (options?.paid !== undefined && expense.paid !== options.paid) {
        return false;
      }
      if (options?.category !== undefined && expense.category !== options.category) {
        return false;
      }
      return true;
    });
    return filtered
      .map((expense, index) => ({ expense, index }))
      .sort((a, b) => b.expense.amount - a.expense.amount || a.index - b.index)
      .map((entry) => entry.expense);
  }
}
