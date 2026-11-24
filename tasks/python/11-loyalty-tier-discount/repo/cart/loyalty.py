"""顧客のロイヤルティティア判定。"""

from __future__ import annotations

from decimal import Decimal

# (しきい値, ティア名, 割引率%) の昇順リスト。
# 累計購入額がしきい値「以上」ならそのティアに該当する（境界値はそのティア側）。
TIER_TABLE: list[tuple[Decimal, str, Decimal]] = [
    (Decimal(0), "bronze", Decimal(0)),
    (Decimal(50000), "silver", Decimal(3)),
    (Decimal(200000), "gold", Decimal(5)),
    (Decimal(500000), "platinum", Decimal(8)),
]


def compute_tier(lifetime_spend: Decimal) -> tuple[str, Decimal]:
    """累計購入額からティア名と割引率(%)のタプルを返す。

    しきい値ちょうどの金額は上位ティア側に含める（例: 50000 は bronze ではなく silver）。
    """
    for threshold, name, rate in reversed(TIER_TABLE):
        if lifetime_spend >= threshold:
            return name, rate
    return TIER_TABLE[0][1], TIER_TABLE[0][2]
