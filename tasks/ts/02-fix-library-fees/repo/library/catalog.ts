/** 蔵書の在庫管理。 */

export class Catalog {
  private copies: Map<string, number> = new Map();

  addCopies(isbn: string, count: number): void {
    this.copies.set(isbn, (this.copies.get(isbn) ?? 0) + count);
  }

  availableCopies(isbn: string): number {
    return this.copies.get(isbn) ?? 0;
  }

  checkOut(isbn: string): void {
    const current = this.availableCopies(isbn);
    this.copies.set(isbn, current - 1);
  }

  checkIn(isbn: string): void {
    this.copies.set(isbn, this.availableCopies(isbn) + 1);
  }
}
