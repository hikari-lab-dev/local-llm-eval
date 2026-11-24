"""隠しテスト: region/month の違いがキャッシュに正しく反映されることを確認する。"""

from __future__ import annotations

from decimal import Decimal

from reports.summary import monthly_region_report


def test_east_and_west_same_month_differ() -> None:
    east = monthly_region_report(region="east", month="2024-01")
    west = monthly_region_report(region="west", month="2024-01")
    assert (east["total"], west["total"]) == (Decimal(1500), Decimal(600))


def test_same_region_different_month_differ() -> None:
    jan = monthly_region_report(region="east", month="2024-01")
    feb = monthly_region_report(region="east", month="2024-02")
    assert (jan["total"], feb["total"]) == (Decimal(1500), Decimal(700))


def test_many_distinct_calls_all_correct() -> None:
    expected = {
        ("east", "2024-01"): Decimal(1500),
        ("west", "2024-01"): Decimal(600),
        ("east", "2024-02"): Decimal(700),
        ("west", "2024-02"): Decimal(900),
        ("north", "2024-01"): Decimal(50),
    }
    actual = {
        key: monthly_region_report(region=key[0], month=key[1])["total"]
        for key in expected
    }
    assert actual == expected


def test_unknown_region_month_is_zero() -> None:
    report = monthly_region_report(region="south", month="2024-01")
    assert report["total"] == Decimal(0)
