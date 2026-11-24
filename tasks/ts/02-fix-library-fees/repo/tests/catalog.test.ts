import test from "node:test";
import assert from "node:assert/strict";
import { Catalog } from "../library/catalog.ts";

test("add and check available copies", () => {
  const catalog = new Catalog();
  catalog.addCopies("978-1", 3);
  assert.equal(catalog.availableCopies("978-1"), 3);
});

test("check out reduces available copies", () => {
  const catalog = new Catalog();
  catalog.addCopies("978-1", 2);
  catalog.checkOut("978-1");
  assert.equal(catalog.availableCopies("978-1"), 1);
});

test("check in increases available copies", () => {
  const catalog = new Catalog();
  catalog.addCopies("978-1", 1);
  catalog.checkOut("978-1");
  catalog.checkIn("978-1");
  assert.equal(catalog.availableCopies("978-1"), 1);
});
