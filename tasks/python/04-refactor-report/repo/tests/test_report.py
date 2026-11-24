from report import generate_report


def test_basic_report() -> None:
    sales = [
        {"item": "pen", "category": "stationery", "amount": 100.0},
        {"item": "notebook", "category": "stationery", "amount": 200.0},
        {"item": "coffee", "category": "drink", "amount": 300.0},
    ]
    report = generate_report(sales)
    assert report == {
        "total": 600.0,
        "by_category": {"stationery": 300.0, "drink": 300.0},
        "average_by_category": {"stationery": 150.0, "drink": 300.0},
        "top_item": "coffee",
        "top_amount": 300.0,
    }
