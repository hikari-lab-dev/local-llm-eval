/** 経費のデータモデル。 */

export type Category = "food" | "transport" | "other";

export interface Expense {
  title: string;
  amount: number;
  category: Category;
  paid: boolean;
}
