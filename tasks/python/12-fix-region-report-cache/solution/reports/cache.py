"""簡易メモ化デコレータ。"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def memoize(fn: F) -> F:
    """引数の組み合わせごとに戻り値をキャッシュするデコレータ。"""
    cache: dict[Any, Any] = {}

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = fn(*args, **kwargs)
        return cache[key]

    return wrapper  # type: ignore[return-value]
