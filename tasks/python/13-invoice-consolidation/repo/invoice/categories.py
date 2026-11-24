"""カテゴリの表示順（既存・変更不要）。"""

from __future__ import annotations

# この順番で明細を並べる。ここに無いカテゴリ名は、この一覧に載っているどのカテゴリより
# 後ろに（カテゴリ名の昇順で）並べる。
CATEGORY_ORDER: list[str] = ["food", "daily", "electronics", "other"]
