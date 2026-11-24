"""割引の抽象基底クラスと既存の具象実装。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from .money import round_money


class Discount(ABC):
    """割引の共通インターフェース。

    ``apply`` は「その時点までの累積金額」を受け取り、丸め済みの新しい金額を返す。
    ``price_cart`` はこのメソッドを割引リストの順に連鎖呼び出しする
    （各ステップの結果が次のステップの入力になる）。実装は必ず
    ``money.round_money`` で丸めてから返すこと（丸め方式をパイプライン全体で統一するため）。
    """

    @abstractmethod
    def apply(self, amount: Decimal) -> Decimal:
        """amount に割引を適用した、丸め済みの新しい金額を返す。"""
        raise NotImplementedError


class PercentageDiscount(Discount):
    """定率割引。"""

    def __init__(self, percent: Decimal) -> None:
        self.percent = percent

    def apply(self, amount: Decimal) -> Decimal:
        discounted = amount * (Decimal(1) - self.percent / Decimal(100))
        return round_money(discounted)


class FixedAmountDiscount(Discount):
    """定額割引（マイナスにはならない）。"""

    def __init__(self, amount_off: Decimal) -> None:
        self.amount_off = amount_off

    def apply(self, amount: Decimal) -> Decimal:
        result = amount - self.amount_off
        result = max(result, Decimal(0))
        return round_money(result)
