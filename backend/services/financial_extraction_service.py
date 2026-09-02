import json
import re

from services.llm_service import generate_json


def clean_json_response(response: str):
    """
    Remove markdown code blocks from Gemini response.
    """

    response = response.replace("```json", "")
    response = response.replace("```", "")

    return response.strip()


def clean_string(value):
    """
    Clean string values returned by Gemini.
    """

    if value is None:
        return None

    value = str(value).strip()

    invalid_values = [
        "",
        "Not specified",
        "not specified",
        "NOT SPECIFIED",
        "Unknown",
        "unknown",
        "N/A",
        "n/a",
        "None",
        "none"
    ]

    if value in invalid_values:
        return None

    return value


def clean_number(value):
    """
    Convert Gemini financial values into float.

    Examples:
        394.3
        "394.3"
        "394.3 billion dollars"
        "1,234.5 million"
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    # Remove commas
    value = value.replace(",", "")

    # Find integer or decimal number
    match = re.search(
        r"-?\d+(?:\.\d+)?",
        value
    )

    if match:
        try:
            return float(match.group())
        except ValueError:
            return None

    return None


def extract_year_from_context(context: str):
    """
    Fallback year extraction.

    If Gemini fails to provide financial_year,
    search the document context for a likely reporting year.
    """

    if not context:
        return None

    # Look for common financial-report wording
    patterns = [
        r"(?:fiscal year|financial year|year ended|year ending)\s+(?:on\s+)?(?:December\s+\d{1,2},\s+)?(20\d{2})",
        r"(?:FY|Fiscal Year)\s*(20\d{2})",
        r"(20\d{2})\s+Annual Report",
        r"Annual Report.*?(20\d{2})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            context,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    # Final fallback:
    # collect years and use the most recent one
    years = re.findall(
        r"\b(20\d{2})\b",
        context
    )

    if years:
        valid_years = [
            int(year)
            for year in years
            if 2000 <= int(year) <= 2100
        ]

        if valid_years:
            return str(max(valid_years))

    return None


def extract_financial_metrics(
    context: str
):

    prompt = f"""
Extract financial information from the financial document below.

Return ONLY valid JSON.

Do NOT return markdown.
Do NOT return an explanation.
Do NOT add extra fields.

Required fields:

company_name
financial_year
revenue
total_assets
total_liabilities
debt
cash_flow


IMPORTANT INSTRUCTIONS FOR financial_year:

1. Find the reporting year from the document itself.
2. Check the document title, annual report title,
   reporting period, financial statements, and
   "year ended" sections.
3. financial_year MUST be a four-digit year such as:
   2020, 2021, 2022, 2023, or 2024.
4. Do NOT return "Not specified" if a reporting year
   can be determined from the document.
5. Only return null for financial_year if the document
   genuinely does not provide enough information.


IMPORTANT INSTRUCTIONS FOR FINANCIAL VALUES:

1. Extract the actual reported financial values.
2. Do not invent missing values.
3. If a value is unavailable, return null.
4. Keep values in the same unit used by the document.
5. Return numeric values whenever possible.


Expected JSON format:

{{
    "company_name": "Apple Inc.",
    "financial_year": "2023",
    "revenue": 383.3,
    "total_assets": 352.6,
    "total_liabilities": 290.0,
    "debt": null,
    "cash_flow": null
}}


DOCUMENT:

{context}
"""

    result = generate_json(prompt)

    print("RAW GEMINI:")
    print(result)

    # --------------------------------------------------
    # Clean Gemini response
    # --------------------------------------------------

    result = clean_json_response(result)

    try:
        metrics = json.loads(result)

    except json.JSONDecodeError:

        print("ERROR: Gemini returned invalid JSON")

        return {
            "company_name": None,
            "financial_year": extract_year_from_context(context),
            "revenue": None,
            "total_assets": None,
            "total_liabilities": None,
            "debt": None,
            "cash_flow": None
        }

    # --------------------------------------------------
    # Extract and clean year
    # --------------------------------------------------

    financial_year = clean_string(
        metrics.get("financial_year")
    )

    # If Gemini didn't find the year,
    # search the document ourselves.
    if financial_year is None:

        financial_year = extract_year_from_context(
            context
        )

    # --------------------------------------------------
    # Normalize all metrics
    # --------------------------------------------------

    normalized = {

        "company_name": clean_string(
            metrics.get("company_name")
        ),

        "financial_year": financial_year,

        "revenue": clean_number(
            metrics.get("revenue")
        ),

        "total_assets": clean_number(
            metrics.get("total_assets")
        ),

        "total_liabilities": clean_number(
            metrics.get("total_liabilities")
        ),

        "debt": clean_number(
            metrics.get("debt")
        ),

        "cash_flow": clean_number(
            metrics.get("cash_flow")
        )
    }

    print("NORMALIZED FINANCIAL DATA:")
    print(normalized)

    return normalized