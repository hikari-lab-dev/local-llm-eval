"""売上レポート生成。"""

from __future__ import annotations


def generate_report(sales: list[dict]) -> dict:
    """売上データから集計レポートを作る。"""
    valid_sales = [sale for sale in sales if _is_valid_amount(sale)]
    total = sum(sale["amount"] for sale in valid_sales)
    by_category = _sum_by_category(valid_sales)
    counts = _count_by_category(valid_sales)
    average_by_category = _average_by_category(by_category, counts)
    top_item, top_amount = _find_top(valid_sales)
    return {
        "total": total,
        "by_category": by_category,
        "average_by_category": average_by_category,
        "top_item": top_item,
        "top_amount": top_amount,
    }


def _is_valid_amount(sale: dict) -> bool:
    """集計対象となる金額を持つレコードかどうかを判定する。"""
    amount = sale.get("amount")
    if amount is None:
        return False
    return amount > 0


def _category_of(sale: dict) -> str:
    """レコードからカテゴリ名を取り出す（未指定は unknown）。"""
    return sale.get("category", "unknown")


def _sum_by_category(sales: list[dict]) -> dict[str, float]:
    """カテゴリごとの金額合計を返す。"""
    totals: dict[str, float] = {}
    for sale in sales:
        category = _category_of(sale)
        totals[category] = totals.get(category, 0.0) + sale["amount"]
    return totals


def _count_by_category(sales: list[dict]) -> dict[str, int]:
    """カテゴリごとの件数を返す。"""
    counts: dict[str, int] = {}
    for sale in sales:
        category = _category_of(sale)
        counts[category] = counts.get(category, 0) + 1
    return counts


def _average_by_category(
    totals: dict[str, float], counts: dict[str, int]
) -> dict[str, float]:
    """カテゴリごとの平均金額を返す。"""
    return {category: totals[category] / counts[category] for category in totals}


def _find_top(sales: list[dict]) -> tuple[str | None, float]:
    """最も金額の大きいレコードの item と amount を返す。"""
    if not sales:
        return None, 0.0
    top_sale = max(sales, key=lambda sale: sale["amount"])
    return top_sale.get("item", "unknown"), top_sale["amount"]
