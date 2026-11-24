"""価格計算（数量割引）。"""

from __future__ import annotations

from inventory.store import Store

BULK_DISCOUNT_THRESHOLD = 10
BULK_DISCOUNT_RATE = 0.1


def calculate_total(store: Store, item: str, unit_price: float, quantity: int) -> float:
    """指定数量ぶんを注文し、在庫を減らして割引後の合計金額を返す。"""
    store.remove_stock(item, quantity)
    subtotal = unit_price * quantity
    if quantity > BULK_DISCOUNT_THRESHOLD:
        return subtotal * (1 - BULK_DISCOUNT_RATE)
    return subtotal
