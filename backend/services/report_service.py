from services.financial_engine_service import run_financial_analysis


def generate_financial_report(financial_data: dict):

    analysis = run_financial_analysis(
        financial_data
    )


    report = {

        "company":
        financial_data.get(
            "company_name",
            "Unknown"
        ),


        "financial_analysis":
        analysis,


        "summary":

        generate_summary(analysis)

    }


    return report



def generate_summary(
    analysis: dict
):

    risk = analysis["risk_assessment"]


    return f"""
Financial analysis completed.

Overall risk level:
{risk['risk_level']}

Risk score:
{risk['risk_score']}/100

Revenue status:
{analysis['revenue_analysis']['classification']}

Debt status:
{analysis['debt_analysis']['classification']}

Liability status:
{analysis['liability_analysis']['classification']}
"""