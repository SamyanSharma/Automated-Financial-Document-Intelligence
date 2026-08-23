def calculate_risk_score(
    revenue_change: float | None,
    debt_change: float | None,
    liability_change: float | None,
    anomaly_count: int
):

    score = 0


    # Revenue decline risk
    if revenue_change is not None:

        if revenue_change < 0:
            score += min(
                abs(revenue_change),
                25
            )


    # Debt increase risk
    if debt_change is not None:

        if debt_change > 0:
            score += min(
                debt_change,
                30
            )


    # Liability increase risk
    if liability_change is not None:

        if liability_change > 0:
            score += min(
                liability_change,
                25
            )


    # Anomaly risk
    score += min(
        anomaly_count * 10,
        20
    )


    # Maximum score
    score = min(score, 100)


    # Risk classification
    if score <= 30:

        level = "LOW"

    elif score <= 60:

        level = "MEDIUM"

    elif score <= 80:

        level = "HIGH"

    else:

        level = "CRITICAL"


    return {

        "risk_score": round(score, 2),

        "risk_level": level

    }