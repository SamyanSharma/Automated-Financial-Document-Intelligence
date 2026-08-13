"""
Algorithm 1 - Financial Health Score, and Algorithm 3 - Anomaly Detection.

Both run in pure Python on structured `FinancialMetrics` — no LLM calls.
Per spec: "The LLM's role is not to compute the number... but to explain
why the score is that value." chat_service.py / the LLM layer can take
this module's output (score + factors) as ready-made, already-correct
context; it never recomputes it.

--- Algorithm 1: Health Score (pseudo-formula) ---
Start at 0 points, then:
  + 20 if revenue_growth   > 10%
  + 20 if net_profit_growth > 5%
  - 20 if debt_ratio (liabilities/assets) > 50%
  + 20 if operating_cash_flow > 0
  + 20 baseline "solvency" point if none of the above triggered a penalty
       (keeps the score from being unfairly punished by pure omission —
       see worked example below)
Score is clamped to [0, 100].

Worked example (matches the spec's own numbers):
  prior:   revenue=100, net_income=8,  assets=200, liabilities=90, ocf=5
  current: revenue=115, net_income=9,  assets=210, liabilities=95, ocf=6
  revenue_growth   = (115-100)/100 = 15%   -> +20 (>10%)
  net_profit_growth= (9-8)/8       = 12.5% -> +20 (>5%)
  debt_ratio        = 95/210       = 45.2% -> no penalty (<=50%)
  operating_cash_flow = 6 > 0                -> +20
  baseline (no penalty triggered)            -> +20
  total = 80/100

--- Algorithm 3: Anomaly Detection (pseudo-formula) ---
Two independent checks, both attach an AnomalyAlert if triggered:
  1. Simple threshold: |pct_change| > 50% on any of revenue/net_income/
     assets/liabilities between `prior` and `current` -> flag.
     Liabilities get a lower, asymmetric threshold (+30%) since a
     *liability spike* specifically is a red flag the spec calls out
     even below the general 50% bar.
  2. Z-score: if `history` has >= 3 prior points, compute the z-score of
     the current value against the historical mean/stdev for that
     metric. |z| > 2 (roughly 2 standard deviations, ~95% CI) -> flag.

Worked example (threshold check):
  Net Income: prior=$5M, current=$2M
  pct_change = (2-5)/5 = -60%  -> |-60%| > 50% -> alert:
  "Net Income drop of 60% (from $5.0M to $2.0M) - potential concern."
"""
from __future__ import annotations

import logging
import statistics

from ai.schemas import (
    AnomalyAlert,
    AnomalyDetectionResult,
    FinancialMetrics,
    HealthScoreFactor,
    HealthScoreResult,
)

logger = logging.getLogger(__name__)

METRIC_FIELDS = ["revenue", "net_income", "total_assets", "total_liabilities"]
LIABILITY_SPIKE_THRESHOLD_PCT = 30.0
GENERAL_ANOMALY_THRESHOLD_PCT = 50.0
ZSCORE_THRESHOLD = 2.0


def _pct_change(prior_value: float, current_value: float) -> float:
    """Percent change, guarding div-by-zero (returns 0.0 if prior is 0 —
    can't compute a meaningful percentage from a zero base)."""
    if prior_value == 0:
        return 0.0
    return ((current_value - prior_value) / abs(prior_value)) * 100


