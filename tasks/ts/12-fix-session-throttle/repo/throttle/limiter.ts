/** ユーザーごとのリクエスト制限。 */

import { getOrCreateBucket } from "./store.ts";

const CAPACITY = 5;

export class RateLimiter {
  allow(userId: string): boolean {
    const bucket = getOrCreateBucket(userId, CAPACITY);
    if (bucket.tokens <= 0) {
      return false;
    }
    bucket.tokens -= 1;
    return true;
  }
}
