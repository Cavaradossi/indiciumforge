from __future__ import annotations

from indiciumforge_core.labels.market_gate import MARKET_DAILY, MARKET_ZH
from indiciumforge_core.market.theme_rules import THEME_STATE_RULES

from indiciumforge_workflow.market_awareness.models import ThemeSectorMetrics, ThemeStateRow


def classify_theme_state(
    metrics: ThemeSectorMetrics,
    rules: dict[str, float | int] | None = None,
) -> ThemeStateRow:
    rule_set = rules or THEME_STATE_RULES
    neutral = MARKET_ZH["neutral_theme"]
    no_risk = MARKET_DAILY["normal_risk"]
    no_div = MARKET_DAILY["normal_divergence"]

    if _is_hard_weak(metrics, rule_set):
        hard_weak = MARKET_DAILY["hard_weak"]
        return ThemeStateRow(
            theme_name=metrics.theme_name,
            status=hard_weak,
            daily_state=MARKET_DAILY["daily_weak"],
            mid_state=neutral,
            risk_state=hard_weak,
            divergence_state=no_div,
        )

    if _is_divergent(metrics, rule_set):
        return ThemeStateRow(
            theme_name=metrics.theme_name,
            status=MARKET_DAILY["divergent"],
            daily_state=MARKET_DAILY["daily_weak"],
            mid_state=neutral,
            risk_state=no_risk,
            divergence_state=MARKET_DAILY["divergent"],
        )

    if _is_turn_weak(metrics, rule_set):
        return ThemeStateRow(
            theme_name=metrics.theme_name,
            status=MARKET_DAILY["mid_strong_daily_weak"],
            daily_state=MARKET_DAILY["daily_weak"],
            mid_state=MARKET_DAILY["mid_strong"],
            risk_state=no_risk,
            divergence_state=no_div,
        )

    if _is_daily_strong(metrics, rule_set):
        daily_strong = MARKET_DAILY["daily_strong"]
        return ThemeStateRow(
            theme_name=metrics.theme_name,
            status=daily_strong,
            daily_state=daily_strong,
            mid_state=neutral,
            risk_state=no_risk,
            divergence_state=no_div,
        )

    return ThemeStateRow(
        theme_name=metrics.theme_name,
        status=neutral,
        daily_state=MARKET_DAILY["daily_weak"],
        mid_state=neutral,
        risk_state=no_risk,
        divergence_state=no_div,
    )


def classify_theme_states(
    metrics_list: list[ThemeSectorMetrics],
    rules: dict[str, float | int] | None = None,
) -> list[ThemeStateRow]:
    return [classify_theme_state(metrics, rules) for metrics in metrics_list]


def _is_hard_weak(metrics: ThemeSectorMetrics, rules: dict[str, float | int]) -> bool:
    if metrics.sample_count < int(rules["min_sample"]):
        return False
    return (
        metrics.median_1d <= float(rules["hard_weak_max_1d_median"])
        and metrics.up_rate <= float(rules["hard_weak_max_up_rate"])
        and metrics.le_minus5_ratio >= float(rules["hard_weak_min_le_minus5_ratio"])
        and metrics.limit_down_count >= int(rules["hard_weak_min_limit_down_count"])
    )


def _is_divergent(metrics: ThemeSectorMetrics, rules: dict[str, float | int]) -> bool:
    if metrics.sample_count < int(rules["min_sample"]):
        return False
    return (
        metrics.limit_up_count >= int(rules["divergent_min_limit_up_count"])
        and metrics.ge5_ratio >= float(rules["divergent_min_ge5_ratio"])
        and metrics.median_1d <= float(rules["divergent_max_1d_median"])
        and metrics.up_rate <= float(rules["divergent_max_up_rate"])
        and metrics.le_minus5_ratio >= float(rules["divergent_min_le_minus5_ratio"])
    )


def _is_turn_weak(metrics: ThemeSectorMetrics, rules: dict[str, float | int]) -> bool:
    if metrics.sample_count < int(rules["min_sample"]):
        return False
    mid_strong = metrics.median_3d >= float(rules["daily_strong_min_1d_median"])
    return mid_strong and (
        metrics.median_1d <= float(rules["turn_weak_max_1d_median"])
        and metrics.up_rate <= float(rules["turn_weak_max_up_rate"])
        and metrics.le_minus5_ratio >= float(rules["turn_weak_min_le_minus5_ratio"])
    )


def _is_daily_strong(metrics: ThemeSectorMetrics, rules: dict[str, float | int]) -> bool:
    min_sample = int(rules["strong_min_sample"])
    if metrics.sample_count < min_sample:
        return False
    return (
        metrics.median_1d >= float(rules["daily_strong_min_1d_median"])
        and metrics.relative_1d >= float(rules["daily_strong_min_relative_1d"])
        and metrics.up_rate >= float(rules["daily_strong_min_up_rate"])
        and metrics.ge5_ratio >= float(rules["daily_strong_min_ge5_ratio"])
        and metrics.limit_up_count >= int(rules["daily_strong_min_limit_up_count"])
    )
