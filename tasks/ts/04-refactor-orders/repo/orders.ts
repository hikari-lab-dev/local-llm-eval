/** 注文集計レポート生成（リファクタリング対象。意図的に責務が混在した実装のまま置いている）。 */

export interface OrderRecord {
  item: string;
  category?: string;
  amount: number | null;
}

export interface OrderSummary {
  total: number;
  byCategory: Record<string, number>;
  averageByCategory: Record<string, number>;
  topItem: string | null;
  topAmount: number;
}

export function summarizeOrders(orders: OrderRecord[]): OrderSummary {
  let total = 0;
  const byCategory: Record<string, number> = {};
  const countByCategory: Record<string, number> = {};
  let topItem: string | null = null;
  let topAmount = 0;

  for (const order of orders) {
    if (order.amount === null || order.amount <= 0) {
      continue;
    }
    const amount = order.amount;
    const category = order.category === undefined ? "unknown" : order.category;
    total += amount;
    if (!(category in byCategory)) {
      byCategory[category] = 0;
      countByCategory[category] = 0;
    }
    byCategory[category] += amount;
    countByCategory[category] += 1;
    if (amount > topAmount) {
      topAmount = amount;
      topItem = order.item;
    } else {
      // 現在の最大値を更新しない
    }
  }

  const averageByCategory: Record<string, number> = {};
  for (const category of Object.keys(byCategory)) {
    averageByCategory[category] = byCategory[category] / countByCategory[category];
  }

  return { total, byCategory, averageByCategory, topItem, topAmount };
}
