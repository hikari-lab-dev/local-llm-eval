import assert from "node:assert/strict";
import test from "node:test";
import { rankPlayers, truncateForDisplay } from "../leaderboard/rank.ts";

test("truncateForDisplay truncates full-width text without exceeding width, budgeting the ellipsis", () => {
  assert.equal(truncateForDisplay("たなかたろう", 6), "たな…");
});

test("truncateForDisplay stops before a wide char that would overflow the budget", () => {
  assert.equal(truncateForDisplay("Bob田中", 5), "Bob…");
});

test("truncateForDisplay returns name unchanged at the exact width boundary", () => {
  assert.equal(truncateForDisplay("たなか", 6), "たなか");
});

test("competition ranking (1224) skips ranks by the tie group size", () => {
  const result = rankPlayers(
    [
      { name: "Bob", rawScore: 100, bonusMultiplier: 1 },
      { name: "Alice", rawScore: 100, bonusMultiplier: 1 },
      { name: "Dave", rawScore: 95, bonusMultiplier: 1 },
      { name: "Charlie", rawScore: 95, bonusMultiplier: 1 },
      { name: "Eve", rawScore: 80, bonusMultiplier: 1 },
    ],
    20,
  );
  const summary = result.map((entry) => [entry.rank, entry.name, entry.score]);
  assert.deepEqual(summary, [
    [1, "Alice", 100],
    [1, "Bob", 100],
    [3, "Charlie", 95],
    [3, "Dave", 95],
    [5, "Eve", 80],
  ]);
});

test("rounds an exact half-point score up before ranking", () => {
  const result = rankPlayers(
    [{ name: "Solo", rawScore: 99.5, bonusMultiplier: 1 }],
    20,
  );
  assert.equal(result[0].score, 100);
});

test("displayName is truncated but ties still use the untruncated name", () => {
  const result = rankPlayers(
    [
      { name: "たなかたろう", rawScore: 50, bonusMultiplier: 1 },
      { name: "Alice", rawScore: 50, bonusMultiplier: 1 },
    ],
    6,
  );
  const names = result.map((entry) => entry.name);
  const displayNames = result.map((entry) => entry.displayName);
  assert.deepEqual(names, ["Alice", "たなかたろう"]);
  assert.deepEqual(displayNames, ["Alice", "たな…"]);
});
