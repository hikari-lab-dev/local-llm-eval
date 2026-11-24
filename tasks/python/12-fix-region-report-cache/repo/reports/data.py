"""生の売上データ（サンプル）。"""

from __future__ import annotations

from decimal import Decimal
from typing import TypedDict


class SalesRow(TypedDict):
    """1件の売上レコード。"""

    region: str
    # month は "YYYY-MM" 形式の文字列。
    month: str
    amount: Decimal


SALES: list[SalesRow] = [
    {"region": "east", "month": "2024-01", "amount": Decimal(1000)},
    {"region": "east", "month": "2024-01", "amount": Decimal(500)},
    {"region": "east", "month": "2024-02", "amount": Decimal(700)},
    {"region": "west", "month": "2024-01", "amount": Decimal(300)},
    {"region": "west", "month": "2024-01", "amount": Decimal(300)},
    {"region": "west", "month": "2024-02", "amount": Decimal(900)},
    {"region": "north", "month": "2024-01", "amount": Decimal(50)},
]