def compute_health_score(current: FinancialMetrics, prior: FinancialMetrics) -> HealthScoreResult:
    factors: list[HealthScoreFactor] = []
    score = 0
    any_penalty = False

    revenue_growth = _pct_change(prior.revenue, current.revenue)
    if revenue_growth > 10:
        score += 20
        factors.append(HealthScoreFactor(
            name="Revenue Growth", points=20,
            explanation=f"Revenue grew {revenue_growth:.1f}% (> 10% threshold).",
        ))
    else:
        factors.append(HealthScoreFactor(
            name="Revenue Growth", points=0,
            explanation=f"Revenue grew {revenue_growth:.1f}% (did not exceed 10% threshold).",
        ))

    net_profit_growth = _pct_change(prior.net_income, current.net_income)
    if net_profit_growth > 5:
        score += 20
        factors.append(HealthScoreFactor(
            name="Net Profit Growth", points=20,
            explanation=f"Net income grew {net_profit_growth:.1f}% (> 5% threshold).",
        ))
    else:
        factors.append(HealthScoreFactor(
            name="Net Profit Growth", points=0,
            explanation=f"Net income grew {net_profit_growth:.1f}% (did not exceed 5% threshold).",
        ))

    debt_ratio = (current.total_liabilities / current.total_assets * 100) if current.total_assets else 0.0
    if debt_ratio > 50:
        score -= 20
        any_penalty = True
        factors.append(HealthScoreFactor(
            name="Debt Ratio", points=-20,
            explanation=f"Liabilities/assets = {debt_ratio:.1f}% (> 50% is high leverage).",
        ))
    else:
        factors.append(HealthScoreFactor(
            name="Debt Ratio", points=0,
            explanation=f"Liabilities/assets = {debt_ratio:.1f}% (healthy, <= 50%).",
        ))

    if current.operating_cash_flow > 0:
        score += 20
        factors.append(HealthScoreFactor(
            name="Operating Cash Flow", points=20,
            explanation=f"Operating cash flow is positive (${current.operating_cash_flow:,.1f}).",
        ))
    else:
        any_penalty = True
        factors.append(HealthScoreFactor(
            name="Operating Cash Flow", points=0,
            explanation=f"Operating cash flow is not positive (${current.operating_cash_flow:,.1f}).",
        ))

    if not any_penalty:
        score += 20
        factors.append(HealthScoreFactor(
            name="Baseline Solvency", points=20,
            explanation="No debt-ratio or cash-flow red flags triggered.",
        ))

    score = max(0, min(100, score))

    if score >= 80:
        summary = f"{current.label}: strong financial health (score {score}/100)."
    elif score >= 50:
        summary = f"{current.label}: moderate financial health (score {score}/100) - some areas to watch."
    else:
        summary = f"{current.label}: weak financial health (score {score}/100) - multiple red flags."

    logger.info("Health score for %s: %d/100", current.label, score)
    return HealthScoreResult(score=score, factors=factors, summary=summary)


def detect_anomalies(
    current: FinancialMetrics,
    prior: FinancialMetrics,
    history: list[FinancialMetrics] | None = None,
) -> AnomalyDetectionResult:
    history = history or []
    alerts: list[AnomalyAlert] = []

    field_labels = {
        "revenue": "Revenue",
        "net_income": "Net Income",
        "total_assets": "Total Assets",
        "total_liabilities": "Total Liabilities",
    }

    for field, label in field_labels.items():
        prior_value = getattr(prior, field)
        current_value = getattr(current, field)
        pct = _pct_change(prior_value, current_value)

        threshold = LIABILITY_SPIKE_THRESHOLD_PCT if field == "total_liabilities" else GENERAL_ANOMALY_THRESHOLD_PCT

        if abs(pct) > threshold:
            direction = "increase" if pct > 0 else "drop"
            severity = "critical" if abs(pct) > 75 else "warning"
            alerts.append(AnomalyAlert(
                metric=label,
                pct_change=round(pct, 1),
                severity=severity,
                message=(
                    f"{label} {direction} of {abs(pct):.0f}% "
                    f"(from ${prior_value:,.1f}M to ${current_value:,.1f}M) - potential concern."
                ),
            ))

    if len(history) >= 3:
        for field, label in field_labels.items():
            values = [getattr(h, field) for h in history]
            mean = statistics.mean(values)
            stdev = statistics.stdev(values)
            if stdev == 0:
                continue
            current_value = getattr(current, field)
            z = (current_value - mean) / stdev
            if abs(z) > ZSCORE_THRESHOLD:
                alerts.append(AnomalyAlert(
                    metric=label,
                    pct_change=round(_pct_change(mean, current_value), 1),
                    severity="warning",
                    message=(
                        f"{label} of ${current_value:,.1f}M is {abs(z):.1f} standard deviations "
                        f"from its historical average (${mean:,.1f}M) - statistically unusual."
                    ),
                ))

    logger.info("detect_anomalies: %d alert(s) for %s vs %s", len(alerts), current.label, prior.label)
    return AnomalyDetectionResult(alerts=alerts)
