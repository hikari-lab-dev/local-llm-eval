/** 参加人数に応じた団体割引ルール。 */

import type { PriceRule } from "./rule.ts";
import { computeGroupRate } from "./groupTiers.ts";
import { roundYen } from "./roundYen.ts";

export class GroupSizeDiscountRule implements PriceRule {
  groupSize: number;

  constructor(groupSize: number) {
    this.groupSize = groupSize;
  }

  apply(amount: number): number {
    const rate = computeGroupRate(this.groupSize);
    return roundYen(amount * (1 - rate / 100));
  }
}
