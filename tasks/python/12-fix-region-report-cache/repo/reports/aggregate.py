"""地域・月ごとの売上集計（キャッシュつき）。"""

from __future__ import annotations

from decimal import Decimal

from .cache import memoize
from .data import SALES


@memoize
def region_total(region: str, month: str) -> Decimal:
    """指定した地域・月の売上合計を返す。"""
    total = Decimal(0)
    for row in SALES:
        if row["region"] == region and row["month"] == month:
            total += row["amount"]
    return total
