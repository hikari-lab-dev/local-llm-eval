from intervals import merge_intervals


def test_adjacent_merge() -> None:
    assert merge_intervals([(1, 3), (3, 5)]) == [(1, 5)]


def test_unsorted_input() -> None:
    assert merge_intervals([(5, 6), (1, 2), (3, 4)]) == [(1, 2), (3, 4), (5, 6)]


def test_contained_interval() -> None:
    assert merge_intervals([(1, 10), (2, 5)]) == [(1, 10)]


def test_multiple_merges_chain() -> None:
    assert merge_intervals([(1, 4), (2, 6), (5, 8), (10, 12)]) == [(1, 8), (10, 12)]


def test_single_interval() -> None:
    assert merge_intervals([(3, 3)]) == [(3, 3)]
