/** 経過時間のフォーマット処理。 */

/**
 * 秒数を `Xd Xh Xm Xs` 形式の文字列に変換する。
 *
 * @param totalSeconds - 0以上の整数（秒）。
 * @returns 値が0の要素を省略した文字列。全体が0の場合は "0s"。
 */
export function formatDuration(totalSeconds: number): string {
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const parts: string[] = [];
  if (days > 0) {
    parts.push(`${days}d`);
  }
  if (hours > 0) {
    parts.push(`${hours}h`);
  }
  if (minutes > 0) {
    parts.push(`${minutes}m`);
  }
  if (seconds > 0 || parts.length === 0) {
    parts.push(`${seconds}s`);
  }
  return parts.join(" ");
}
