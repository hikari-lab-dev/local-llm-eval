import pytest
from inventory.pricing import calculate_total
from inventory.store import Store


def test_remove_stock_insufficient_raises() -> None:
    store = Store()
    store.add_stock("apple", 3)
    with pytest.raises(ValueError):
        store.remove_stock("apple", 5)


def test_remove_stock_insufficient_keeps_quantity() -> None:
    store = Store()
    store.add_stock("apple", 3)
    with pytest.raises(ValueError):
        store.remove_stock("apple", 5)
    assert store.get_quantity("apple") == 3


def test_calculate_total_insufficient_stock_raises() -> None:
    store = Store()
    store.add_stock("apple", 3)
    with pytest.raises(ValueError):
        calculate_total(store, "apple", 100.0, 5)


def test_calculate_total_insufficient_stock_keeps_quantity() -> None:
    store = Store()
    store.add_stock("apple", 3)
    with pytest.raises(ValueError):
        calculate_total(store, "apple", 100.0, 5)
    assert store.get_quantity("apple") == 3


def test_bulk_discount_applies_at_threshold() -> None:
    store = Store()
    store.add_stock("apple", 10)
    assert calculate_total(store, "apple", 100.0, 10) == pytest.approx(900.0)


def test_bulk_discount_applies_above_threshold() -> None:
    store = Store()
    store.add_stock("apple", 20)
    assert calculate_total(store, "apple", 100.0, 20) == pytest.approx(1800.0)


def test_no_discount_below_threshold() -> None:
    store = Store()
    store.add_stock("apple", 9)
    assert calculate_total(store, "apple", 100.0, 9) == pytest.approx(900.0)
