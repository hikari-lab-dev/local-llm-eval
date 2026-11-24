"""隠しテスト: LoyaltyTierDiscount の境界値・パイプライン連鎖・動的参照。"""

from __future__ import annotations

from decimal import Decimal

import pytest
from cart import loyalty
from cart.discounts import FixedAmountDiscount
from cart.loyalty_discount import LoyaltyTierDiscount
from cart.pricing import price_cart


@pytest.mark.parametrize(
    ("lifetime_spend", "expected"),
    [
        (Decimal(0), Decimal("1000.00")),
        (Decimal("49999.99"), Decimal("1000.00")),
        (Decimal(50000), Decimal("970.00")),
        (Decimal("199999.99"), Decimal("970.00")),
        (Decimal(200000), Decimal("950.00")),
        (Decimal("499999.99"), Decimal("950.00")),
        (Decimal(500000), Decimal("920.00")),
        (Decimal(1000000), Decimal("920.00")),
    ],
)
def test_tier_boundaries(lifetime_spend: Decimal, expected: Decimal) -> None:
    discount = LoyaltyTierDiscount(lifetime_spend)
    assert discount.apply(Decimal("1000.00")) == expected


def test_chains_after_fixed_discount_using_running_amount() -> None:
    total = price_cart(
        Decimal("1000.00"),
        [FixedAmountDiscount(Decimal("333.33")), LoyaltyTierDiscount(Decimal(500000))],
    )
    assert total == Decimal("613.34")


def test_uses_round_half_up_not_bankers_rounding() -> None:
    discount = LoyaltyTierDiscount(Decimal(0))
    assert discount.apply(Decimal("10.005")) == Decimal("10.01")


def test_uses_live_tier_table_not_cached_at_init(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    discount = LoyaltyTierDiscount(Decimal(1000))
    monkeypatch.setattr(
        loyalty,
        "TIER_TABLE",
        [
            (Decimal(0), "bronze", Decimal(0)),
            (Decimal(1000), "vip", Decimal(50)),
        ],
    )
    assert discount.apply(Decimal("200.00")) == Decimal("100.00")


def test_uses_live_tier_table_not_hardcoded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        loyalty,
        "TIER_TABLE",
        [(Decimal(0), "bronze", Decimal(0))],
    )
    discount = LoyaltyTierDiscount(Decimal(999999999))
    assert discount.apply(Decimal("1000.00")) == Decimal("1000.00")
