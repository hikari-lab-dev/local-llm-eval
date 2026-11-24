import test from "node:test";
import assert from "node:assert/strict";
import { parseCookieHeader } from "../cookies.ts";

test("parses multiple pairs", () => {
  assert.deepEqual(parseCookieHeader("a=1; b=2"), { a: "1", b: "2" });
});

test("parses single pair", () => {
  assert.deepEqual(parseCookieHeader("session=abc123"), { session: "abc123" });
});

test("empty string returns empty object", () => {
  assert.deepEqual(parseCookieHeader(""), {});
});
