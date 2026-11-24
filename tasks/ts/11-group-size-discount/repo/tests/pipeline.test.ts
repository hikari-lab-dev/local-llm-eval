import assert from "node:assert/strict";
import test from "node:test";
import { FlatOffRule, PercentOffRule } from "../pricing/rules.ts";
import { priceOrder } from "../pricing/pipeline.ts";

test("percent then flat", () => {
  const total = priceOrder(10000, [new PercentOffRule(10), new FlatOffRule(500)]);
  assert.equal(total, 8500);
});

test("flat discount never goes negative", () => {
  const total = priceOrder(300, [new FlatOffRule(1000)]);
  assert.equal(total, 0);
});

test("no rules returns rounded subtotal", () => {
  const total = priceOrder(1999.6, []);
  assert.equal(total, 2000);
});
