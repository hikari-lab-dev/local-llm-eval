"""既存の回帰テスト（変更禁止）。"""

from __future__ import annotations

from decimal import Decimal

from reports.summary import monthly_region_report


def test_east_january_total() -> None:
    report = monthly_region_report(region="east", month="2024-01")
    assert report["total"] == Decimal(1500)


def test_repeated_call_is_stable() -> None:
    first = monthly_region_report(region="east", month="2024-01")
    second = monthly_region_report(region="east", month="2024-01")
    assert first == second
