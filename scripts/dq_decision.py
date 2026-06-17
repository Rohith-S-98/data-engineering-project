def evaluate_dq_status(rule_summary: list[dict]) -> str:
    """
    Evaluate final DQ status based on severity failures.

    Rules:
    - HIGH severity failure → FAILED
    - MEDIUM/LOW severity failure → SUCCESS_WITH_WARNINGS
    - No failures → SUCCESS
    """

    high_failure_found = False
    warning_failure_found = False

    for rule in rule_summary:
        failed_count = rule["failed_count"]
        severity = rule["severity"]

        if failed_count > 0:
            if severity == "HIGH":
                high_failure_found = True
            elif severity in ["MEDIUM", "LOW"]:
                warning_failure_found = True

    if high_failure_found:
        return "FAILED"

    if warning_failure_found:
        return "SUCCESS_WITH_WARNINGS"

    return "SUCCESS"