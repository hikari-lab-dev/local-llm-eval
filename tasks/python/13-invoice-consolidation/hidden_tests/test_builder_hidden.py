"""隠しテスト: 名寄せ・atomic 検証・丸め・整列の境界値。"""

from __future__ import annotations

from decimal import Decimal

import pytest
from invoice.builder import build_invoice
from invoice.models import InvalidInvoiceError, LineItem


def _item(name: str, quantity: int, unit_price: int, **overrides: str) -> LineItem:
    category = overrides.get("category", "food")
    tax_rate = overrides.get("tax_rate", "0.08")
    return LineItem(
        name=name,
        quantity=quantity,
        unit_price=Decimal(unit_price),
        category=category,
        tax_rate=Decimal(tax_rate),
    )


def test_merge_uses_first_seen_display_name_and_sums_quantity() -> None:
    items = [
        _item("ｺｰﾋｰ豆", 3, 500),
        _item("コーヒー豆", 2, 500),
    ]
    result = build_invoice(items)
    actual = (len(result), result[0].name, result[0].quantity)
    assert actual == (1, "ｺｰﾋｰ豆", 5)


def test_negative_merged_quantity_rejects_whole_invoice_atomically() -> None:
    items = [
        _item("牛乳", 5, 200),
        _item("キャンセル対象", 2, 1000, category="daily"),
        _item("キャンセル対象", -3, 1000, category="daily"),
    ]
    snapshot = list(items)
    with pytest.raises(InvalidInvoiceError):
        build_invoice(items)
    assert items == snapshot


def test_zero_merged_quantity_is_also_invalid() -> None:
    items = [
        _item("相殺品", 4, 100, category="daily"),
        _item("相殺品", -4, 100, category="daily"),
    ]
    with pytest.raises(InvalidInvoiceError):
        build_invoice(items)


def test_tax_rounding_uses_half_up_on_exact_half_yen() -> None:
    items = [_item("消しゴム", 1, 125, category="daily", tax_rate="0.10")]
    line = build_invoice(items)[0]
    assert (line.tax, line.total) == (Decimal(13), Decimal(138))


def test_sort_order_across_known_and_unknown_categories() -> None:
    items = [
        _item("Zebra照明", 1, 1000, category="electronics"),
        _item("art品", 1, 1000, category="art"),
        _item("apple味ガム", 1, 100, category="electronics"),
        _item("その他品", 1, 100, category="other"),
        _item("toys品", 1, 100, category="toys"),
        _item("米", 1, 100, category="food"),
        _item("洗剤", 1, 100, category="daily"),
    ]
    result = build_invoice(items)
    actual = (
        [line.category for line in result],
        [line.name for line in result if line.category == "electronics"],
    )
    assert actual == (
        ["food", "daily", "electronics", "electronics", "other", "art", "toys"],
        ["apple味ガム", "Zebra照明"],
    )
