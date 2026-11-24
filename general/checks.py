"""汎用作業評価の自動採点。各関数は作業ディレクトリを受け取り (得点, 満点, 所見) を返す。"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import unicodedata
import urllib.request
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import cache
from pathlib import Path
from typing import Any

TASKS = Path(__file__).resolve().parent / "tasks"
Result = tuple[float, int, list[str]]
EMOJI = re.compile(f"[{chr(0x1F000)}-{chr(0x1FAFF)}{chr(0x2600)}-{chr(0x27BF)}]")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"__error__": str(exc)} if path.exists() else None


def _norm(text: object) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", str(text))).upper()


def _score(items: list[tuple[bool, str]], full: int) -> Result:
    """(合否, 不合格時の所見) の列を得点にまとめる。"""
    return sum(ok for ok, _ in items), full, [note for ok, note in items if not ok]


MINUTES_EXPECTED = {
    "佐藤": "2026-09-23",
    "鈴木": "2026-10-04",
    "高橋": "2026-10-02",
    "田中": "2026-09-30",
    "伊藤": "2026-10-10",
}


def check_minutes(work: Path) -> Result:
    data = _load_json(work / "actions.json")
    if not isinstance(data, list):
        return 0, 5, ["actions.json が無いか JSON 配列でない"]
    items: list[tuple[bool, str]] = []
    matched: set[str] = set()
    for item in data:
        owner = str(item.get("owner", "")) if isinstance(item, dict) else ""
        name = next((n for n in MINUTES_EXPECTED if n in owner), None)
        ok = (
            name is not None
            and name not in matched
            and item.get("due") == MINUTES_EXPECTED[name]
        )
        matched.add(name or "")
        items.append((ok, f"不一致または余分: {item}"))
    score, _, notes = _score(items, 5)
    return max(0, score - max(0, len(data) - 5)), 5, notes


SCHEDULE_PARTS = ("S1", "S2", "A1", "A2", "T", "B")
ROOM_CAP = {"ホール": 2, "会議室A": 1, "会議室B": 1}


def _schedule_valid(plan: object) -> bool:
    try:
        assert isinstance(plan, dict) and set(plan) == set(SCHEDULE_PARTS)
        slots = [(plan[p]["room"], plan[p]["slot"]) for p in SCHEDULE_PARTS]
        assert all(r in ROOM_CAP and s in ("13:00", "15:00") for r, s in slots)
        return all(slots.count(rs) <= ROOM_CAP[rs[0]] for rs in slots)
    except (AssertionError, KeyError, TypeError):
        return False


def check_schedule(work: Path) -> Result:
    plan = _load_json(work / "plan.json")
    if not _schedule_valid(plan):
        return 0, 8, ["plan.json の構造・部屋の定員が不正"]

    def at(part: str) -> tuple[str, str]:
        return plan[part]["room"], plan[part]["slot"]

    hall_15 = sum(1 for p in SCHEDULE_PARTS if at(p) == ("ホール", "15:00"))
    rules = [
        at("S1") == at("S2"),
        at("T")[0] in ("ホール", "会議室A"),
        at("B")[1] != at("T")[1],
        at("A1")[1] != "13:00",
        all(at(p) != ("会議室B", "15:00") for p in SCHEDULE_PARTS),
        at("A1")[0] != at("A2")[0],
        hall_15 <= 1,
    ]
    score, _, notes = _score(
        [(ok, f"条件{i + 1} 違反") for i, ok in enumerate(rules)], 8
    )
    return 1 + score, 8, notes


def check_notice(work: Path) -> Result:
    path = work / "notice.txt"
    if not path.exists():
        return 0, 8, ["notice.txt が無い"]
    text = path.read_text(encoding="utf-8")
    lines = text.rstrip("\n").split("\n")
    bullets = lines[2:]
    bodies = [b[2:] for b in bullets]
    required = ("10月11日（日）", "13時〜17時", "市民会館 第2練習室", "1,000円")
    rules = [
        lines[0].startswith("【お知らせ】"),
        len(lines) > 1 and lines[1].strip() == "",
        len(bullets) == 4 and all(b.startswith("- ") for b in bullets),
        bool(bodies)
        and all(len(b) <= 40 and b.endswith(("です。", "ます。")) for b in bodies),
        all(r in text for r in required),
        not re.search("[！!]", text) and not EMOJI.search(text),
        len(text.strip()) <= 250,
        all(c in text for c in ("レクイエム", "駐車", "乗り合", "会費")),
    ]
    return _score([(ok, f"規則{i + 1} 違反") for i, ok in enumerate(rules)], 8)


EMAIL_BUSY = [
    (datetime.fromisoformat(e["start"]), datetime.fromisoformat(e["end"]))
    for e in json.loads(
        (TASKS / "email/files/calendar.json").read_text(encoding="utf-8")
    )["events"]
]


def _parse_slot(slot: Any) -> tuple[datetime, datetime] | None:
    """枠を naive な日時の組にする。タイムゾーン付き（+09:00 など）は外して JST とみなす。"""
    try:
        start, end = (
            datetime.fromisoformat(slot[k]).replace(tzinfo=None)
            for k in ("start", "end")
        )
        return start, end
    except (KeyError, TypeError, ValueError):
        return None


def _slot_ok(slot: object) -> bool:
    parsed = _parse_slot(slot)
    if parsed is None:
        return False
    start, end = parsed
    pad = timedelta(minutes=15)
    lunch_start, lunch_end = (
        start.replace(hour=12, minute=0),
        start.replace(hour=13, minute=0),
    )
    return (
        "2026-10-05" <= start.date().isoformat() <= "2026-10-09"
        and end - start == timedelta(hours=1)
        and start.hour >= 9
        and end <= start.replace(hour=18, minute=0)
        and not (start < lunch_end and end > lunch_start)
        and all(
            not (start < b_end + pad and end > b_start - pad)
            for b_start, b_end in EMAIL_BUSY
        )
    )


def _mentioned(reply: str, slot: dict[str, str]) -> bool:
    start = datetime.fromisoformat(slot["start"])
    text = _norm(reply)
    day = (
        f"{start.month}月{start.day}日" in text or f"{start.month}/{start.day}" in text
    )
    hour = f"{start.hour}:{start.minute:02d}" in text or f"{start.hour}時" in text
    return day and hour


def check_email(work: Path) -> Result:
    slots = _load_json(work / "slots.json")
    reply_path = work / "reply.txt"
    if not isinstance(slots, list) or not reply_path.exists():
        return 0, 5, ["slots.json か reply.txt が無い"]
    valid = [s for s in slots if _slot_ok(s)]
    days = {s["start"][:10] for s in valid}
    reply = reply_path.read_text(encoding="utf-8")
    items = [(False, f"条件外の枠: {s}") for s in slots if not _slot_ok(s)]
    items += [
        (len(slots) == 3 and len(days) == 3, "3 枠・別日になっていない"),
        (
            "件名" in reply
            and len(valid) == len(slots)
            and all(_mentioned(reply, s) for s in valid),
            "件名が無いか、本文の日時が slots.json と一致しない",
        ),
    ]
    extra, _, notes = _score(items, 5)
    return max(0, min(3, len(valid)) - max(0, len(slots) - 3) + extra), 5, notes


def _read_index(path: Path) -> list[tuple[str, str, str]]:
    try:
        with path.open(encoding="utf-8-sig") as f:
            return [(r["original"], r["date"], r["amount"]) for r in csv.DictReader(f)]
    except (OSError, KeyError) as exc:
        return [("__error__", str(exc), "")]


def check_receipts(work: Path) -> Result:
    truth = _load_json(TASKS / "receipts/truth.json")
    names = {
        unicodedata.normalize("NFC", p.name) for p in (work / "receipts").glob("*")
    }
    items = [
        (t["renamed"] in names, f"{t['original']} → {t['renamed']} になっていない")
        for t in truth
    ]
    want = [
        (
            t["original"],
            f"{t['renamed'][:4]}-{t['renamed'][4:6]}-{t['renamed'][6:8]}",
            t["renamed"].rsplit("_", 1)[1].removesuffix(".txt"),
        )
        for t in truth
    ]
    items.append(
        (_read_index(work / "index.csv") == want, "index.csv が無いか内容・順序が違う")
    )
    return _score(items, 9)


def check_expenses(work: Path) -> Result:
    truth = _load_json(TASKS / "expenses/truth.json")
    got = _load_json(work / "summary.json")
    if not isinstance(got, dict):
        return 0, 7, ["summary.json が無い"]
    by_cat = got.get("by_category") or {}
    items = [
        (by_cat.get(c) == v, f"{c}: {v} のはずが {by_cat.get(c)}")
        for c, v in truth["by_category"].items()
    ]
    items += [
        (got.get(k) == truth[k], f"{k}: {truth[k]} のはずが {got.get(k)}")
        for k in ("total", "max_month")
    ]
    return _score(items, 7)


def check_web_gemma(work: Path) -> Result:
    data = _load_json(work / "answer.json")
    if not isinstance(data, dict):
        return 0, 5, ["answer.json が無い"]
    sizes = {_norm(s) for s in data.get("sizes") or []}
    rules = [
        data.get("first_release_date") in ("2026-03-31", "2026-04-02"),
        all(any(k in s for s in sizes) for k in ("E2B", "E4B", "26B", "31B", "12B")),
        "APACHE" in _norm(data.get("license", ""))
        and "2.0" in str(data.get("license")),
        "12B" in _norm(data.get("latest_addition", "")),
        any(str(u).startswith("http") for u in data.get("sources") or []),
    ]
    return _score([(ok, f"項目{i + 1} 誤り") for i, ok in enumerate(rules)], 5)


@cache
def _uv_latest() -> tuple[str, str]:
    out = subprocess.run(
        [
            "gh",
            "api",
            "repos/astral-sh/uv/releases/latest",
            "--jq",
            "[.tag_name,.published_at]",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout
    tag, published = json.loads(out)
    return tag.lstrip("v"), published[:10]


def check_web_release(work: Path) -> Result:
    data = _load_json(work / "release.json")
    if not isinstance(data, dict):
        return 0, 4, ["release.json が無い"]
    version, published = _uv_latest()
    rules = [
        str(data.get("version", "")).lstrip("v") == version,
        data.get("published") == published,
        len(data.get("highlights") or []) == 3,
        "astral-sh/uv" in str(data.get("source", "")),
    ]
    return _score(
        [
            (ok, f"項目{i + 1} 誤り（正解 {version} / {published}）")
            for i, ok in enumerate(rules)
        ],
        4,
    )


@cache
def _pypi_latest(pkg: str) -> str:
    with urllib.request.urlopen(f"https://pypi.org/pypi/{pkg}/json", timeout=30) as r:
        return json.load(r)["info"]["version"]


def check_web_pypi(work: Path) -> Result:
    data = _load_json(work / "outdated.json")
    if not isinstance(data, dict):
        return 0, 8, ["outdated.json が無い"]
    current = {
        "requests": "2.28.0",
        "numpy": "1.24.0",
        "pydantic": "1.10.0",
        "httpx": "0.23.0",
    }
    items: list[tuple[bool, str]] = []
    for pkg, cur in current.items():
        latest = _pypi_latest(pkg)
        entry = data.get(pkg) or {}
        major = latest.split(".")[0] != cur.split(".")[0]
        items.append(
            (
                entry.get("latest") == latest,
                f"{pkg}: 最新 {latest} のはずが {entry.get('latest')}",
            )
        )
        items.append((entry.get("major_update") is major, f"{pkg}: major_update 誤り"))
    return _score(items, 8)


def check_web_report(work: Path) -> Result:
    path = work / "report.md"
    if not path.exists():
        return 0, 4, ["report.md が無い"]
    text = path.read_text(encoding="utf-8")
    rules = [
        all(k in text.lower() for k in ("llama.cpp", "ollama", "vllm")),
        len(set(re.findall(r"https?://[^\s)\]>]+", text))) >= 3,
        800 <= len(text) <= 3500,
        "結論" in text,
    ]
    return _score([(ok, f"項目{i + 1} 不足") for i, ok in enumerate(rules)], 4)


CHECKS: dict[str, Callable[[Path], Result]] = {
    "minutes": check_minutes,
    "schedule": check_schedule,
    "notice": check_notice,
    "email": check_email,
    "receipts": check_receipts,
    "expenses": check_expenses,
    "web_gemma": check_web_gemma,
    "web_release": check_web_release,
    "web_pypi": check_web_pypi,
    "web_report": check_web_report,
}
