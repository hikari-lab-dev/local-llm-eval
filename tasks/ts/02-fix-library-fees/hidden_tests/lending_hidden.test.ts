import test from "node:test";
import assert from "node:assert/strict";
import { Catalog } from "../library/catalog.ts";
import { calculateLateFee, borrowBook } from "../library/lending.ts";

test("no fee exactly at grace boundary", () => {
  assert.equal(calculateLateFee(7), 0);
});

test("fee not doubled just below long-overdue threshold", () => {
  // overDays = 13 - 7 = 6, fee = 6 * 20 = 120 (not doubled)
  assert.equal(calculateLateFee(13), 120);
});

test("fee doubled exactly at long-overdue threshold (14 days)", () => {
  // overDays = 14 - 7 = 7, fee = 7 * 20 * 2 = 280
  assert.equal(calculateLateFee(14), 280);
});

test("fee doubled above long-overdue threshold", () => {
  // overDays = 20 - 7 = 13, fee = 13 * 20 * 2 = 520
  assert.equal(calculateLateFee(20), 520);
});

test("borrowBook propagates out-of-stock error and keeps catalog unchanged", () => {
  const catalog = new Catalog();
  catalog.addCopies("978-4", 1);
  borrowBook(catalog, "978-4");
  assert.throws(() => borrowBook(catalog, "978-4"), Error);
  assert.equal(catalog.availableCopies("978-4"), 0);
});
