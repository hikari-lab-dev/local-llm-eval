from inventory.pricing import calculate_total
from inventory.store import Store


def test_add_and_get_quantity() -> None:
    store = Store()
    store.add_stock("apple", 5)
    assert store.get_quantity("apple") == 5


def test_remove_stock_within_range() -> None:
    store = Store()
    store.add_stock("apple", 5)
    store.remove_stock("apple", 3)
    assert store.get_quantity("apple") == 2


def test_calculate_total_no_discount() -> None:
    store = Store()
    store.add_stock("apple", 5)
    assert calculate_total(store, "apple", 100.0, 5) == 500.0


def test_calculate_total_reduces_stock() -> None:
    store = Store()
    store.add_stock("apple", 5)
    calculate_total(store, "apple", 100.0, 5)
    assert store.get_quantity("apple") == 0
