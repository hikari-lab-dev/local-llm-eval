"""区間のマージ処理。"""

from __future__ import annotations


def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """重なる区間・隣接する区間を1つに結合する。

    Args:
        intervals: (start, end) のタプルのリスト（開始順は不定）。

    Returns:
        開始位置の昇順でソートされ、重なり・隣接がすべて結合された区間のリスト。
    """
    if not intervals:
        return []
    ordered = sorted(intervals)
    merged: list[tuple[int, int]] = [ordered[0]]
    for start, end in ordered[1:]:
        last_start, last_end = merged[-1]
        if start > last_end:
            merged.append((start, end))
            continue
        merged[-1] = (last_start, max(last_end, end))
    return merged
