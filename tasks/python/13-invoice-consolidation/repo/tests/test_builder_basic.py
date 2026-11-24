"""既存の回帰テスト（変更禁止）。基本的なハッピーパスのみを検証する。"""

from __future__ import annotations

from decimal import Decimal

from invoice.builder import build_invoice
from invoice.models import LineItem

_ITEMS = [
    LineItem(
        name="ノートPC",
        quantity=1,
        unit_price=Decimal(100000),
        category="electronics",
        tax_rate=Decimal("0.10"),
    ),
    LineItem(
        name="お米",
        quantity=2,
        unit_price=Decimal(1000),
        category="food",
        tax_rate=Decimal("0.08"),
    ),
]


def test_sorted_by_category_order() -> None:
    result = build_invoice(_ITEMS)
    assert [line.name for line in result] == ["お米", "ノートPC"]


def test_line_amounts() -> None:
    rice = build_invoice(_ITEMS)[0]
    actual = (rice.quantity, rice.subtotal, rice.tax, rice.total)
    assert actual == (2, Decimal(2000), Decimal(160), Decimal(2160))
