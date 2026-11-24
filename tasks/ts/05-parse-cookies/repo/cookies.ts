/** Cookie ヘッダーのパース処理。 */

/**
 * HTTP の Cookie ヘッダー文字列をパースする。
 *
 * @param header - `"a=1; b=2"` のような Cookie ヘッダー文字列。
 * @returns キーと値の組をまとめたオブジェクト。
 */
export function parseCookieHeader(header: string): Record<string, string> {
  throw new Error("not implemented");
}
