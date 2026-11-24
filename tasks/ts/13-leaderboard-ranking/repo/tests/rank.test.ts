import assert from "node:assert/strict";
import test from "node:test";
import { rankPlayers, truncateForDisplay } from "../leaderboard/rank.ts";

test("truncateForDisplay returns unchanged when it fits", () => {
  assert.equal(truncateForDisplay("Alice", 10), "Alice");
});

test("rankPlayers orders by score descending with no ties", () => {
  const result = rankPlayers(
    [
      { name: "Alice", rawScore: 90, bonusMultiplier: 1 },
      { name: "Bob", rawScore: 70, bonusMultiplier: 1 },
      { name: "Carol", rawScore: 80, bonusMultiplier: 1 },
    ],
    20,
  );
  const summary = result.map((entry) => [entry.rank, entry.name, entry.score]);
  assert.deepEqual(summary, [
    [1, "Alice", 90],
    [2, "Carol", 80],
    [3, "Bob", 70],
  ]);
});
