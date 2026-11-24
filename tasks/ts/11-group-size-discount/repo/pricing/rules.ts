/** 既存の割引ルール実装。 */

import type { PriceRule } from "./rule.ts";
import { roundYen } from "./roundYen.ts";

export class PercentOffRule implements PriceRule {
  percent: number;

  constructor(percent: number) {
    this.percent = percent;
  }

  apply(amount: number): number {
    return roundYen(amount * (1 - this.percent / 100));
  }
}

export class FlatOffRule implements PriceRule {
  amountOff: number;

  constructor(amountOff: number) {
    this.amountOff = amountOff;
  }

  apply(amount: number): number {
    const result = amount - this.amountOff;
    return roundYen(Math.max(result, 0));
  }
}
