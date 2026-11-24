import test from "node:test";
import assert from "node:assert/strict";
import { summarizeOrders } from "../orders.ts";

test("basic summary", () => {
  const orders = [
    { item: "pen", category: "stationery", amount: 100 },
    { item: "notebook", category: "stationery", amount: 200 },
    { item: "coffee", category: "drink", amount: 300 },
  ];
  const summary = summarizeOrders(orders);
  assert.deepEqual(summary, {
    total: 600,
    byCategory: { stationery: 300, drink: 300 },
    averageByCategory: { stationery: 150, drink: 300 },
    topItem: "coffee",
    topAmount: 300,
  });
});
