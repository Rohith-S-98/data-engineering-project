from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

DEFAULT_RETRY_POLICY_PATH = "config/retries/customer_medallion_retry_policy.json"

RETRY_EVENT_COLUMNS = [
    "event_id",
    "event_timestamp",
    "job_run_id",
    "step_id",
    "step_name",
    "attempt_number",
    "max_retry_attempts",
    "event_type",
    "status",
    "error_type",
    "error_message",
]


def get_current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_retry_policy(
    retry_policy_path: str = DEFAULT_RETRY_POLICY_PATH,
) -> dict[str, Any]:
    path = Path(retry_policy_path)

    if not path.exists():
        return {
            "enabled": False,
            "default_max_retry_attempts": 0,
            "default_retry_delay_seconds": 0,
            "steps": {},
        }

    with path.open(mode="r", encoding="utf-8") as file:
        policy = json.load(file)

    if "enabled" not in policy:
        raise ValueError("Retry policy must contain an 'enabled' flag")

    return policy


def normalize_status(value: Any) -> str:
    if value is None:
        return "SUCCESS"

    return str(value).upper()


def is_expected_status(
    raw_result: Any,
    expected_success_statuses: list[Any],
) -> bool:
    normalized_result = normalize_status(raw_result)
    normalized_expected = [
        "SUCCESS" if status is None else str(status).upper()
        for status in expected_success_statuses
    ]

    if raw_result is None and None in expected_success_statuses:
        return True

    return normalized_result in normalized_expected


def get_step_retry_config(
    step_config: dict[str, Any],
    retry_policy: dict[str, Any],
) -> dict[str, Any]:
    step_name = step_config["step_name"]
    policy_steps = retry_policy.get("steps", {})
    step_policy = policy_steps.get(step_name, {})

    return {
        "retry_enabled": step_policy.get(
            "retry_enabled",
            retry_policy.get("enabled", False),
        ),
        "max_retry_attempts": int(
            step_policy.get(
                "max_retry_attempts",
                retry_policy.get("default_max_retry_attempts", 0),
            )
        ),
        "retry_delay_seconds": float(
            step_policy.get(
                "retry_delay_seconds",
                retry_policy.get("default_retry_delay_seconds", 0),
            )
        ),
    }


def _append_jsonl(file_path: str, record: dict[str, Any]) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(mode="a", encoding="utf-8") as file:
        file.write(json.dumps(record, default=str) + "\n")


def _append_csv(file_path: str, record: dict[str, Any]) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = path.exists()

    with path.open(mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=RETRY_EVENT_COLUMNS)

        if not file_exists:
            writer.writeheader()

        writer.writerow({column: record.get(column, "") for column in RETRY_EVENT_COLUMNS})


def write_retry_event(
    retry_policy: dict[str, Any],
    job_run_id: str,
    step_config: dict[str, Any],
    attempt_number: int,
    max_retry_attempts: int,
    event_type: str,
    status: str,
    error_type: str = "",
    error_message: str = "",
) -> dict[str, Any]:
    event = {
        "event_id": (
            f"{job_run_id}-{step_config['step_id']}-"
            f"{attempt_number}-{event_type}"
        ),
        "event_timestamp": get_current_utc_timestamp(),
        "job_run_id": job_run_id,
        "step_id": step_config["step_id"],
        "step_name": step_config["step_name"],
        "attempt_number": attempt_number,
        "max_retry_attempts": max_retry_attempts,
        "event_type": event_type,
        "status": status,
        "error_type": error_type,
        "error_message": error_message,
    }

    jsonl_file = retry_policy.get("retry_event_jsonl_file")
    csv_file = retry_policy.get("retry_event_csv_file")

    if jsonl_file:
        _append_jsonl(jsonl_file, event)

    if csv_file:
        _append_csv(csv_file, event)

    return event


def should_retry_exception(
    error: Exception,
    retry_policy: dict[str, Any],
) -> bool:
    error_type = type(error).__name__

    non_retryable = set(retry_policy.get("non_retryable_exceptions", []))
    retryable = set(retry_policy.get("retryable_exceptions", []))

    if error_type in non_retryable:
        return False

    return error_type in retryable or "Exception" in retryable


