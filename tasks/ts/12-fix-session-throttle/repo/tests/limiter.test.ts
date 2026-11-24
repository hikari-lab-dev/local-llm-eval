import assert from "node:assert/strict";
import test from "node:test";
import { RateLimiter } from "../throttle/limiter.ts";
import { resetStore } from "../throttle/store.ts";

test("single user is denied after exhausting capacity", () => {
  resetStore();
  const limiter = new RateLimiter();
  for (let i = 0; i < 5; i++) {
    assert.equal(limiter.allow("alice"), true);
  }
  assert.equal(limiter.allow("alice"), false);
});
