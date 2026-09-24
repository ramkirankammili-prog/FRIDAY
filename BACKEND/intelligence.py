from datetime import datetime


def analyze_incident(logs):
    """
    Analyze related events and generate:
    - Root cause
    - Confidence
    - Evidence
    - Incident story
    """

    database_latency = False
    connection_pool = False
    database_timeout = False
    order_failure = False
    payment_timeout = False
    api_failure = False

    for log in logs:

        event_type = log.get("event_type")

        if event_type == "DB_LATENCY":
            database_latency = True

        elif event_type == "CONNECTION_POOL":
            connection_pool = True

        elif event_type == "DB_TIMEOUT":
            database_timeout = True

        elif event_type == "ORDER_FAILURE":
            order_failure = True

        elif event_type == "PAYMENT_TIMEOUT":
            payment_timeout = True

        elif event_type == "HTTP_500":
            api_failure = True

    evidence = []
    score = 0

    if database_latency:
        evidence.append(
            "Database latency increased"
        )
        score += 20

    if connection_pool:
        evidence.append(
            "Database connection pool reached critical utilization"
        )
        score += 30

    if database_timeout:
        evidence.append(
            "Database connection timeout detected"
        )
        score += 25

    if order_failure:
        evidence.append(
            "Order service started failing after database errors"
        )
        score += 10

    if payment_timeout:
        evidence.append(
            "Payment requests timed out downstream"
        )
        score += 10

    if api_failure:
        evidence.append(
            "API gateway returned HTTP 500 errors"
        )
        score += 5

    # Determine likely root cause
    if database_timeout and connection_pool:

        root_cause = "Database connection pool saturation"

        story = (
            "The incident most likely originated in the database layer. "
            "Increasing database latency caused the connection pool to "
            "approach saturation, resulting in database connection timeouts. "
            "These failures propagated to the Order Service, followed by "
            "Payment Service timeouts and API HTTP 500 errors."
        )

    elif database_latency:

        root_cause = "Abnormally high database latency"

        story = (
            "The incident appears to have started with abnormal database "
            "latency. The increased latency affected dependent services "
            "and eventually produced application failures."
        )

    elif payment_timeout:

        root_cause = "Payment service timeout"

        story = (
            "The incident appears to have originated in the Payment Service. "
            "Payment requests began timing out and affected downstream "
            "application operations."
        )

    elif order_failure:

        root_cause = "Order service failure"

        story = (
            "The Order Service experienced failures that affected dependent "
            "operations and contributed to the wider incident."
        )

    else:

        root_cause = "Unknown infrastructure or application issue"

        story = (
            "FRIDAY detected abnormal system activity but does not yet "
            "have enough evidence to determine a reliable root cause."
        )

    confidence = min(score, 99)

    return {
        "root_cause": root_cause,
        "confidence": confidence,
        "evidence": evidence,
        "story": story,
        "analyzed_at": datetime.now().strftime("%H:%M:%S")
    }