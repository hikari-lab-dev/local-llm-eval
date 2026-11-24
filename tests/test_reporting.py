from dataclasses import dataclass

from eval_lib.reporting import aggregate, render_markdown, wilson_interval


@dataclass(frozen=True)
class _SampleResult:
    """テスト用の最小限のレコードを組み立てるためのパラメータ一式。"""

    model: str
    lang: str
    hidden_pass: bool
    status: str
    seconds: float
    tag: str = "baseline"
    lint_pass: bool | None = None


def _record(sample: _SampleResult) -> dict:
    """テスト用の最小限のレコードを作る。"""
    return {
        "model": sample.model,
        "lang": sample.lang,
        "hidden_pass": sample.hidden_pass,
        "worker_status": sample.status,
        "total_seconds": sample.seconds,
        "tag": sample.tag,
        "lint_pass": sample.lint_pass,
    }


def test_aggregate_groups_by_model_and_lang() -> None:
    records = [
        _record(_SampleResult("m1", "python", True, "success", 10.0)),
        _record(_SampleResult("m1", "python", False, "verify_failed", 20.0)),
        _record(_SampleResult("m2", "python", True, "success", 5.0)),
    ]
    aggregates = aggregate(records)
    assert [(item.model, item.lang, item.trial_count) for item in aggregates] == [
        ("m1", "python", 2),
        ("m2", "python", 1),
    ]


def test_aggregate_hidden_pass_rate() -> None:
    records = [
        _record(_SampleResult("m1", "python", True, "success", 10.0)),
        _record(_SampleResult("m1", "python", False, "verify_failed", 20.0)),
    ]
    aggregates = aggregate(records)
    assert aggregates[0].hidden_pass_rate == 0.5


def test_aggregate_average_seconds() -> None:
    records = [
        _record(_SampleResult("m1", "python", True, "success", 10.0)),
        _record(_SampleResult("m1", "python", False, "verify_failed", 20.0)),
    ]
    aggregates = aggregate(records)
    assert aggregates[0].average_seconds == 15.0


def test_render_markdown_empty_results() -> None:
    markdown = render_markdown([])
    assert "results" in markdown


def test_render_markdown_includes_model_name() -> None:
    records = [_record(_SampleResult("m1", "python", True, "success", 10.0))]
    markdown = render_markdown(aggregate(records))
    assert "m1" in markdown


def test_render_markdown_includes_lang_name() -> None:
    records = [_record(_SampleResult("m1", "python", True, "success", 10.0))]
    markdown = render_markdown(aggregate(records))
    assert "python" in markdown


def test_aggregate_groups_by_tag_separately() -> None:
    """同じ model/lang でも tag が異なれば別グループになる（規約あり/なしの比較用）。"""
    records = [
        _record(_SampleResult("m1", "python", True, "success", 10.0, tag="baseline")),
        _record(_SampleResult("m1", "python", True, "success", 10.0, tag="rules")),
    ]
    aggregates = aggregate(records)
    assert {item.tag for item in aggregates} == {"baseline", "rules"}


def test_aggregate_reads_legacy_records_without_tag_as_baseline() -> None:
    """tag キーの無い旧形式レコードは baseline として集計する。"""
    legacy_record = {
        "model": "m1",
        "lang": "python",
        "hidden_pass": True,
        "worker_status": "success",
        "total_seconds": 10.0,
    }
    aggregates = aggregate([legacy_record])
    assert aggregates[0].tag == "baseline"


def test_aggregate_lint_pass_rate_excludes_unmeasured() -> None:
    """lint_pass が None（未計測・検証不能）の件は lint_pass_rate の分母から除く。"""
    records = [
        _record(_SampleResult("m1", "python", True, "success", 10.0, lint_pass=True)),
        _record(_SampleResult("m1", "python", True, "success", 10.0, lint_pass=False)),
        _record(_SampleResult("m1", "python", True, "success", 10.0, lint_pass=None)),
    ]
    aggregates = aggregate(records)
    assert aggregates[0].lint_measured_count == 2
    assert aggregates[0].lint_pass_rate == 0.5


