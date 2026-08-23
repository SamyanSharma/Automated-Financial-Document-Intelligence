from services.financial_analysis_service import analyze_metric
from services.anomaly_service import detect_anomaly
from services.risk_service import calculate_risk_score



def create_empty_analysis(
    current_value,
    previous_value
):

    return {

        "current_value": current_value,

        "previous_value": previous_value,

        "absolute_change": None,

        "percentage_change": None,

        "classification": "Data unavailable"

    }



def run_financial_analysis(
    financial_data: dict
):


    # Revenue Analysis


    if (
        financial_data.get("revenue_current") is not None
        and financial_data.get("revenue_previous") is not None
    ):

        revenue_analysis = analyze_metric(
            current_value=
            financial_data["revenue_current"],

            previous_value=
            financial_data["revenue_previous"]
        )

    else:

        revenue_analysis = create_empty_analysis(
            financial_data.get("revenue_current"),
            financial_data.get("revenue_previous")
        )




    # Debt Analysis


    if (
        financial_data.get("debt_current") is not None
        and financial_data.get("debt_previous") is not None
    ):

        debt_analysis = analyze_metric(
            current_value=
            financial_data["debt_current"],

            previous_value=
            financial_data["debt_previous"]
        )

    else:

        debt_analysis = create_empty_analysis(
            financial_data.get("debt_current"),
            financial_data.get("debt_previous")
        )



    # Liability Analysis

    if (
        financial_data.get("liability_current") is not None
        and financial_data.get("liability_previous") is not None
    ):

        liability_analysis = analyze_metric(
            current_value=
            financial_data["liability_current"],

            previous_value=
            financial_data["liability_previous"]
        )

    else:

        liability_analysis = create_empty_analysis(
            financial_data.get("liability_current"),
            financial_data.get("liability_previous")
        )



  
    # Anomaly Detection


    revenue_anomaly = detect_anomaly(
        current_value=
        financial_data.get("revenue_current"),

        historical_values=
        financial_data.get(
            "revenue_history",
            []
        )
    )


    anomaly_count = 0


    if revenue_anomaly["is_anomaly"]:
        anomaly_count += 1



    #Risk Score

    risk = calculate_risk_score(

        revenue_change=
        revenue_analysis.get(
            "percentage_change"
        ),


        debt_change=
        debt_analysis.get(
            "percentage_change"
        ),


        liability_change=
        liability_analysis.get(
            "percentage_change"
        ),


        anomaly_count=
        anomaly_count

    )



    return {

        "revenue_analysis":
        revenue_analysis,


        "debt_analysis":
        debt_analysis,


        "liability_analysis":
        liability_analysis,


        "anomaly_detection":
        revenue_anomaly,


        "risk_assessment":
        risk

    }