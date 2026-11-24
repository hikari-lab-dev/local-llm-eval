/** 貸出処理と延滞料金の計算。 */

import { Catalog } from "./catalog.ts";

export const GRACE_DAYS = 7;
export const LATE_FEE_PER_DAY = 20;
export const LONG_OVERDUE_DAYS = 14;

export function calculateLateFee(daysBorrowed: number): number {
  if (daysBorrowed <= GRACE_DAYS) {
    return 0;
  }
  const overDays = daysBorrowed - GRACE_DAYS;
  let fee = overDays * LATE_FEE_PER_DAY;
  if (daysBorrowed > LONG_OVERDUE_DAYS) {
    fee = fee * 2;
  }
  return fee;
}

export function borrowBook(catalog: Catalog, isbn: string): void {
  catalog.checkOut(isbn);
}
