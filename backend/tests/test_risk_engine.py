from ai.risk_engine import compute_health_score, detect_anomalies
from ai.schemas import FinancialMetrics


def _metrics(label, revenue, net_income, total_assets, total_liabilities, operating_cash_flow):
    return FinancialMetrics(
        label=label,
        revenue=revenue,
        net_income=net_income,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        operating_cash_flow=operating_cash_flow,
    )


def test_health_score_worked_example_from_spec():
    """Matches the docstring's worked example exactly: score should be 80."""
    prior = _metrics("Q3 2024", 100, 8, 200, 90, 5)
    current = _metrics("Q4 2024", 115, 9, 210, 95, 6)

    result = compute_health_score(current, prior)

    assert result.score == 80
    assert "strong" in result.summary.lower()
    assert len(result.factors) == 5  # revenue, profit, debt, ocf, baseline


def test_health_score_penalizes_high_debt_and_negative_cash_flow():
    prior = _metrics("Q3", 100, 8, 200, 90, 5)
    current = _metrics("Q4", 100, 8, 200, 180, -5)  # debt_ratio=90%, ocf negative

    result = compute_health_score(current, prior)

    debt_factor = next(f for f in result.factors if f.name == "Debt Ratio")
    ocf_factor = next(f for f in result.factors if f.name == "Operating Cash Flow")
    assert debt_factor.points == -20
    assert ocf_factor.points == 0
    assert result.score < 80


def test_health_score_clamped_to_valid_range():
    prior = _metrics("P", 100, 100, 100, 10, 100)
    current = _metrics("C", 1000, 1000, 100, 5, 1000)  # everything maxed out positive
    result = compute_health_score(current, prior)
    assert 0 <= result.score <= 100


def test_anomaly_detection_flags_large_net_income_drop():
    """Matches the docstring's worked example: 60% drop should be flagged."""
    prior = _metrics("Q3", 100, 5, 200, 90, 5)
    current = _metrics("Q4", 102, 2, 201, 91, 6)

    result = detect_anomalies(current, prior)

    net_income_alerts = [a for a in result.alerts if a.metric == "Net Income"]
    assert len(net_income_alerts) == 1
    assert net_income_alerts[0].pct_change == -60.0
    assert "60%" in net_income_alerts[0].message


def test_anomaly_detection_no_alerts_for_stable_metrics():
    prior = _metrics("Q3", 100, 8, 200, 90, 5)
    current = _metrics("Q4", 103, 8.2, 202, 91, 5.1)  # all small, normal moves

    result = detect_anomalies(current, prior)
    assert result.alerts == []


def test_anomaly_detection_liability_spike_lower_threshold():
    """Liabilities use a 30% threshold (spec calls out liability spikes
    specifically), lower than the general 50% threshold."""
    prior = _metrics("Q3", 100, 8, 200, 90, 5)
    current = _metrics("Q4", 102, 8.1, 201, 125, 5)  # liabilities +38.9%, revenue +2%

    result = detect_anomalies(current, prior)

    liability_alerts = [a for a in result.alerts if a.metric == "Total Liabilities"]
    revenue_alerts = [a for a in result.alerts if a.metric == "Revenue"]
    assert len(liability_alerts) == 1
    assert revenue_alerts == []  # +2% doesn't cross the 50% general threshold


def test_anomaly_detection_zscore_with_history():
    prior = _metrics("Q3", 100, 8, 200, 90, 5)
    current = _metrics("Q4", 400, 8, 200, 90, 5)  # revenue way outside historical pattern
    history = [
        _metrics("Q0", 98, 8, 200, 90, 5),
        _metrics("Q1", 101, 8, 200, 90, 5),
        _metrics("Q2", 99, 8, 200, 90, 5),
    ]

    result = detect_anomalies(current, prior, history=history)
    revenue_alerts = [a for a in result.alerts if a.metric == "Revenue"]
    assert len(revenue_alerts) >= 1


def test_pct_change_handles_zero_prior_without_crashing():
    prior = _metrics("Q3", 0, 0, 100, 50, 0)
    current = _metrics("Q4", 100, 10, 110, 55, 5)
    # Should not raise ZeroDivisionError
    result = compute_health_score(current, prior)
    assert isinstance(result.score, int)
