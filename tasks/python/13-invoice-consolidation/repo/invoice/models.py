"""請求書のデータモデル（既存・変更不要）。"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LineItem:
    """統合前の1明細行。"""

    name: str
    quantity: int
    unit_price: Decimal
    category: str
    tax_rate: Decimal


@dataclass(frozen=True)
class InvoiceLine:
    """統合後の出力用1行。"""

    name: str
    quantity: int
    category: str
    subtotal: Decimal
    tax: Decimal
    total: Decimal


class InvalidInvoiceError(Exception):
    """統合後の数量が0以下になるなど、請求書として不正な状態を表す。"""
