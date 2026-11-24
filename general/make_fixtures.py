"""receipts / expenses 課題の入力ファイルと正解を生成する（決定的。再実行しても同じ内容）。"""

from __future__ import annotations

import csv
import io
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "tasks"

RECEIPTS = [
    # 各要素は元ファイル名・本文・正解のリネーム後ファイル名の 3 つ組
    (
        "scan_001.txt",
        "サンプルマート 北町店\nご利用日 2026/9/3 18:22\nおにぎり 2点 ¥300\nお茶 ¥160\n小計 ¥460\n消費税等 ¥36\n合計 ¥496\nお預り ¥1,000\nお釣り ¥504\n",
        "20260903_サンプルマート_496.txt",
    ),
    (
        "IMG_2041.txt",
        "テスト-イレブン 南口店\n令和8年9月5日(土) 07:51\nコーヒーL ¥250\nサンドイッチ ¥398\n合計 ¥648 (税込)\n",
        "20260905_テスト-イレブン_648.txt",
    ),
    (
        "receipt-a.txt",
        "ダミーソン 中央店\n2026-09-07\nお弁当 598円\n小計 598円\n合計 646円\nクレジット 646円\n",
        "20260907_ダミーソン_646.txt",
    ),
    (
        "r4.txt",
        "みほんドラッグ 東口店\n9月10日（2026年）\n目薬 880円\nマスク 2点 1,200円\n小計 2,080円\n割引 -100円\nお会計 1,980円\n",
        "20260910_みほんドラッグ_1980.txt",
    ),
    (
        "scan_002.txt",
        "サンプル衣料 駅前店\n発行日: 2026年9月12日\nTシャツ 1,990円\nソックス 990円\n合計 2,980円（税込）\n",
        "20260912_サンプル衣料_2980.txt",
    ),
    (
        "photo(1).txt",
        "ためし コーヒー 港駅店\n26/09/14 15:03\nラテ Tall ¥495\nスコーン ¥340\nTotal ¥835\n",
        "20260914_ためし コーヒー_835.txt",
    ),
    (
        "doc7.txt",
        "ダミー電器 マルチメディアXYZ店\n令和8年9月20日\nUSBケーブル ¥1,480\nポイント利用 -¥480\nお支払い合計 ¥1,000\n",
        "20260920_ダミー電器_1000.txt",
    ),
    (
        "last.txt",
        "みほんスーパー モール西店\n2026.9.28\n食品 3点 ¥2,360\n合計 ¥2,548\n",
        "20260928_みほんスーパー_2548.txt",
    ),
]

CATEGORIES = ["交通費", "消耗品", "会議費", "通信費", "書籍"]


def make_receipts() -> None:
    base = ROOT / "receipts"
    files = base / "files" / "receipts"
    files.mkdir(parents=True, exist_ok=True)
    for name, body, _ in RECEIPTS:
        (files / name).write_text(body, encoding="utf-8")
    truth = [{"original": n, "renamed": r} for n, _, r in RECEIPTS]
    (base / "truth.json").write_text(
        json.dumps(truth, ensure_ascii=False, indent=1), encoding="utf-8"
    )


def _generate_rows() -> list[dict[str, str]]:
    rng = random.Random(20261003)
    rows: list[dict[str, str]] = []
    for _ in range(48):
        month = rng.choice([7, 8, 9])
        day = rng.randint(1, 28)
        cat = rng.choice(CATEGORIES)
        rows.append(
            {
                "date": f"2026-{month:02d}-{day:02d}",
                "category": cat,
                "item": f"{cat}-{rng.randint(100, 999)}",
                "amount": str(rng.randrange(300, 20000, 10)),
                "tax": rng.choice(["税込", "税込", "税抜"]),
                "memo": "",
            }
        )
    for i in (5, 17, 33):
        rows[i]["memo"] = "取消"
    for i in (8, 21):
        rows.append(dict(rows[i]))
    rows.sort(key=lambda r: (r["date"], r["item"]))
    return rows


def _aggregate(rows: list[dict[str, str]]) -> dict[str, object]:
    seen: set[tuple[str, str, str]] = set()
    by_cat = dict.fromkeys(CATEGORIES, 0)
    by_month: dict[str, int] = {}
    for r in rows:
        key = (r["date"], r["item"], r["amount"])
        if "取消" in r["memo"] or key in seen:
            continue
        seen.add(key)
        amt = int(r["amount"])
        if r["tax"] == "税抜":
            amt = amt * 110 // 100
        by_cat[r["category"]] += amt
        by_month[r["date"][:7]] = by_month.get(r["date"][:7], 0) + amt
    return {
        "by_category": by_cat,
        "total": sum(by_cat.values()),
        "max_month": max(by_month, key=lambda k: by_month[k]),
        "by_month": by_month,
    }


def make_expenses() -> None:
    rows = _generate_rows()
    base = ROOT / "expenses"
    (base / "files").mkdir(parents=True, exist_ok=True)
    with (base / "files" / "expenses.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    truth = _aggregate(rows)
    (base / "truth.json").write_text(
        json.dumps(truth, ensure_ascii=False, indent=1), encoding="utf-8"
    )


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    make_receipts()
    make_expenses()
