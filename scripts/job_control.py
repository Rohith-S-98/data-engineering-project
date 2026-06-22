from __future__ import annotations

import csv
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

JOB_RUN_COLUMNS = [
    "job_run_id",
    "job_name",
    "environment",
    "start_time",
    "end_time",
    "status",
    "total_steps",
    "successful_steps",
    "failed_steps",
    "skipped_steps",
    "error_message",
]

STEP_RUN_COLUMNS = [
    "job_run_id",
    "step_id",
    "step_name",
    "module",
    "function",
    "critical",
    "enabled",
    "start_time",
    "end_time",
    "status",
    "result_status",
    "error_message",
]

DEFAULT_JOB_RUN_LOG_FILE = "output/job_control/job_runs.csv"
DEFAULT_STEP_RUN_LOG_FILE = "output/job_control/step_runs.csv"


def get_current_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _read_csv_rows(file_path: str, fieldnames: list[str]) -> list[dict[str, Any]]:
    path = Path(file_path)

    if not path.exists():
        return []

    with path.open(mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    return rows


def _write_csv_rows(
    file_path: str,
    fieldnames: list[str],
    rows: list[dict[str, Any]],
) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _append_csv_row(
    file_path: str,
    fieldnames: list[str],
    row: dict[str, Any],
) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = path.exists()

    with path.open(mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


def create_job_run(
    job_name: str,
    environment: str,
    job_run_log_file: str = DEFAULT_JOB_RUN_LOG_FILE,
) -> str:
    job_run_id = str(uuid.uuid4())

    _append_csv_row(
        file_path=job_run_log_file,
        fieldnames=JOB_RUN_COLUMNS,
        row={
            "job_run_id": job_run_id,
            "job_name": job_name,
            "environment": environment,
            "start_time": get_current_timestamp(),
            "end_time": "",
            "status": "STARTED",
            "total_steps": "",
            "successful_steps": "",
            "failed_steps": "",
            "skipped_steps": "",
            "error_message": "",
        },
    )

    return job_run_id


def update_job_run(
    job_run_id: str,
    status: str,
    total_steps: int,
    successful_steps: int,
    failed_steps: int,
    skipped_steps: int,
    error_message: str = "",
    job_run_log_file: str = DEFAULT_JOB_RUN_LOG_FILE,
) -> None:
    rows = _read_csv_rows(
        file_path=job_run_log_file,
        fieldnames=JOB_RUN_COLUMNS,
    )

    updated = False

    for row in rows:
        if row["job_run_id"] == job_run_id:
            row["end_time"] = get_current_timestamp()
            row["status"] = status
            row["total_steps"] = total_steps
            row["successful_steps"] = successful_steps
            row["failed_steps"] = failed_steps
            row["skipped_steps"] = skipped_steps
            row["error_message"] = error_message
            updated = True

    if not updated:
        raise ValueError(f"Job run not found: {job_run_id}")

    _write_csv_rows(
        file_path=job_run_log_file,
        fieldnames=JOB_RUN_COLUMNS,
        rows=rows,
    )


def create_step_run(
    job_run_id: str,
    step_config: dict[str, Any],
    step_run_log_file: str = DEFAULT_STEP_RUN_LOG_FILE,
) -> None:
    _append_csv_row(
        file_path=step_run_log_file,
        fieldnames=STEP_RUN_COLUMNS,
        row={
            "job_run_id": job_run_id,
            "step_id": step_config["step_id"],
            "step_name": step_config["step_name"],
            "module": step_config["module"],
            "function": step_config["function"],
            "critical": step_config.get("critical", True),
            "enabled": step_config.get("enabled", True),
            "start_time": get_current_timestamp(),
            "end_time": "",
            "status": "STARTED",
            "result_status": "",
            "error_message": "",
        },
    )


def update_step_run(
    job_run_id: str,
    step_id: int,
    status: str,
    result_status: str = "",
    error_message: str = "",
    step_run_log_file: str = DEFAULT_STEP_RUN_LOG_FILE,
) -> None:
    rows = _read_csv_rows(
        file_path=step_run_log_file,
        fieldnames=STEP_RUN_COLUMNS,
    )

    updated = False

    for row in rows:
        if row["job_run_id"] == job_run_id and str(row["step_id"]) == str(step_id):
            row["end_time"] = get_current_timestamp()
            row["status"] = status
            row["result_status"] = result_status
            row["error_message"] = error_message
            updated = True

    if not updated:
        raise ValueError(
            f"Step run not found for job_run_id={job_run_id}, step_id={step_id}"
        )

    _write_csv_rows(
        file_path=step_run_log_file,
        fieldnames=STEP_RUN_COLUMNS,
        rows=rows,
    )
