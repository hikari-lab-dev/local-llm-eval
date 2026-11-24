/** Cookie ヘッダーのパース処理。 */

/**
 * HTTP の Cookie ヘッダー文字列をパースする。
 *
 * @param header - `"a=1; b=2"` のような Cookie ヘッダー文字列。
 * @returns キーと値の組をまとめたオブジェクト。
 */
export function parseCookieHeader(header: string): Record<string, string> {
  const result: Record<string, string> = {};
  const segments = header.split(";");
  for (const segment of segments) {
    const separatorIndex = segment.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }
    const key = segment.slice(0, separatorIndex).trim();
    if (key.length === 0) {
      continue;
    }
    if (Object.hasOwn(result, key)) {
      continue;
    }
    const rawValue = segment.slice(separatorIndex + 1).trim();
    result[key] = decodeURIComponent(rawValue);
  }
  return result;
}
