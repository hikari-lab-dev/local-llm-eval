import test from "node:test";
import assert from "node:assert/strict";
import { ExpenseStore } from "../expense/store.ts";
import { formatExpenses } from "../expense/format.ts";

test("add and list all", () => {
  const store = new ExpenseStore();
  store.add("牛乳", 200, "food");
  store.add("電車代", 300, "transport", true);
  const titles = store.listAll().map((expense) => expense.title);
  assert.deepEqual(titles, ["牛乳", "電車代"]);
});

test("formatExpenses formats paid marker and fields", () => {
  const store = new ExpenseStore();
  store.add("牛乳", 200, "food", true);
  const lines = formatExpenses(store.listAll());
  assert.deepEqual(lines, ["[x] 牛乳 (food): 200"]);
});
