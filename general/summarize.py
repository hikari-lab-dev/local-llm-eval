"""general/results/<tag>.jsonl（run_general.py の出力）をモデル別に集計して表示する。

  python3 summarize.py results/general1.jsonl results/hard1.jsonl
  python3 summarize.py --csv results/general1.jsonl   # 課題ごとの数値だけの CSV を標準出力へ

CSV には final_text・notes・workdir を含めない（生の出力や環境のパスが混ざらないようにするため）。
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

CSV_COLUMNS = [
    "tag",
    "model",
    "task",
    "web",
    "status",
    "elapsed_s",
    "score",
    "max",
    "steps",
    "tool_errors",
    "output_tokens",
    "cost_usd",
]


def load_rows(paths: list[Path]) -> list[dict]:
    """jsonl ファイルを読み、1 行 1 レコードのリストにする。"""
    rows = []
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def summarize(rows: list[dict]) -> list[tuple[str, str, int, int, int, float]]:
    """(tag, model, 課題数, 得点, 満点, 所要秒の合計) をタグ・モデル順に返す。"""
    acc: dict[tuple[str, str], list[float]] = defaultdict(lambda: [0, 0, 0, 0.0])
    for row in rows:
        entry = acc[(row["tag"], row["model"])]
        entry[0] += 1
        entry[1] += row["score"]
        entry[2] += row["max"]
        entry[3] += row["elapsed_s"]
    return [
        (tag, model, int(v[0]), int(v[1]), int(v[2]), round(v[3], 1))
        for (tag, model), v in sorted(acc.items())
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--csv", action="store_true", help="課題ごとの CSV を出力する")
    args = ap.parse_args()
    rows = load_rows(args.files)
    if args.csv:
        writer = csv.DictWriter(sys.stdout, CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        return 0
    print("tag\tmodel\ttasks\tscore\tmax\tseconds")
    for tag, model, n, score, full, seconds in summarize(rows):
        print(f"{tag}\t{model}\t{n}\t{score}\t{full}\t{seconds}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
