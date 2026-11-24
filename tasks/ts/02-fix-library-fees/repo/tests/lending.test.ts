import test from "node:test";
import assert from "node:assert/strict";
import { Catalog } from "../library/catalog.ts";
import { calculateLateFee, borrowBook } from "../library/lending.ts";

test("no fee within grace period", () => {
  assert.equal(calculateLateFee(5), 0);
});

test("basic fee just over grace period", () => {
  assert.equal(calculateLateFee(8), 20);
});

test("borrowBook checks out a copy", () => {
  const catalog = new Catalog();
  catalog.addCopies("978-2", 1);
  borrowBook(catalog, "978-2");
  assert.equal(catalog.availableCopies("978-2"), 0);
});
