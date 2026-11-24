"""売上レポート生成（リファクタリング対象。意図的にネストの深い実装のまま置いている）。"""

from __future__ import annotations


def generate_report(sales: list[dict]) -> dict:
    """売上データから集計レポートを作る。"""
    total = 0.0
    by_category: dict[str, float] = {}
    count_by_category: dict[str, int] = {}
    top_item = None
    top_amount = 0.0
    for sale in sales:
        if sale.get("amount") is None:
            continue
        amount = sale["amount"]
        if amount <= 0:
            continue
        category = sale.get("category", "unknown")
        total += amount
        if category not in by_category:
            by_category[category] = 0.0
            count_by_category[category] = 0
        by_category[category] += amount
        count_by_category[category] += 1
        if amount > top_amount:
            top_amount = amount
            top_item = sale.get("item", "unknown")
    average_by_category = {}
    for category, category_total in by_category.items():
        average_by_category[category] = category_total / count_by_category[category]
    return {
        "total": total,
        "by_category": by_category,
        "average_by_category": average_by_category,
        "top_item": top_item,
        "top_amount": top_amount,
    }
