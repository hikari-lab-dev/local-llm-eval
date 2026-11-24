"""簡易設定ファイルパーサー。"""

from __future__ import annotations


def parse_config(text: str) -> dict[str, dict[str, object]]:
    """簡易INI風の設定テキストをパースする。

    Args:
        text: 設定ファイルの内容全体。

    Returns:
        セクション名をキーとし、値は key: 変換後の値 の辞書を持つ辞書。
    """
    raise NotImplementedError
