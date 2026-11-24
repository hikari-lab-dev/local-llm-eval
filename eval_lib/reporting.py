"""results.jsonl の集計と Markdown レポート生成。"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass

_WILSON_Z_95 = 1.959963984540054
_LOOP_STATUSES = frozenset({"tool_loop", "step_limit"})
_LOOP_REPEAT_STREAK_THRESHOLD = 3


def wilson_interval(successes: int, total: int) -> tuple[float, float]:
    """Wilson score 法による95%信頼区間を返す（0.0〜1.0のペア）。total が0なら(0.0, 0.0)。"""
    if total == 0:
        return (0.0, 0.0)
    p_hat = successes / total
    z_squared = _WILSON_Z_95**2
    denominator = 1 + z_squared / total
    center = p_hat + z_squared / (2 * total)
    margin = _WILSON_Z_95 * math.sqrt(
        p_hat * (1 - p_hat) / total + z_squared / (4 * total**2)
    )
    lower = (center - margin) / denominator
    upper = (center + margin) / denominator
    return (max(0.0, lower), min(1.0, upper))


@dataclass(frozen=True)
class Aggregate:
    """モデル×言語×タグごとの集計結果。"""

    model: str
    lang: str
    tag: str
    trial_count: int
    hidden_pass_count: int
    average_seconds: float
    status_counts: Counter[str]
    lint_measured_count: int
    lint_pass_count: int
    task_count: int
    pass_all_count: int
    average_output_tokens: float | None
    loop_suspect_count: int

    @property
    def hidden_pass_rate(self) -> float:
        """隠しテスト通過率（0.0〜1.0）。"""
        if self.trial_count == 0:
            return 0.0
        return self.hidden_pass_count / self.trial_count

    @property
    def lint_pass_rate(self) -> float:
        """lint 合格率（0.0〜1.0）。lint_pass が None（未計測・検証不能）の件は分母から除く。"""
        if self.lint_measured_count == 0:
            return 0.0
        return self.lint_pass_count / self.lint_measured_count

    @property
    def hidden_pass_ci(self) -> tuple[float, float]:
        """hidden_pass_rate の Wilson 95% 信頼区間。"""
        return wilson_interval(self.hidden_pass_count, self.trial_count)

    @property
    def lint_pass_ci(self) -> tuple[float, float]:
        """lint_pass_rate の Wilson 95% 信頼区間（lint_measured_count が分母）。"""
        return wilson_interval(self.lint_pass_count, self.lint_measured_count)


def aggregate(records: list[dict]) -> list[Aggregate]:
    """レコード一覧を (model, lang, tag) ごとに集計する。

    tag が無い旧形式のレコードは baseline として扱う。
    """
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for record in records:
        key = (record["model"], record["lang"], record.get("tag", "baseline"))
        grouped[key].append(record)
    return [
        _aggregate_group(model, lang, tag, group)
        for (model, lang, tag), group in sorted(grouped.items())
    ]


def _aggregate_group(model: str, lang: str, tag: str, group: list[dict]) -> Aggregate:
    """1つの (model, lang, tag) グループを集計する。"""
    trial_count = len(group)
    total_seconds = sum(record["total_seconds"] for record in group)
    lint_values = [
        record["lint_pass"] for record in group if record.get("lint_pass") is not None
    ]
    pass_all = _pass_all_counts(group)
    return Aggregate(
        model=model,
        lang=lang,
        tag=tag,
        trial_count=trial_count,
        hidden_pass_count=sum(1 for record in group if record["hidden_pass"]),
        average_seconds=total_seconds / trial_count if trial_count else 0.0,
        status_counts=Counter(record["worker_status"] for record in group),
        lint_measured_count=len(lint_values),
        lint_pass_count=sum(1 for value in lint_values if value),
        task_count=pass_all[0],
        pass_all_count=pass_all[1],
        average_output_tokens=_average_output_tokens(group),
        loop_suspect_count=sum(1 for record in group if _is_loop_suspect(record)),
    )


def _is_full_pass(record: dict) -> bool:
    """hidden_pass かつ lint_pass が False でない（None=未計測は許容）か。"""
    return bool(record["hidden_pass"]) and record.get("lint_pass") is not False


def _pass_all_counts(group: list[dict]) -> tuple[int, int]:
    """(課題数, 全試行で合格した課題数) を返す。task キーの無いレコードは数えない。"""
    by_task: dict[str, list[bool]] = defaultdict(list)
    for record in group:
        if "task" in record:
            by_task[record["task"]].append(_is_full_pass(record))
    return len(by_task), sum(1 for results in by_task.values() if all(results))


def _average_output_tokens(group: list[dict]) -> float | None:
    """出力＋reasoning トークンの平均。output_tokens が無い古いレコードは除外する。"""
    totals = [
        record["output_tokens"] + (record.get("reasoning_tokens") or 0)
        for record in group
        if record.get("output_tokens") is not None
    ]
    if not totals:
        return None
    return sum(totals) / len(totals)


def _is_loop_suspect(record: dict) -> bool:
    """ループ疑い（tool_loop / step_limit、length 停止あり、同一ツール連続の多発）か。"""
    if record["worker_status"] in _LOOP_STATUSES:
        return True
    if (record.get("length_stop_count") or 0) > 0:
        return True
    streak = record.get("max_repeat_tool_streak") or 0
    return streak >= _LOOP_REPEAT_STREAK_THRESHOLD


def render_markdown(aggregates: list[Aggregate]) -> str:
    """集計結果を短い Markdown 表に整形する。"""
    if not aggregates:
        return "# local-llm-eval report\n\n結果がありません（results/results.jsonl が空です）。\n"
    lines = [
        "# local-llm-eval report",
        "",
        "| tag | model | lang | trials | hidden_pass | lint_pass | pass_all_k "
        "| avg_out_tokens | avg_seconds | loop_suspect | status内訳 |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    lines.extend(_render_row(item) for item in aggregates)
    lines.append("")
    return "\n".join(lines)


def _render_row(item: Aggregate) -> str:
    """1行ぶんの Markdown テーブル行を作る。"""
    status_text = ", ".join(
        f"{status}:{count}" for status, count in sorted(item.status_counts.items())
    )
    hidden_text = _render_rate_cell(
        item.hidden_pass_count, item.trial_count, item.hidden_pass_ci
    )
    lint_text = _render_lint_cell(item)
    return (
        f"| {item.tag} | {item.model} | {item.lang} | {item.trial_count} "
        f"| {hidden_text} "
        f"| {lint_text} "
        f"| {item.pass_all_count}/{item.task_count} "
        f"| {_render_tokens(item.average_output_tokens)} "
        f"| {round(item.average_seconds, 1)} "
        f"| {item.loop_suspect_count}/{item.trial_count} | {status_text} |"
    )


def _render_tokens(average: float | None) -> str:
    """平均トークン数のセル。計測済みレコードが無ければ N/A。"""
    if average is None:
        return "N/A"
    return str(round(average))


def _render_rate_cell(count: int, total: int, ci: tuple[float, float]) -> str:
    """'n/N (pct%, lo–hi%)' 形式のセルを作る。信頼区間はパーセントの整数へ丸める。"""
    if total == 0:
        return f"{count}/{total} (0%)"
    pct = round(count / total * 100)
    lo = round(ci[0] * 100)
    hi = round(ci[1] * 100)
    return f"{count}/{total} ({pct}%, {lo}–{hi}%)"


def _render_lint_cell(item: Aggregate) -> str:
    """lint_pass セルを組み立てる。計測件数が0（--lint 未使用など）なら N/A にする。"""
    if item.lint_measured_count == 0:
        return "N/A"
    return _render_rate_cell(
        item.lint_pass_count, item.lint_measured_count, item.lint_pass_ci
    )
