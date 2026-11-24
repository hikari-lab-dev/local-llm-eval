/** トークンバケットのデータ構造（既存・変更不要）。 */

export interface Bucket {
  tokens: number;
  lastRefillMs: number;
}

export function createBucket(capacity: number): Bucket {
  return { tokens: capacity, lastRefillMs: 0 };
}
