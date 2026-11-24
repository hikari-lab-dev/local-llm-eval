from intervals import merge_intervals


def test_no_overlap() -> None:
    assert merge_intervals([(1, 2), (4, 5)]) == [(1, 2), (4, 5)]


def test_simple_overlap() -> None:
    assert merge_intervals([(1, 3), (2, 5)]) == [(1, 5)]


def test_empty() -> None:
    assert merge_intervals([]) == []
