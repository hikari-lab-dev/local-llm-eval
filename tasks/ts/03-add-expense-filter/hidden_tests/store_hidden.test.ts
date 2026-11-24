import test from "node:test";
import assert from "node:assert/strict";
import { ExpenseStore } from "../expense/store.ts";

function buildSampleStore(): ExpenseStore {
  const store = new ExpenseStore();
  store.add("牛乳", 200, "food", false);
  store.add("電車代", 500, "transport", true);
  store.add("コーヒー", 400, "food", true);
  store.add("バス代", 500, "transport", false);
  store.add("雑誌", 300, "other", false);
  return store;
}

test("filterBy with no options returns all sorted by amount desc", () => {
  const store = buildSampleStore();
  const titles = store.filterBy().map((expense) => expense.title);
  assert.deepEqual(titles, ["電車代", "バス代", "コーヒー", "雑誌", "牛乳"]);
});

test("filterBy same amount keeps insertion order (stable sort)", () => {
  const store = buildSampleStore();
  const titles = store.filterBy({ category: "transport" }).map((expense) => expense.title);
  assert.deepEqual(titles, ["電車代", "バス代"]);
});

test("filterBy paid only", () => {
  const store = buildSampleStore();
  const titles = store.filterBy({ paid: true }).map((expense) => expense.title);
  assert.deepEqual(titles, ["電車代", "コーヒー"]);
});

test("filterBy category only", () => {
  const store = buildSampleStore();
  const titles = store.filterBy({ category: "food" }).map((expense) => expense.title);
  assert.deepEqual(titles, ["コーヒー", "牛乳"]);
});

test("filterBy paid and category combined (AND condition)", () => {
  const store = buildSampleStore();
  const titles = store
    .filterBy({ paid: false, category: "transport" })
    .map((expense) => expense.title);
  assert.deepEqual(titles, ["バス代"]);
});

test("filterBy on empty store returns empty array", () => {
  const store = new ExpenseStore();
  assert.deepEqual(store.filterBy(), []);
});
