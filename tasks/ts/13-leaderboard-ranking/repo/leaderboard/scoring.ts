/** スコア計算（既存・変更不要）。 */

/** 生スコアにボーナス倍率を掛け、四捨五入（0.5は切り上げ）で整数にする。 */
export function roundScore(rawScore: number, bonusMultiplier: number): number {
  return Math.floor(rawScore * bonusMultiplier + 0.5);
}