def execute_step_with_retry(
    step_function: Callable[..., Any],
    step_config: dict[str, Any],
    step_kwargs: dict[str, Any],
    job_run_id: str,
    retry_policy: dict[str, Any],
) -> Any:
    retry_config = get_step_retry_config(
        step_config=step_config,
        retry_policy=retry_policy,
    )

    retry_enabled = retry_policy.get("enabled", False) and retry_config["retry_enabled"]
    max_retry_attempts = retry_config["max_retry_attempts"] if retry_enabled else 0
    retry_delay_seconds = retry_config["retry_delay_seconds"]

    expected_statuses = step_config.get("expected_success_statuses", ["SUCCESS"])
    total_attempts = max_retry_attempts + 1

    last_error: Exception | None = None
    last_result: Any = None

    for attempt_number in range(1, total_attempts + 1):
        try:
            last_result = step_function(**step_kwargs)

            if is_expected_status(last_result, expected_statuses):
                if attempt_number > 1:
                    write_retry_event(
                        retry_policy=retry_policy,
                        job_run_id=job_run_id,
                        step_config=step_config,
                        attempt_number=attempt_number,
                        max_retry_attempts=max_retry_attempts,
                        event_type="RECOVERY_SUCCESS",
                        status=normalize_status(last_result),
                    )

                return last_result

            result_status = normalize_status(last_result)

            if attempt_number <= max_retry_attempts:
                write_retry_event(
                    retry_policy=retry_policy,
                    job_run_id=job_run_id,
                    step_config=step_config,
                    attempt_number=attempt_number,
                    max_retry_attempts=max_retry_attempts,
                    event_type="RETRY_ATTEMPT",
                    status=result_status,
                    error_type="UnexpectedStatus",
                    error_message=(
                        f"Step returned status {result_status}; "
                        f"expected one of {expected_statuses}"
                    ),
                )

                if retry_delay_seconds > 0:
                    time.sleep(retry_delay_seconds)

                continue

            write_retry_event(
                retry_policy=retry_policy,
                job_run_id=job_run_id,
                step_config=step_config,
                attempt_number=attempt_number,
                max_retry_attempts=max_retry_attempts,
                event_type="RECOVERY_EXHAUSTED",
                status=result_status,
                error_type="UnexpectedStatus",
                error_message=(
                    f"Step returned status {result_status}; "
                    f"expected one of {expected_statuses}"
                ),
            )

            return last_result

        except Exception as error:
            last_error = error
            error_type = type(error).__name__
            retryable_error = retry_enabled and should_retry_exception(
                error=error,
                retry_policy=retry_policy,
            )

            if retryable_error and attempt_number <= max_retry_attempts:
                write_retry_event(
                    retry_policy=retry_policy,
                    job_run_id=job_run_id,
                    step_config=step_config,
                    attempt_number=attempt_number,
                    max_retry_attempts=max_retry_attempts,
                    event_type="RETRY_ATTEMPT",
                    status="EXCEPTION",
                    error_type=error_type,
                    error_message=str(error),
                )

                if retry_delay_seconds > 0:
                    time.sleep(retry_delay_seconds)

                continue

            event_type = (
                "RECOVERY_EXHAUSTED"
                if retryable_error
                else "NON_RETRYABLE_FAILURE"
            )

            write_retry_event(
                retry_policy=retry_policy,
                job_run_id=job_run_id,
                step_config=step_config,
                attempt_number=attempt_number,
                max_retry_attempts=max_retry_attempts,
                event_type=event_type,
                status="EXCEPTION",
                error_type=error_type,
                error_message=str(error),
            )

            raise

    if last_error is not None:
        raise last_error

    return last_result


def create_replay_request(
    job_run_id: str,
    failed_step_name: str,
    replay_reason: str,
    replay_request_file: str = "output/recovery/replay_requests.jsonl",
) -> dict[str, Any]:
    request = {
        "replay_requested_at": get_current_utc_timestamp(),
        "job_run_id": job_run_id,
        "failed_step_name": failed_step_name,
        "replay_reason": replay_reason,
        "status": "REQUESTED",
    }

    _append_jsonl(replay_request_file, request)

    return request
