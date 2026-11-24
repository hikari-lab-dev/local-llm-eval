/** ランキング表の組み立て。 */

import type { PlayerScore, RankedEntry } from "./models.ts";
import { roundScore } from "./scoring.ts";
import { charWidth, displayWidth } from "./textWidth.ts";

const ELLIPSIS = "…";
const ELLIPSIS_WIDTH = displayWidth(ELLIPSIS);

export function truncateForDisplay(name: string, maxWidth: number): string {
  if (displayWidth(name) <= maxWidth) {
    return name;
  }
  const budget = maxWidth - ELLIPSIS_WIDTH;
  let result = "";
  let width = 0;
  for (const ch of name) {
    const next = width + charWidth(ch);
    if (next > budget) {
      break;
    }
    result += ch;
    width = next;
  }
  return result + ELLIPSIS;
}

interface ScoredEntry {
  name: string;
  score: number;
}

export function rankPlayers(entries: PlayerScore[], maxNameWidth: number): RankedEntry[] {
  const scored: ScoredEntry[] = entries.map((entry) => ({
    name: entry.name,
    score: roundScore(entry.rawScore, entry.bonusMultiplier),
  }));
  const sorted = scored.sort((a, b) => _compare(a, b));
  return sorted.map((entry, index) => ({
    rank: _competitionRank(sorted, index),
    name: entry.name,
    displayName: truncateForDisplay(entry.name, maxNameWidth),
    score: entry.score,
  }));
}

function _compare(a: ScoredEntry, b: ScoredEntry): number {
  if (a.score !== b.score) {
    return b.score - a.score;
  }
  if (a.name < b.name) {
    return -1;
  }
  if (a.name > b.name) {
    return 1;
  }
  return 0;
}

function _competitionRank(sorted: ScoredEntry[], index: number): number {
  for (let i = index; i >= 0; i--) {
    if (sorted[i].score !== sorted[index].score) {
      return i + 2;
    }
  }
  return 1;
}