def test_render_markdown_shows_na_when_lint_not_measured() -> None:
    """lint_pass が全件 None（--lint 未使用）なら N/A と表示する。"""
    records = [_record(_SampleResult("m1", "python", True, "success", 10.0))]
    markdown = render_markdown(aggregate(records))
    assert "N/A" in markdown


def test_wilson_interval_zero_total_returns_zero_zero() -> None:
    assert wilson_interval(0, 0) == (0.0, 0.0)


def test_wilson_interval_contains_point_estimate() -> None:
    """信頼区間は必ず点推定（successes/total）を含む。"""
    lower, upper = wilson_interval(14, 15)
    assert lower <= 14 / 15 <= upper


def test_wilson_interval_narrower_with_more_trials() -> None:
    """試行回数が多いほど信頼区間は狭くなる（同じ通過率で比較）。"""
    narrow = wilson_interval(140, 150)
    wide = wilson_interval(14, 15)
    assert (narrow[1] - narrow[0]) < (wide[1] - wide[0])


def test_aggregate_hidden_pass_ci_is_wilson_interval() -> None:
    """Aggregate.hidden_pass_ci が trial_count/hidden_pass_count から計算される。"""
    records = [
        _record(_SampleResult("m1", "python", True, "success", 10.0)),
        _record(_SampleResult("m1", "python", True, "success", 10.0)),
        _record(_SampleResult("m1", "python", False, "verify_failed", 10.0)),
    ]
    aggregates = aggregate(records)
    assert aggregates[0].hidden_pass_ci == wilson_interval(2, 3)


def test_render_markdown_includes_confidence_interval_range() -> None:
    """レポートの hidden_pass セルに信頼区間の範囲（'-'区切り）が出る。"""
    records = [_record(_SampleResult("m1", "python", True, "success", 10.0))]
    markdown = render_markdown(aggregate(records))
    assert "–" in markdown


def _task_record(task: str, **overrides: object) -> dict:
    """task 付きの成功レコード。overrides でキーを上書きする。"""
    base = {
        "task": task,
        "model": "m1",
        "lang": "python",
        "hidden_pass": True,
        "worker_status": "success",
        "total_seconds": 10.0,
        "lint_pass": True,
    }
    return {**base, **overrides}


def test_pass_all_counts_task_only_when_every_trial_passes() -> None:
    records = [
        _task_record("t1"),
        _task_record("t1"),
        _task_record("t2"),
        _task_record("t2", hidden_pass=False),
    ]
    item = aggregate(records)[0]
    assert (item.pass_all_count, item.task_count) == (1, 2)


def test_pass_all_fails_when_lint_pass_is_false() -> None:
    item = aggregate([_task_record("t1", lint_pass=False)])[0]
    assert item.pass_all_count == 0


def test_pass_all_tolerates_unmeasured_lint() -> None:
    item = aggregate([_task_record("t1", lint_pass=None)])[0]
    assert item.pass_all_count == 1


def test_average_output_tokens_sums_reasoning_and_skips_old_records() -> None:
    records = [
        _task_record("t1", output_tokens=100, reasoning_tokens=50),
        _task_record("t2", output_tokens=200, reasoning_tokens=None),
        _task_record("t3"),
    ]
    assert aggregate(records)[0].average_output_tokens == 175.0


def test_average_output_tokens_is_none_without_measurements() -> None:
    assert aggregate([_task_record("t1")])[0].average_output_tokens is None


def test_loop_suspect_by_worker_status() -> None:
    item = aggregate([_task_record("t1", worker_status="tool_loop")])[0]
    assert item.loop_suspect_count == 1


def test_loop_suspect_by_length_stop() -> None:
    item = aggregate([_task_record("t1", length_stop_count=1)])[0]
    assert item.loop_suspect_count == 1


def test_loop_suspect_by_repeat_streak_threshold() -> None:
    records = [
        _task_record("t1", max_repeat_tool_streak=3),
        _task_record("t2", max_repeat_tool_streak=2),
        _task_record("t3", max_repeat_tool_streak=None),
    ]
    assert aggregate(records)[0].loop_suspect_count == 1


def test_render_markdown_shows_new_columns() -> None:
    records = [_task_record("t1", output_tokens=10, reasoning_tokens=5)]
    markdown = render_markdown(aggregate(records))
    assert "| 1/1 | 15 | 10.0 | 0/1 |" in markdown
