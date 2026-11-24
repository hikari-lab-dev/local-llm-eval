import test from "node:test";
import assert from "node:assert/strict";
import { formatDuration } from "../duration.ts";

test("exact minute", () => {
  assert.equal(formatDuration(60), "1m");
});

test("exact hour", () => {
  assert.equal(formatDuration(3600), "1h");
});

test("exact day", () => {
  assert.equal(formatDuration(86400), "1d");
});

test("day with hour minute second, no gaps", () => {
  assert.equal(formatDuration(90061), "1d 1h 1m 1s");
});

test("day and trailing seconds only (middle units omitted)", () => {
  assert.equal(formatDuration(86401), "1d 1s");
});

test("hour and second only (minute omitted)", () => {
  assert.equal(formatDuration(3601), "1h 1s");
});

test("fifty nine seconds does not round to a minute", () => {
  assert.equal(formatDuration(59), "59s");
});

test("multiple days and hours", () => {
  assert.equal(formatDuration(2 * 86400 + 5 * 3600), "2d 5h");
});
