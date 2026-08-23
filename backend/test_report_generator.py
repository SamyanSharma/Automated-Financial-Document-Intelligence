from services.report_generator_service import generate_financial_report



history = [

{
"year":"2020",
"revenue":274
},

{
"year":"2021",
"revenue":365
},

{
"year":"2022",
"revenue":394
},

{
"year":"2023",
"revenue":383
}

]


financial_data = {


"revenue_current":394,

"revenue_previous":383,


"debt_current":106,

"debt_previous":110,


"liability_current":290,

"liability_previous":290,


"revenue_history":[
274,
365,
394,
383
]

}



report = generate_financial_report(

    company_name="Apple Inc.",

    history=history,

    financial_data=financial_data

)


print(report)