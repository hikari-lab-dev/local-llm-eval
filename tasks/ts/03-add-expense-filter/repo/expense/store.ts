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

  // TODO: filterBy(options) を実装する（spec.md 参照）。
}
