/** ユーザーごとのバケットを保持するストア。 */

import { createBucket, type Bucket } from "./bucket.ts";

const buckets = new Map<string, Bucket>();

/** userId に対応するバケットを返す。無ければ新規作成して保存する。 */
export function getOrCreateBucket(userId: string, capacity: number): Bucket {
  const existing = buckets.get(userId);
  if (existing) {
    return existing;
  }
  const created = createBucket(capacity);
  buckets.set(userId, created);
  return created;
}

/** テスト間で状態を初期化するためのユーティリティ。 */
export function resetStore(): void {
  buckets.clear();
}
