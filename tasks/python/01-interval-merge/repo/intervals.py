"""区間のマージ処理。"""

from __future__ import annotations


def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """重なる区間・隣接する区間を1つに結合する。

    Args:
        intervals: (start, end) のタプルのリスト（開始順は不定）。

    Returns:
        開始位置の昇順でソートされ、重なり・隣接がすべて結合された区間のリスト。
    """
    raise NotImplementedError
