from services.financial_engine_service import run_financial_analysis


financial_data = {

    "revenue_current":394.3,

    "revenue_previous":383.3,


    "debt_current":150,

    "debt_previous":100,


    "liability_current":290,

    "liability_previous":250,


    "revenue_history":[
        350,
        370,
        380,
        383
    ]
}



result = run_financial_analysis(
    financial_data
)


print(result)