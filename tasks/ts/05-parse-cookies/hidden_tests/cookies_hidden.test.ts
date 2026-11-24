import test from "node:test";
import assert from "node:assert/strict";
import { parseCookieHeader } from "../cookies.ts";

test("url-decodes values", () => {
  assert.deepEqual(parseCookieHeader("name=hello%20world"), { name: "hello world" });
});

test("trims whitespace around key and value", () => {
  assert.deepEqual(parseCookieHeader("  a = 1 ; b=2"), { a: "1", b: "2" });
});

test("value containing an equals sign keeps the remainder", () => {
  assert.deepEqual(parseCookieHeader("token=abc=def"), { token: "abc=def" });
});

test("segment without equals sign is ignored", () => {
  assert.deepEqual(parseCookieHeader("a=1; invalid; b=2"), { a: "1", b: "2" });
});

test("segment with empty key is ignored", () => {
  assert.deepEqual(parseCookieHeader("=value; a=1"), { a: "1" });
});

test("duplicate key keeps first occurrence", () => {
  assert.deepEqual(parseCookieHeader("a=1; a=2"), { a: "1" });
});

test("trailing semicolon and extra spaces are tolerated", () => {
  assert.deepEqual(parseCookieHeader("a=1; "), { a: "1" });
});

test("only invalid segments returns empty object", () => {
  assert.deepEqual(parseCookieHeader("invalid; =also-invalid"), {});
});
