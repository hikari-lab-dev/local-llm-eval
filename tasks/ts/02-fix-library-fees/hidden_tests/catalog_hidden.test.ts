import test from "node:test";
import assert from "node:assert/strict";
import { Catalog } from "../library/catalog.ts";

test("check out with no stock throws", () => {
  const catalog = new Catalog();
  catalog.addCopies("978-3", 1);
  catalog.checkOut("978-3");
  assert.throws(() => catalog.checkOut("978-3"), Error);
});

test("check out with no stock does not change quantity", () => {
  const catalog = new Catalog();
  catalog.addCopies("978-3", 1);
  catalog.checkOut("978-3");
  assert.throws(() => catalog.checkOut("978-3"), Error);
  assert.equal(catalog.availableCopies("978-3"), 0);
});

test("check out on never-stocked isbn throws", () => {
  const catalog = new Catalog();
  assert.throws(() => catalog.checkOut("unknown-isbn"), Error);
});
