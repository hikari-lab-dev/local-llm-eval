/** ランキングのデータモデル（既存・変更不要）。 */

export interface PlayerScore {
  name: string;
  rawScore: number;
  bonusMultiplier: number;
}

export interface RankedEntry {
  rank: number;
  name: string;
  displayName: string;
  score: number;
}
