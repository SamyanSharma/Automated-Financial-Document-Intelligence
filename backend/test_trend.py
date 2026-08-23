from services.trend_analysis_service import analyze_revenue_trend


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


result = analyze_revenue_trend(
    history
)


print(result)