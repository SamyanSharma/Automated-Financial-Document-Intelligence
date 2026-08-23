from services.anomaly_service import detect_anomaly



historical_revenue = [
    380,
    390,
    400,
    410,
    420
]


result = detect_anomaly(
    current_value=800,
    historical_values=historical_revenue
)


print(result)