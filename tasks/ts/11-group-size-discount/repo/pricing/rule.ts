/** 割引ルールの共通インターフェース。 */
export interface PriceRule {
  apply(amount: number): number;
}
