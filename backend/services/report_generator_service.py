from services.trend_analysis_service import analyze_revenue_trend
from services.financial_engine_service import run_financial_analysis



def generate_financial_report(
    company_name: str,
    history: list[dict],
    financial_data: dict
):

    # 1. Trend analysis

    revenue_trend = analyze_revenue_trend(
        history
    )


    # 2. Risk analysis

    risk_analysis = run_financial_analysis(
        financial_data
    )


    # 3. Generate findings

    findings = generate_findings(
        revenue_trend,
        risk_analysis
    )


    return {

        "company":
        company_name,


        "analysis_period":
        f"{history[0]['year']} - {history[-1]['year']}",


        "trend_analysis":
        revenue_trend,


        "risk_assessment":
        risk_analysis["risk_assessment"],


        "key_findings":
        findings,


        "summary":
        generate_summary(
            revenue_trend,
            risk_analysis
        )

    }



def generate_findings(
    trend,
    risk
):

    findings = []


    if trend["trend"] == "Growing":

        findings.append(
            "Revenue shows positive long-term growth."
        )


    elif trend["trend"] == "Declining":

        findings.append(
            "Revenue decline requires attention."
        )


    if (
        risk["risk_assessment"]["risk_level"]
        in ["HIGH","CRITICAL"]
    ):

        findings.append(
            "Financial risk indicators detected."
        )


    else:

        findings.append(
            "No critical financial risk detected."
        )


    return findings



def generate_summary(
    trend,
    risk
):

    return f"""

Financial analysis completed.

Revenue trend:
{trend['trend']}

Revenue CAGR:
{trend['cagr']}%

Overall risk:
{risk['risk_assessment']['risk_level']}

Risk score:
{risk['risk_assessment']['risk_score']}/100

"""
