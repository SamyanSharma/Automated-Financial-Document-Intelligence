from services.report_service import generate_financial_report


financial_data = {


    "company_name":"Apple",


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


report = generate_financial_report(
    financial_data
)


print(report)