def calculate_cagr(
    start_value: float,
    end_value: float,
    years: int
):

    if start_value <= 0 or years <= 0:
        return None


    cagr = (
        (end_value / start_value)
        ** (1 / years)
        - 1
    ) * 100


    return round(cagr, 2)



def calculate_growth_rates(
    values: list[float]
):

    growth_rates = []


    for i in range(1, len(values)):

        previous = values[i-1]

        current = values[i]


        if previous == 0:
            continue


        growth = (
            (current - previous)
            / previous
        ) * 100


        growth_rates.append(
            round(growth,2)
        )


    return growth_rates



def classify_trend(
    growth_rates:list[float]
):

    if not growth_rates:
        return "Unknown"


    average_growth = (
        sum(growth_rates)
        /
        len(growth_rates)
    )


    if average_growth > 5:
        return "Growing"


    elif average_growth < -5:
        return "Declining"


    else:
        return "Stable"



def analyze_revenue_trend(
    history:list[dict]
):

    revenue_values = [
        item["revenue"]
        for item in history
        if item["revenue"] is not None
    ]


    years = len(revenue_values)-1


    cagr = calculate_cagr(
        revenue_values[0],
        revenue_values[-1],
        years
    )


    growth_rates = calculate_growth_rates(
        revenue_values
    )


    trend = classify_trend(
        growth_rates
    )


    return {

        "start_revenue":
        revenue_values[0],


        "end_revenue":
        revenue_values[-1],


        "cagr":
        cagr,


        "yearly_growth":
        growth_rates,


        "trend":
        trend

    }