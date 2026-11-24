"""明細の統合ロジック。"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from .categories import CATEGORY_ORDER
from .models import InvalidInvoiceError, InvoiceLine, LineItem
from .normalize import normalize_name


def build_invoice(raw_items: list[LineItem]) -> list[InvoiceLine]:
    """明細行を名寄せ・検証・金額計算・整列した上で返す。"""
    merged = _merge(raw_items)
    _validate(merged)
    lines = [_to_invoice_line(item) for item in merged.values()]
    return sorted(lines, key=_sort_key)


def _merge(raw_items: list[LineItem]) -> dict[tuple[str, str], LineItem]:
    """(category, normalize_name(name)) をキーに、数量を合算した LineItem を作る。"""
    merged: dict[tuple[str, str], LineItem] = {}
    for item in raw_items:
        key = (item.category, normalize_name(item.name))
        existing = merged.get(key)
        if existing is None:
            merged[key] = item
            continue
        merged[key] = LineItem(
            name=existing.name,
            quantity=existing.quantity + item.quantity,
            unit_price=existing.unit_price,
            category=existing.category,
            tax_rate=existing.tax_rate,
        )
    return merged


def _validate(merged: dict[tuple[str, str], LineItem]) -> None:
    """統合後の数量が0以下の商品があれば送出する。"""
    invalid = [item.name for item in merged.values() if item.quantity <= 0]
    if invalid:
        msg = f"quantity <= 0 for: {', '.join(invalid)}"
        raise InvalidInvoiceError(msg)


def _to_invoice_line(item: LineItem) -> InvoiceLine:
    """1商品の金額を計算する。"""
    subtotal = item.unit_price * item.quantity
    tax = (subtotal * item.tax_rate).quantize(Decimal(1), rounding=ROUND_HALF_UP)
    total = subtotal + tax
    return InvoiceLine(
        name=item.name,
        quantity=item.quantity,
        category=item.category,
        subtotal=subtotal,
        tax=tax,
        total=total,
    )


def _category_rank(category: str) -> tuple[int, str]:
    """既知カテゴリは定義順、未知カテゴリはそれより後ろでアルファベット順になる比較キー。"""
    if category in CATEGORY_ORDER:
        return (CATEGORY_ORDER.index(category), "")
    return (len(CATEGORY_ORDER), category)


def _sort_key(line: InvoiceLine) -> tuple[tuple[int, str], str]:
    """カテゴリ順 → 正規化名の昇順、の比較キー。"""
    return (_category_rank(line.category), normalize_name(line.name))
