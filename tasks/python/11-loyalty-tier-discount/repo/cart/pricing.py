"""割引パイプラインの適用。"""

from __future__ import annotations

from decimal import Decimal

from .discounts import Discount
from .money import round_money


def price_cart(subtotal: Decimal, discounts: list[Discount]) -> Decimal:
    """subtotal に discounts を「先頭から順番に」連鎖適用する。

    各割引の適用結果はそのステップで丸められ、次の割引の入力になる
    （最後にまとめて1回だけ丸めるのではない）。
    """
    amount = round_money(subtotal)
    for discount in discounts:
        amount = discount.apply(amount)
    return amount
