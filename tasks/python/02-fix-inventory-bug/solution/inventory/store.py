"""在庫管理。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Store:
    """商品ごとの在庫数を保持する。"""

    stock: dict[str, int] = field(default_factory=dict)

    def add_stock(self, item: str, quantity: int) -> None:
        """在庫を増やす。"""
        self.stock[item] = self.stock.get(item, 0) + quantity

    def remove_stock(self, item: str, quantity: int) -> None:
        """在庫を減らす。在庫不足の場合は ValueError を送出し在庫を変更しない。"""
        current = self.stock.get(item, 0)
        if quantity > current:
            raise ValueError(f"在庫不足です: {item} (在庫 {current}, 要求 {quantity})")
        self.stock[item] = current - quantity

    def get_quantity(self, item: str) -> int:
        """在庫数を返す。"""
        return self.stock.get(item, 0)
