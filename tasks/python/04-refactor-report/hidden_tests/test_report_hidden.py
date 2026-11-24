import ast
import re

from report import generate_report


def test_excludes_zero_and_negative_and_none_amount() -> None:
    sales = [
        {"item": "a", "category": "x", "amount": 0},
        {"item": "b", "category": "x", "amount": -5},
        {"item": "c", "category": "x", "amount": None},
        {"item": "d", "category": "x", "amount": 50.0},
    ]
    report = generate_report(sales)
    assert report["total"] == 50.0


def test_top_item_ignores_excluded_records() -> None:
    sales = [
        {"item": "a", "category": "x", "amount": -5},
        {"item": "d", "category": "x", "amount": 50.0},
    ]
    report = generate_report(sales)
    assert report["top_item"] == "d"


def test_missing_category_becomes_unknown() -> None:
    sales = [{"item": "a", "amount": 10.0}]
    report = generate_report(sales)
    assert report["by_category"] == {"unknown": 10.0}


def test_average_by_category() -> None:
    sales = [
        {"item": "a", "category": "x", "amount": 10.0},
        {"item": "b", "category": "x", "amount": 30.0},
    ]
    report = generate_report(sales)
    assert report["average_by_category"] == {"x": 20.0}


def test_empty_sales_returns_defaults() -> None:
    report = generate_report([])
    assert report == {
        "total": 0.0,
        "by_category": {},
        "average_by_category": {},
        "top_item": None,
        "top_amount": 0.0,
    }


def test_no_else_blocks_in_source() -> None:
    with open("report.py", encoding="utf-8") as source_file:
        source = source_file.read()
    assert re.search(r"^\s*else\s*:", source, re.MULTILINE) is None


def test_generate_report_is_split_into_helper_functions() -> None:
    with open("report.py", encoding="utf-8") as source_file:
        tree = ast.parse(source_file.read())
    function_names = [
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    ]
    assert len(function_names) >= 4
