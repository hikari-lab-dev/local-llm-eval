/** 全角文字を幅2、それ以外を幅1として扱う簡易的な表示幅計算（既存・変更不要）。 */

function isWideCodePoint(codePoint: number): boolean {
  return (
    (codePoint >= 0x1100 && codePoint <= 0x115f) ||
    (codePoint >= 0x2e80 && codePoint <= 0xa4cf) ||
    (codePoint >= 0xac00 && codePoint <= 0xd7a3) ||
    (codePoint >= 0xf900 && codePoint <= 0xfaff) ||
    (codePoint >= 0xff00 && codePoint <= 0xff60) ||
    (codePoint >= 0xffe0 && codePoint <= 0xffe6)
  );
}

/** 1文字の表示幅（全角=2, それ以外=1）を返す。 */
export function charWidth(char: string): number {
  const codePoint = char.codePointAt(0) ?? 0;
  return isWideCodePoint(codePoint) ? 2 : 1;
}

/** 文字列全体の表示幅を返す。 */
export function displayWidth(text: string): number {
  let width = 0;
  for (const ch of text) {
    width += charWidth(ch);
  }
  return width;
}
