"""難しめの汎用課題（長文議事録・入金消込・メモ整理）の入力と正解を生成する（決定的）。"""

from __future__ import annotations

import csv
import io
import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "tasks"

FILLER_TOPICS = {
    "発声練習": [
        "発声練習の時間を 10 分から 15 分に延ばしてはどうかという意見が出た。",
        "腹式呼吸の確認を毎回入れることにした。",
    ],
    "パート報告": [
        "ソプラノは高音部の音程が安定してきたと報告があった。",
        "テノールの人数が少ないので、当面はバリトンの 2 名が応援に入る。",
    ],
    "広報": [
        "SNS の投稿は月 2 回を目安にする。",
        "チラシの配布先として近隣の図書館を追加する案が出た。",
    ],
    "衣装": [
        "衣装の色は黒で統一する方向で検討を続ける。",
        "古い衣装の処分は次回以降に持ち越しとなった。",
    ],
    "連絡事項": [
        "欠席連絡は前日までにグループに書き込むよう再確認した。",
        "楽譜のコピーは各自で行うこととした。",
    ],
    "練習内容": [
        "次回は第 2 曲の後半を中心に練習する。",
        "暗譜の目標時期について意見交換をした。",
    ],
}
MEMBERS = ["佐藤", "田中", "鈴木", "高橋", "伊藤", "山本", "中村", "小林"]

# 回次ごとに差し込む事実。答えはこの並びから決まる。
PLANTED = {
    3: "【会費】田中さんから月額会費を 3,000 円から 3,500 円に上げる提案があったが、今回は保留とした。",
    4: "【楽譜購入】混声合唱曲集 12,000 円の購入を承認した。",
    5: "【練習場所】常設の練習場所を公民館から市民会館 第2練習室へ移すことを決定した。",
    6: "【入団】見学者 2 名の入団を承認した。",
    8: "【演奏会】演奏会の日程は 2026 年 11 月 22 日で仮押さえとした。",
    9: "【会費】前回保留の件を再審議し、田中さんの提案どおり月額会費を 3,500 円にすることを決定した。",
    11: "【楽譜購入】参考用 CD 8,000 円の購入案は否決した。",
    13: "【入団】1 名の入団を承認した。",
    14: "【練習場所】市民会館の改修のため、常設の練習場所を中央公民館 大会議室へ移すことを決定した。",
    16: "【楽譜購入】パート練習用の楽譜 5,500 円の購入を承認した。",
    18: "【演奏会】ホールの都合により、仮押さえを 2026 年 11 月 29 日に変更した。",
    19: "【入団】大学生 3 名の入団を承認した。",
    20: "【練習場所】小学校の音楽室を常設の練習場所にする案が出たが、見送りとなった。",
    22: "【会費】佐藤さんから会費を 4,000 円にする提案があったが、採決の結果否決された。",
    25: "【楽譜購入】オーケストラ譜の貸出料 9,800 円の支払いを承認した。",
    26: "【楽譜購入】前回承認した貸出料 9,800 円は、無料で借りられることが分かったため承認を取り消した。",
    27: "【演奏会】ホールから正式な回答があり、演奏会は 2026 年 12 月 6 日に開催することを正式決定した。",
    29: "【退団】1 名の退団の申し出を受理した。",
    30: "【練習場所】市民会館の改修が終わったため、常設の練習場所を市民会館 第1練習室へ移すことを決定した。",
    33: "【楽譜購入】演奏会用の楽譜一式 15,400 円の購入を承認した。",
    37: "【会費】伊藤さんから、会場費の値上げに合わせて会費を 3,800 円にする提案があり、10 月分から適用することを決定した。",
    38: "【入団】2 名の入団を承認した。",
    41: "【楽譜購入】予備の楽譜 3,300 円の購入を承認した。",
    44: "【練習場所】次回 1 回に限り、市民会館が使えないため中央公民館で練習する。常設の場所は変えない。",
}

MINUTES_TRUTH = {
    "current_fee": 3800,
    "fee_proposer": "伊藤",
    "location_changes": 3,
    "current_location": "市民会館 第1練習室",
    "concert_date": "2026-12-06",
    "concert_decided_on": "",
    "score_purchase_total": 36200,
    "new_members_total": 8,
}


def _meeting(no: int, day: date, rng: random.Random) -> str:
    attendees = rng.sample(MEMBERS, rng.randint(5, 8))
    lines = [
        f"## 第{no}回 練習後ミーティング（{day.year}年{day.month}月{day.day}日）",
        f"出席: {'、'.join(attendees)}",
    ]
    for topic in rng.sample(list(FILLER_TOPICS), rng.randint(3, 4)):
        lines.append(f"【{topic}】{''.join(rng.sample(FILLER_TOPICS[topic], 2))}")
    if no in PLANTED:
        lines.insert(rng.randint(2, len(lines)), PLANTED[no])
    lines.append(f"記録: {rng.choice(attendees)}")
    return "\n".join(lines)


def make_minutes() -> None:
    rng = random.Random(4242)
    start = date(2026, 1, 10)
    days = [start + timedelta(weeks=i) for i in range(50)]
    body = "\n\n".join(_meeting(i + 1, d, rng) for i, d in enumerate(days))
    base = ROOT / "long_minutes"
    (base / "files").mkdir(parents=True, exist_ok=True)
    (base / "files" / "minutes_2026.md").write_text(
        f"# つばめ合唱団 2026年 ミーティング記録\n\n{body}\n", encoding="utf-8"
    )
    truth = dict(MINUTES_TRUTH, concert_decided_on=days[26].isoformat())
    (base / "truth.json").write_text(
        json.dumps(truth, ensure_ascii=False, indent=1), encoding="utf-8"
    )


