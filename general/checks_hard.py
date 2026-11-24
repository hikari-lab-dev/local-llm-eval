"""難しめの汎用課題の自動採点。checks.py と同じく (得点, 満点, 所見) を返す。"""

from __future__ import annotations

import json
import re
import subprocess
import urllib.request
from collections.abc import Callable
from functools import cache
from pathlib import Path
from typing import Any

from checks import TASKS, Result, _load_json, _norm, _score


def check_long_minutes(work: Path) -> Result:
    truth = _load_json(TASKS / "long_minutes/truth.json")
    got = _load_json(work / "answers.json")
    if not isinstance(got, dict):
        return 0, 9, ["answers.json が無い"]
    items = [
        (_norm(got.get(k)) == _norm(v), f"{k}: {v} のはずが {got.get(k)}")
        for k, v in truth.items()
    ]
    summary = work / "summary.md"
    text = summary.read_text(encoding="utf-8") if summary.exists() else ""
    items.append(
        (
            0 < len(text.strip()) <= 400,
            f"summary.md が無いか 400 字超（{len(text.strip())} 字）",
        )
    )
    return _score(items, 9)


def check_reconcile(work: Path) -> Result:
    truth = _load_json(TASKS / "reconcile/truth.json")
    got = _load_json(work / "result.json")
    if not isinstance(got, dict):
        return 0, 9, ["result.json が無い"]
    matched = got.get("matched") or {}
    items = [
        (
            sorted(matched.get(inv) or []) == deps,
            f"{inv}: {deps} のはずが {matched.get(inv)}",
        )
        for inv, deps in truth["matched"].items()
    ]
    items.append(
        (
            sorted(got.get("unpaid") or []) == truth["unpaid"],
            f"unpaid: {got.get('unpaid')}",
        )
    )
    items.append(
        (
            sorted(got.get("unknown_deposits") or []) == truth["unknown_deposits"],
            f"unknown: {got.get('unknown_deposits')}",
        )
    )
    return _score(items, 9)


REHEARSAL_MIN = {
    "M1": 20,
    "M2": 25,
    "M3": 15,
    "M4": 30,
    "M5": 20,
    "M6": 25,
    "M7": 15,
    "M8": 20,
}


def _rehearsal_valid(plan: Any) -> bool:
    return (
        isinstance(plan, dict)
        and set(plan) == {"R1", "R2", "R3"}
        and all(
            isinstance(v, list) and all(m in REHEARSAL_MIN for m in v)
            for v in plan.values()
        )
    )


def check_rehearsal(work: Path) -> Result:
    plan = _load_json(work / "plan.json")
    if not _rehearsal_valid(plan):
        return 0, 7, ["plan.json の構造が不正"]
    counts = {m: sum(m in v for v in plan.values()) for m in REHEARSAL_MIN}
    rules = [
        all(c == 2 for c in counts.values())
        and all(len(v) == len(set(v)) for v in plan.values()),
        all(90 <= sum(REHEARSAL_MIN[m] for m in v) <= 120 for v in plan.values()),
        "M4" not in plan["R2"],
        "M6" not in plan["R2"],
        {"M1", "M8"} <= set(plan["R3"]),
        sum({"M5", "M7"} <= set(v) for v in plan.values()) <= 1,
    ]
    score, _, notes = _score(
        [(ok, f"条件{i + 1} 違反") for i, ok in enumerate(rules)], 7
    )
    return score + (score == 6), 7, notes


def check_notes_index(work: Path) -> Result:
    truth = _load_json(TASKS / "notes_index/truth.json")
    got = _load_json(work / "index.json")
    if not isinstance(got, dict):
        return 0, 8, ["index.json が無い"]
    tags = got.get("tags") or {}
    items = [
        (tags.get(t) == n, f"tag {t}: {n} のはずが {tags.get(t)}")
        for t, n in truth["tags"].items()
    ]
    items.append(
        (
            got.get("broken_links") == truth["broken_links"],
            f"broken_links: {got.get('broken_links')}",
        )
    )
    items.append(
        (got.get("orphans") == truth["orphans"], f"orphans: {got.get('orphans')}")
    )
    return _score(items, 8)


@cache
def _json_url(url: str) -> Any:
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


@cache
def _gh_latest(repo: str) -> str:
    return subprocess.run(
        ["gh", "api", f"repos/{repo}/releases/latest", "--jq", ".tag_name"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()


def _web_multi_truth() -> dict[str, Any]:
    cycles = {
        c["cycle"]: c["latest"]
        for c in _json_url("https://endoflife.date/api/python.json")
    }
    lts = next(r for r in _json_url("https://nodejs.org/dist/index.json") if r["lts"])
    return {
        "py314": cycles["3.14"],
        "py313": cycles["3.13"],
        "node_major": int(lts["version"].lstrip("v").split(".")[0]),
        "node_codename": lts["lts"],
        "node_latest": lts["version"].lstrip("v"),
        "llama": _gh_latest("ggml-org/llama.cpp"),
    }


def check_web_multi(work: Path) -> Result:
    got = _load_json(work / "answer.json")
    if not isinstance(got, dict):
        return 0, 7, ["answer.json が無い"]
    t = _web_multi_truth()
    node = got.get("node_active_lts") or {}
    pairs = [
        ("3.14", got.get("python_3_14_latest"), t["py314"]),
        ("3.13", got.get("python_3_13_latest"), t["py313"]),
        ("node major", node.get("major"), t["node_major"]),
        ("node codename", _norm(node.get("codename")), _norm(t["node_codename"])),
        ("node latest", str(node.get("latest", "")).lstrip("v"), t["node_latest"]),
        ("llama.cpp", got.get("llama_cpp_latest"), t["llama"]),
    ]
    items = [(g == w, f"{label}: {w} のはずが {g}") for label, g, w in pairs]
    items.append(
        (
            any(str(u).startswith("http") for u in got.get("sources") or []),
            "sources なし",
        )
    )
    return _score(items, 7)


WAGE_TRUTH = {
    "tokyo_hourly": 1280,
    "tokyo_increase": 54,
    "tokyo_effective": "2026-10-01",
    "national_average": 1177,
}


def check_web_jp(work: Path) -> Result:
    got = _load_json(work / "wage.json")
    if not isinstance(got, dict):
        return 0, 5, ["wage.json が無い"]
    items = [
        (got.get(k) == v, f"{k}: {v} のはずが {got.get(k)}")
        for k, v in WAGE_TRUTH.items()
    ]
    items.append(
        (
            any("mhlw.go.jp" in str(u) for u in got.get("sources") or []),
            "厚労省・労働局の出典なし",
        )
    )
    return _score(items, 5)


def check_web_mtp(work: Path) -> Result:
    path = work / "mtp.md"
    if not path.exists():
        return 0, 4, ["mtp.md が無い"]
    text = path.read_text(encoding="utf-8")
    rules = [
        "--spec-type" in text and "draft-mtp" in text,
        len(set(re.findall(r"https?://[^\s)\]>]+", text))) >= 4,
        1200 <= len(text) <= 5000,
        bool(re.search(r"\d+(\.\d+)?\s*(tok/s|tokens?/s|倍|%)", text)),
    ]
    return _score([(ok, f"項目{i + 1} 不足") for i, ok in enumerate(rules)], 4)


HARD_CHECKS: dict[str, Callable[[Path], Result]] = {
    "long_minutes": check_long_minutes,
    "reconcile": check_reconcile,
    "rehearsal": check_rehearsal,
    "notes_index": check_notes_index,
    "web_multi": check_web_multi,
    "web_jp": check_web_jp,
    "web_mtp": check_web_mtp,
}
