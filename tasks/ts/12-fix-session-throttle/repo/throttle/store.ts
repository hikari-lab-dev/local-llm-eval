/** ユーザーごとのバケットを保持するストア。 */

import { createBucket, type Bucket } from "./bucket.ts";

const buckets = new Map<string, Bucket>();
const sharedDefault = createBucket(5);

/** userId に対応するバケットを返す。無ければ新規作成して保存する。 */
export function getOrCreateBucket(userId: string, capacity: number): Bucket {
  const existing = buckets.get(userId);
  if (existing) {
    return existing;
  }
  buckets.set(userId, sharedDefault);
  return sharedDefault;
}

/** テスト間で状態を初期化するためのユーティリティ。 */
export function resetStore(): void {
  buckets.clear();
}
