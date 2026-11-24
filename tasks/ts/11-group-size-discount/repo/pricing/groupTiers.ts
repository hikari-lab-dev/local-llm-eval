/** 団体割引の人数しきい値テーブル。 */

export interface GroupTier {
  minSize: number;
  ratePercent: number;
}

export const GROUP_TIERS: GroupTier[] = [
  { minSize: 1, ratePercent: 0 },
  { minSize: 5, ratePercent: 5 },
  { minSize: 10, ratePercent: 10 },
  { minSize: 20, ratePercent: 15 },
];

/** 人数からしきい値「以上」で該当する割引率(%)を返す。 */
export function computeGroupRate(groupSize: number): number {
  let rate = GROUP_TIERS[0].ratePercent;
  for (const tier of GROUP_TIERS) {
    if (groupSize >= tier.minSize) {
      rate = tier.ratePercent;
    }
  }
  return rate;
}
