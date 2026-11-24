"""既存の割引パイプラインの回帰テスト（変更禁止）。"""

from __future__ import annotations

from decimal import Decimal

from cart.discounts import FixedAmountDiscount, PercentageDiscount
from cart.pricing import price_cart


def test_percentage_then_fixed() -> None:
    total = price_cart(
        Decimal("1000.00"),
        [PercentageDiscount(Decimal(10)), FixedAmountDiscount(Decimal(50))],
    )
    assert total == Decimal("850.00")


def test_fixed_discount_never_negative() -> None:
    total = price_cart(Decimal("30.00"), [FixedAmountDiscount(Decimal(100))])
    assert total == Decimal("0.00")


def test_no_discounts_returns_rounded_subtotal() -> None:
    total = price_cart(Decimal("19.999"), [])
    assert total == Decimal("20.00")