COMPANIES = [
    ("株式会社テスト精工", "カ）テストセイコウ"),
    ("有限会社ためし商店", "ユ）タメシシヨウテン"),
    ("株式会社サンプル電機", "カ）サンプルデンキ"),
    ("合同会社みほん", "ド）ミホン"),
    ("株式会社カクウシステム", "カ）カクウシステム"),
    ("株式会社れいじ物流", "カ）レイジブツリユウ"),
    ("株式会社かり企画", "カ）カリキカク"),
    ("一般社団法人かめい会", "シヤ）カメイカイ"),
]


INVOICES = [
    ("INV-101", 0, 55000),
    ("INV-102", 1, 33000),
    ("INV-103", 2, 128000),
    ("INV-104", 3, 22000),
    ("INV-105", 4, 76500),
    ("INV-106", 5, 41800),
    ("INV-107", 6, 19800),
    ("INV-108", 7, 64900),
    ("INV-109", 0, 27500),
    ("INV-110", 2, 88000),
]
DEPOSITS = [
    ("D01", "2026-09-25", 0, 55000),
    ("D02", "2026-09-26", 1, 32560),
    ("D03", "2026-09-26", 2, 63340),
    ("D04", "2026-09-29", 2, 64000),
    ("D05", "2026-09-29", 4, 76500),
    ("D06", "2026-09-30", 5, 41140),
    ("D07", "2026-09-30", 0, 27500),
    ("D08", "2026-09-30", 7, 64900),
    ("D09", "2026-09-30", None, 12000),
]


def _reconcile_rows() -> tuple[
    list[dict[str, str]], list[dict[str, str]], dict[str, object]
]:
    invoices = [
        {
            "invoice_id": i,
            "customer": COMPANIES[c][0],
            "amount": str(a),
            "due": "2026-09-30",
        }
        for i, c, a in INVOICES
    ]
    deposits = [
        {
            "deposit_id": d,
            "date": dt,
            "payer_kana": COMPANIES[c][1] if c is not None else "ナナシ　ゴンベエ",
            "amount": str(a),
        }
        for d, dt, c, a in DEPOSITS
    ]
    truth: dict[str, object] = {
        "matched": {
            "INV-101": ["D01"],
            "INV-102": ["D02"],
            "INV-103": ["D03", "D04"],
            "INV-105": ["D05"],
            "INV-106": ["D06"],
            "INV-108": ["D08"],
            "INV-109": ["D07"],
        },
        "unpaid": ["INV-104", "INV-107", "INV-110"],
        "unknown_deposits": ["D09"],
    }
    return invoices, deposits, truth


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def make_reconcile() -> None:
    invoices, deposits, truth = _reconcile_rows()
    base = ROOT / "reconcile"
    (base / "files").mkdir(parents=True, exist_ok=True)
    _write_csv(base / "files" / "invoices.csv", invoices)
    _write_csv(base / "files" / "bank.csv", deposits)
    (base / "truth.json").write_text(
        json.dumps(truth, ensure_ascii=False, indent=1), encoding="utf-8"
    )


NOTE_TAGS = ["合唱", "ローカルLLM", "経費", "旅行", "読書", "家電"]


def _notes(rng: random.Random) -> dict[str, tuple[list[str], list[str]]]:
    names = [f"note-{i:02d}" for i in range(1, 26)]
    notes: dict[str, tuple[list[str], list[str]]] = {}
    for name in names:
        tags = rng.sample(NOTE_TAGS, rng.randint(1, 3))
        links = rng.sample([n for n in names if n != name], rng.randint(0, 3))
        notes[name] = (tags, links)
    for broken, src in (
        ("note-99", "note-03"),
        ("会計メモ", "note-11"),
        ("note-7", "note-20"),
    ):
        notes[src][1].append(broken)
    return notes


def make_notes() -> None:
    rng = random.Random(777)
    notes = _notes(rng)
    files = ROOT / "notes_index" / "files" / "notes"
    files.mkdir(parents=True, exist_ok=True)
    for name, (tags, links) in notes.items():
        body = "\n".join(f"- 関連: [[{target}]]" for target in links)
        (files / f"{name}.md").write_text(
            f"---\ntags: [{', '.join(tags)}]\n---\n# {name}\n\nメモ本文。\n{body}\n",
            encoding="utf-8",
        )
    tag_count = {t: sum(t in tags for tags, _ in notes.values()) for t in NOTE_TAGS}
    broken = sorted(
        [
            {"from": f"{s}.md", "to": t}
            for s, (_, ls) in notes.items()
            for t in ls
            if t not in notes
        ],
        key=lambda x: (x["from"], x["to"]),
    )
    incoming = {t for _, ls in notes.values() for t in ls}
    truth = {
        "tags": tag_count,
        "broken_links": broken,
        "orphans": sorted(f"{n}.md" for n in notes if n not in incoming),
    }
    (ROOT / "notes_index" / "truth.json").write_text(
        json.dumps(truth, ensure_ascii=False, indent=1), encoding="utf-8"
    )


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    make_minutes()
    make_reconcile()
    make_notes()
