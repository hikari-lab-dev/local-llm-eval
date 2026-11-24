/** 注文集計レポート生成。 */

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
  const validOrders = orders.filter(isCountable);
  const total = sumAmounts(validOrders);
  const byCategory = sumByCategory(validOrders);
  const counts = countByCategory(validOrders);
  const averageByCategory = averageByCategoryFrom(byCategory, counts);
  const { topItem, topAmount } = findTop(validOrders);
  return { total, byCategory, averageByCategory, topItem, topAmount };
}

function isCountable(order: OrderRecord): boolean {
  if (order.amount === null) {
    return false;
  }
  return order.amount > 0;
}

function categoryOf(order: OrderRecord): string {
  if (order.category === undefined) {
    return "unknown";
  }
  return order.category;
}

function sumAmounts(orders: OrderRecord[]): number {
  return orders.reduce((total, order) => total + (order.amount ?? 0), 0);
}

function sumByCategory(orders: OrderRecord[]): Record<string, number> {
  const totals: Record<string, number> = {};
  for (const order of orders) {
    const category = categoryOf(order);
    totals[category] = (totals[category] ?? 0) + (order.amount ?? 0);
  }
  return totals;
}

function countByCategory(orders: OrderRecord[]): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const order of orders) {
    const category = categoryOf(order);
    counts[category] = (counts[category] ?? 0) + 1;
  }
  return counts;
}

function averageByCategoryFrom(
  totals: Record<string, number>,
  counts: Record<string, number>,
): Record<string, number> {
  const averages: Record<string, number> = {};
  for (const category of Object.keys(totals)) {
    averages[category] = totals[category] / counts[category];
  }
  return averages;
}

function findTop(orders: OrderRecord[]): { topItem: string | null; topAmount: number } {
  if (orders.length === 0) {
    return { topItem: null, topAmount: 0 };
  }
  let topOrder = orders[0];
  for (const order of orders) {
    if ((order.amount ?? 0) > (topOrder.amount ?? 0)) {
      topOrder = order;
    }
  }
  return { topItem: topOrder.item, topAmount: topOrder.amount ?? 0 };
}
