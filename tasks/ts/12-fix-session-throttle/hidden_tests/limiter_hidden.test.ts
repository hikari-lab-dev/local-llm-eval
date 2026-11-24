import assert from "node:assert/strict";
import test from "node:test";
import { RateLimiter } from "../throttle/limiter.ts";
import { resetStore } from "../throttle/store.ts";

test("a fresh user gets a full independent allowance after another user partially consumed theirs", () => {
  resetStore();
  const limiter = new RateLimiter();
  assert.equal(limiter.allow("alice"), true);
  assert.equal(limiter.allow("alice"), true);
  assert.equal(limiter.allow("alice"), true);

  for (let i = 0; i < 5; i++) {
    assert.equal(limiter.allow("bob"), true, `bob request ${i + 1} should be allowed`);
  }
  assert.equal(limiter.allow("bob"), false);
});

test("three distinct users each get their own 5-request allowance", () => {
  resetStore();
  const limiter = new RateLimiter();
  const users = ["carol", "dave", "erin"];
  for (const user of users) {
    for (let i = 0; i < 5; i++) {
      assert.equal(limiter.allow(user), true, `${user} request ${i + 1} should be allowed`);
    }
    assert.equal(limiter.allow(user), false);
  }
});

test("exhausting one user does not affect a user created earlier but not yet used again", () => {
  resetStore();
  const limiter = new RateLimiter();
  assert.equal(limiter.allow("frank"), true);
  for (let i = 0; i < 5; i++) {
    limiter.allow("gina");
  }
  assert.equal(limiter.allow("frank"), true);
});
