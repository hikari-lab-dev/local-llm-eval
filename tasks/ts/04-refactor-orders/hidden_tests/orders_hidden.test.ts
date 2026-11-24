import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { summarizeOrders } from "../orders.ts";

test("excludes null, zero and negative amount", () => {
  const orders = [
    { item: "a", category: "x", amount: 0 },
    { item: "b", category: "x", amount: -5 },
    { item: "c", category: "x", amount: null },
    { item: "d", category: "x", amount: 50 },
  ];
  const summary = summarizeOrders(orders);
  assert.equal(summary.total, 50);
});

test("topItem ignores excluded records", () => {
  const orders = [
    { item: "a", category: "x", amount: -5 },
    { item: "d", category: "x", amount: 50 },
  ];
  const summary = summarizeOrders(orders);
  assert.equal(summary.topItem, "d");
});

test("missing category becomes unknown", () => {
  const orders = [{ item: "a", amount: 10 }];
  const summary = summarizeOrders(orders);
  assert.deepEqual(summary.byCategory, { unknown: 10 });
});

test("average by category", () => {
  const orders = [
    { item: "a", category: "x", amount: 10 },
    { item: "b", category: "x", amount: 30 },
  ];
  const summary = summarizeOrders(orders);
  assert.deepEqual(summary.averageByCategory, { x: 20 });
});

test("empty orders returns defaults", () => {
  const summary = summarizeOrders([]);
  assert.deepEqual(summary, {
    total: 0,
    byCategory: {},
    averageByCategory: {},
    topItem: null,
    topAmount: 0,
  });
});

test("source contains no else blocks", () => {
  const source = readFileSync("orders.ts", "utf-8");
  assert.equal(/\belse\b/.test(source), false);
});

test("summarizeOrders is split into helper functions", () => {
  const source = readFileSync("orders.ts", "utf-8");
  const matches = source.match(/^\s*(export\s+)?function\s+\w+/gm) ?? [];
  assert.ok(
    matches.length >= 4,
    `expected at least 4 function declarations, found ${matches.length}`,
  );
});
