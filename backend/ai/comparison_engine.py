"""
Algorithm 2 - Financial Comparison.

Pseudo-formula: for each key metric (revenue, net income, assets,
liabilities), compute the percentage change between two periods and
generate a plain-English insight sentence. Pure Python/pandas, no LLM.

Worked example (matches the spec's own sample):
  prior.revenue = $100M, current.revenue = $115M
  pct_change = (115-100)/100 = 15%
  insight -> "Revenue increased by 15.0% from $100.0M to $115.0M."
"""
from __future__ import annotations

import logging

import pandas as pd

from ai.schemas import ComparisonResult, FinancialMetrics, MetricChange

logger = logging.getLogger(__name__)

METRIC_LABELS = {
    "revenue": "Revenue",
    "net_income": "Net Income",
    "total_assets": "Total Assets",
    "total_liabilities": "Total Liabilities",
    "operating_cash_flow": "Operating Cash Flow",
}


def _insight_sentence(label: str, prior_value: float, current_value: float, pct: float) -> str:
    direction = "increased" if pct >= 0 else "decreased"
    return (
        f"{label} {direction} by {abs(pct):.1f}% "
        f"from ${prior_value:,.1f}M to ${current_value:,.1f}M."
    )


def compare_reports(current: FinancialMetrics, prior: FinancialMetrics) -> ComparisonResult:
    """
    Uses a small pandas DataFrame purely for the vectorized pct_change
    computation (spec calls for Pandas/NumPy for comparisons) — the
    dataset here is tiny, but this is the same code path that would scale
    to comparing many metrics or many periods at once.
    """
    df = pd.DataFrame(
        {
            "prior": [getattr(prior, f) for f in METRIC_LABELS],
            "current": [getattr(current, f) for f in METRIC_LABELS],
        },
        index=list(METRIC_LABELS.keys()),
    )
    df["pct_change"] = ((df["current"] - df["prior"]) / df["prior"].replace(0, pd.NA)) * 100
    df["pct_change"] = df["pct_change"].fillna(0.0)

    changes: list[MetricChange] = []
    for field, label in METRIC_LABELS.items():
        prior_value = float(df.loc[field, "prior"])
        current_value = float(df.loc[field, "current"])
        pct = float(df.loc[field, "pct_change"])
        changes.append(MetricChange(
            metric=label,
            prior_value=prior_value,
            current_value=current_value,
            pct_change=round(pct, 1),
            insight=_insight_sentence(label, prior_value, current_value, pct),
        ))

    logger.info("compare_reports: %s vs %s -> %d metrics", current.label, prior.label, len(changes))
    return ComparisonResult(current_label=current.label, prior_label=prior.label, changes=changes)
