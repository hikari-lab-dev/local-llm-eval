/** 金額を最も近い1円単位に丸める（0.5円は切り上げ）。 */
export function roundYen(amount: number): number {
  return Math.floor(amount + 0.5);
}
