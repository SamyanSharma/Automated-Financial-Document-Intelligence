from services.risk_service import calculate_risk_score


result = calculate_risk_score(

    revenue_change=-15,

    debt_change=30,

    liability_change=20,

    anomaly_count=2

)


print(result)