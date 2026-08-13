from ai.comparison_engine import compare_reports
from ai.schemas import FinancialMetrics


def test_compare_reports_worked_example_from_spec():
    """Matches the spec's own example: revenue increased 15% from $100M to $115M."""
    prior = FinancialMetrics(label="Q3", revenue=100, net_income=8, total_assets=200,
                              total_liabilities=90, operating_cash_flow=5)
    current = FinancialMetrics(label="Q4", revenue=115, net_income=9, total_assets=210,
                                total_liabilities=95, operating_cash_flow=6)

    result = compare_reports(current, prior)

    revenue_change = next(c for c in result.changes if c.metric == "Revenue")
    assert revenue_change.pct_change == 15.0
    assert revenue_change.insight == "Revenue increased by 15.0% from $100.0M to $115.0M."


def test_compare_reports_handles_decrease():
    prior = FinancialMetrics(label="Q3", revenue=100, net_income=10, total_assets=200,
                              total_liabilities=90, operating_cash_flow=5)
    current = FinancialMetrics(label="Q4", revenue=80, net_income=10, total_assets=200,
                                total_liabilities=90, operating_cash_flow=5)

    result = compare_reports(current, prior)
    revenue_change = next(c for c in result.changes if c.metric == "Revenue")
    assert revenue_change.pct_change == -20.0
    assert "decreased" in revenue_change.insight


def test_compare_reports_zero_prior_does_not_crash():
    prior = FinancialMetrics(label="Q3", revenue=0, net_income=0, total_assets=100,
                              total_liabilities=50, operating_cash_flow=0)
    current = FinancialMetrics(label="Q4", revenue=50, net_income=5, total_assets=105,
                                total_liabilities=52, operating_cash_flow=3)

    result = compare_reports(current, prior)
    assert len(result.changes) == 5  # all 5 metrics present, no crash on div-by-zero


def test_compare_reports_covers_all_expected_metrics():
    prior = FinancialMetrics(label="A", revenue=1, net_income=1, total_assets=1,
                              total_liabilities=1, operating_cash_flow=1)
    current = FinancialMetrics(label="B", revenue=2, net_income=2, total_assets=2,
                                total_liabilities=2, operating_cash_flow=2)

    result = compare_reports(current, prior)
    metric_names = {c.metric for c in result.changes}
    assert metric_names == {"Revenue", "Net Income", "Total Assets", "Total Liabilities", "Operating Cash Flow"}
