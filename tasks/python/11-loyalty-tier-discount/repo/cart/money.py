"""金額の丸めユーティリティ。"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def round_money(amount: Decimal) -> Decimal:
    """金額を「四捨五入（0.5は切り上げ）」で小数点以下2桁に丸める。

    パイプライン全体でこの関数を通した丸めに統一すること
    （Python 標準の ``round()`` は銀行丸め（偶数丸め）なので使わない）。
    """
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)
