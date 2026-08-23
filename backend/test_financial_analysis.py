from services.financial_analysis_service import analyze_metric


result = analyze_metric(
    current_value=394.3,
    previous_value=383.3
)

print(result)