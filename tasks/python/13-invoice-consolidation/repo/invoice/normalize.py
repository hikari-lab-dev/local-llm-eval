"""商品名の正規化（既存・変更不要）。"""

from __future__ import annotations

import unicodedata


def normalize_name(name: str) -> str:
    """全角/半角・大文字小文字・前後空白の違いを吸収した比較キーを返す。

    NFKC 正規化（全角英数・半角カナなどの互換分解）→ casefold（大文字小文字を無視する
    比較用の変換）→ 前後の空白除去、の順で適用する。表示用の元の文字列はこの関数の
    戻り値ではなく、呼び出し側が別途保持すること。
    """
    return unicodedata.normalize("NFKC", name).casefold().strip()
