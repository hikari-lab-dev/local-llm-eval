import test from "node:test";
import assert from "node:assert/strict";
import { ExpenseStore } from "../expense/store.ts";
import { formatFilteredExpenses } from "../expense/format.ts";

test("formatFilteredExpenses formats sorted and filtered result", () => {
  const store = new ExpenseStore();
  store.add("牛乳", 200, "food", false);
  store.add("コーヒー", 400, "food", true);
  store.add("電車代", 500, "transport", true);

  const lines = formatFilteredExpenses(store, { category: "food" });
  assert.deepEqual(lines, ["[x] コーヒー (food): 400", "[ ] 牛乳 (food): 200"]);
});

test("formatFilteredExpenses with no options formats all sorted by amount desc", () => {
  const store = new ExpenseStore();
  store.add("牛乳", 200, "food", false);
  store.add("電車代", 500, "transport", true);

  const lines = formatFilteredExpenses(store);
  assert.deepEqual(lines, ["[x] 電車代 (transport): 500", "[ ] 牛乳 (food): 200"]);
});
