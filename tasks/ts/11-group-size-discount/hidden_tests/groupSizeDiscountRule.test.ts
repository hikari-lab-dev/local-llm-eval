import assert from "node:assert/strict";
import test from "node:test";
import * as groupTiers from "../pricing/groupTiers.ts";
import { GroupSizeDiscountRule } from "../pricing/groupSizeDiscountRule.ts";
import { FlatOffRule } from "../pricing/rules.ts";
import { priceOrder } from "../pricing/pipeline.ts";

const boundaryCases: Array<[number, number]> = [
  [1, 1000],
  [4, 1000],
  [5, 950],
  [9, 950],
  [10, 900],
  [19, 900],
  [20, 850],
  [100, 850],
];

for (const [groupSize, expected] of boundaryCases) {
  test(`tier boundary for groupSize=${groupSize}`, () => {
    const rule = new GroupSizeDiscountRule(groupSize);
    assert.equal(rule.apply(1000), expected);
  });
}

test("chains after flat discount using the running amount", () => {
  const total = priceOrder(10000, [new FlatOffRule(3333), new GroupSizeDiscountRule(20)]);
  assert.equal(total, 5667);
});

test("rounds an exact half-yen tie up", () => {
  const rule = new GroupSizeDiscountRule(5);
  assert.equal(rule.apply(2010), 1910);
});

test("uses the live group tier table, not a value cached at construction", () => {
  const rule = new GroupSizeDiscountRule(5);
  const original = groupTiers.GROUP_TIERS.slice();
  groupTiers.GROUP_TIERS.length = 0;
  groupTiers.GROUP_TIERS.push({ minSize: 1, ratePercent: 0 }, { minSize: 5, ratePercent: 50 });
  try {
    assert.equal(rule.apply(200), 100);
  } finally {
    groupTiers.GROUP_TIERS.length = 0;
    groupTiers.GROUP_TIERS.push(...original);
  }
});
