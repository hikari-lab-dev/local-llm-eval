/** 経費一覧の表示整形。 */

import type { Expense } from "./model.ts";

export function formatExpenses(expenses: Expense[]): string[] {
  return expenses.map(
    (expense) =>
      `[${expense.paid ? "x" : " "}] ${expense.title} (${expense.category}): ${expense.amount}`,
  );
}

// TODO: formatFilteredExpenses(store, options) を実装する（spec.md 参照）。
