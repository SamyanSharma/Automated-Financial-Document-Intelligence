import re


def clean_number(value):

    if value is None:
        return None


    # If already number
    if isinstance(value, (int, float)):
        return float(value)


    # Extract numeric part
    match = re.search(
        r"[-+]?\d*\.?\d+",
        value
    )


    if match:
        return float(match.group())


    return None



def normalize_financial_metrics(
    metrics: dict
):

    return {

        "company_name":
            metrics.get("company_name"),


        "financial_year":
            metrics.get("financial_year"),


        "revenue":
            clean_number(
                metrics.get("revenue")
            ),


        "total_assets":
            clean_number(
                metrics.get("total_assets")
            ),


        "total_liabilities":
            clean_number(
                metrics.get("total_liabilities")
            ),


        "debt":
            clean_number(
                metrics.get("debt")
            ),


        "cash_flow":
            clean_number(
                metrics.get("cash_flow")
            )
    }