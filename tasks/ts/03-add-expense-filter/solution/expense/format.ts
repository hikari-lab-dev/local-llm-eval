/** 経費一覧の表示整形。 */

import type { Category, Expense } from "./model.ts";
import type { ExpenseStore } from "./store.ts";

export function formatExpenses(expenses: Expense[]): string[] {
  return expenses.map(
    (expense) =>
      `[${expense.paid ? "x" : " "}] ${expense.title} (${expense.category}): ${expense.amount}`,
  );
}

export function formatFilteredExpenses(
  store: ExpenseStore,
  options?: { paid?: boolean; category?: Category },
): string[] {
  return formatExpenses(store.filterBy(options));
}
