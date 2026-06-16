import csv
import uuid
from datetime import datetime
from pathlib import Path


AUDIT_COLUMNS = [
    "run_id",
    "pipeline_name",
    "environment",
    "start_time",
    "end_time",
    "status",
    "error_message",
]


def get_current_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def create_pipeline_run(
    pipeline_name: str,
    environment: str,
    audit_log_file: str,
) -> str:
    run_id = str(uuid.uuid4())
    audit_file = Path(audit_log_file)
    audit_file.parent.mkdir(parents=True, exist_ok=True)

    file_exists = audit_file.exists()

    with open(audit_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=AUDIT_COLUMNS)

        if not file_exists:
            writer.writeheader()

        writer.writerow(
            {
                "run_id": run_id,
                "pipeline_name": pipeline_name,
                "environment": environment,
                "start_time": get_current_timestamp(),
                "end_time": "",
                "status": "STARTED",
                "error_message": "",
            }
        )

    return run_id


def update_pipeline_run(
    run_id: str,
    audit_log_file: str,
    status: str,
    error_message: str = "",
) -> None:
    audit_file = Path(audit_log_file)

    if not audit_file.exists():
        raise FileNotFoundError(f"Audit log file not found: {audit_file}")

    with open(audit_file, mode="r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    updated_rows = []

    for row in rows:
        if row["run_id"] == run_id:
            row["end_time"] = get_current_timestamp()
            row["status"] = status
            row["error_message"] = error_message

        updated_rows.append(row)

    with open(audit_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=AUDIT_COLUMNS)
        writer.writeheader()
        writer.writerows(updated_rows)