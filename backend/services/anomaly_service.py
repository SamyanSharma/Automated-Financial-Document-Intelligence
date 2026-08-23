import statistics


def calculate_z_score(
    current_value: float,
    historical_values: list[float]
):

    mean = statistics.mean(
        historical_values
    )

    std = statistics.stdev(
        historical_values
    )

    if std == 0:
        return 0

    z_score = (
        current_value - mean
    ) / std

    return z_score



def detect_anomaly(
    current_value: float,
    historical_values: list[float],
    threshold: float = 2
):

    z_score = calculate_z_score(
        current_value,
        historical_values
    )

    is_anomaly = (
        abs(z_score) > threshold
    )


    return {

        "current_value": current_value,

        "mean": statistics.mean(
            historical_values
        ),

        "z_score": z_score,

        "is_anomaly": is_anomaly,

        "severity":
            "HIGH"
            if abs(z_score) > 3
            else "MEDIUM"
            if abs(z_score) > 2
            else "NORMAL"
    }