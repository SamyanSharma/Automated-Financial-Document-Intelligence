import json
import re

from services.llm_service import generate_json



def clean_json_response(response: str):

    # Remove markdown code blocks

    response = response.replace(
        "```json",
        ""
    )

    response = response.replace(
        "```",
        ""
    )

    return response.strip()



def clean_number(value):

    if value is None:
        return None


    if isinstance(value, (int, float)):
        return float(value)


    match = re.search(
        r"\d+\.?\d*",
        str(value)
    )


    if match:
        return float(match.group())


    return None



def extract_financial_metrics(
    context: str
):

    prompt = f"""

Extract financial information.

Return ONLY JSON.

No markdown.
No explanation.

Fields:

company_name
financial_year
revenue
total_assets
total_liabilities
debt
cash_flow


Document:

{context}

"""


    result = generate_json(prompt)


    print("RAW GEMINI:")
    print(result)


    result = clean_json_response(
        result
    )


    metrics = json.loads(
        result
    )


    normalized = {

        "company_name":
        clean_string(
            metrics.get("company_name")
        ),

        "financial_year":
        clean_string(
            metrics.get("financial_year")
        ),

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


    return normalized
def clean_string(value):

    if value is None:
        return None

    invalid_values = [
        "Not specified",
        "not specified",
        "Unknown",
        "unknown",
        ""
    ]

    if value in invalid_values:
        return None

    return value