"""レポート表示用の組み立て。"""

from __future__ import annotations

from decimal import Decimal
from typing import TypedDict

from . import aggregate


class RegionReport(TypedDict):
    """1件の地域別レポート。"""

    region: str
    month: str
    total: Decimal


def monthly_region_report(region: str, month: str) -> RegionReport:
    """指定した地域・月の売上レポートを返す。"""
    total = aggregate.region_total(region=region, month=month)
    return {"region": region, "month": month, "total": total}
