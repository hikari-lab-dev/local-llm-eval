/** 割引パイプラインの適用。 */

import type { PriceRule } from "./rule.ts";
import { roundYen } from "./roundYen.ts";

/**
 * subtotal に rules を先頭から順番に連鎖適用する。
 * 各ルールの適用結果はそのステップで丸められ、次のルールの入力になる。
 */
export function priceOrder(subtotal: number, rules: PriceRule[]): number {
  let amount = roundYen(subtotal);
  for (const rule of rules) {
    amount = rule.apply(amount);
  }
  return amount;
}
