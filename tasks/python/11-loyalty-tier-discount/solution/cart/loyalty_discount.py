"""ロイヤルティティアに応じた割引。"""

from __future__ import annotations

from decimal import Decimal

from .discounts import Discount
from .loyalty import compute_tier
from .money import round_money


class LoyaltyTierDiscount(Discount):
    """顧客の累計購入額から求めたティア割引率を適用する。"""

    def __init__(self, lifetime_spend: Decimal) -> None:
        self.lifetime_spend = lifetime_spend

    def apply(self, amount: Decimal) -> Decimal:
        _tier_name, rate = compute_tier(self.lifetime_spend)
        discounted = amount * (Decimal(1) - rate / Decimal(100))
        return round_money(discounted)
