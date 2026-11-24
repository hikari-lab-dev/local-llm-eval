import test from "node:test";
import assert from "node:assert/strict";
import { formatDuration } from "../duration.ts";

test("zero seconds", () => {
  assert.equal(formatDuration(0), "0s");
});

test("seconds only", () => {
  assert.equal(formatDuration(45), "45s");
});

test("minutes and seconds", () => {
  assert.equal(formatDuration(90), "1m 30s");
});

test("hours minutes seconds", () => {
  assert.equal(formatDuration(3661), "1h 1m 1s");
});
