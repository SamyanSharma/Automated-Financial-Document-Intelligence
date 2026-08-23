def calculate_change(
    current_value,
    previous_value
):

    if current_value is None or previous_value is None:
        return {
            "current_value": current_value,
            "previous_value": previous_value,
            "absolute_change": None,
            "percentage_change": None,
            "classification": "Data unavailable"
        }


    absolute_change = current_value - previous_value


    if previous_value != 0:
        percentage_change = (
            absolute_change / previous_value
        ) * 100
    else:
        percentage_change = 0


    return {
        "current_value": current_value,
        "previous_value": previous_value,
        "absolute_change": round(absolute_change,2),
        "percentage_change": round(percentage_change,2),
        "classification": classify_change(
            percentage_change
        )
    }

def classify_change(
    percentage_change: float,
    threshold: float = 5.0
) -> str:

    if percentage_change >= threshold:
        return "significant increase"

    if percentage_change <= -threshold:
        return "significant decrease"

    return "stable"

def analyze_metric(
    current_value: float,
    previous_value: float,
    threshold: float = 5.0
) -> dict:

    result = calculate_change(
        current_value,
        previous_value
    )

    percentage_change = result["percentage_change"]

    if percentage_change is None:
        classification = "undefined"
    else:
        classification = classify_change(
            percentage_change,
            threshold
        )

    result["classification"] = classification

    return result