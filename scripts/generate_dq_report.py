import csv
import json
from datetime import datetime
from pathlib import Path


RAW_DATA_FILE = Path("data/raw/customer_data.csv")
DQ_REPORT_DIR = Path("output/dq_reports")
DQ_REPORT_FILE = DQ_REPORT_DIR / "customer_dq_report.json"

REQUIRED_COLUMNS = [
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "phone",
    "city",
    "state",
    "created_date",
    "source_system",
]


def read_csv(file_path: Path) -> list[dict]:
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(file_path, mode="r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def get_duplicate_count(rows: list[dict]) -> int:
    seen_customer_ids = set()
    duplicate_count = 0

    for row in rows:
        customer_id = row["customer_id"]

        if customer_id in seen_customer_ids:
            duplicate_count += 1
        else:
            seen_customer_ids.add(customer_id)

    return duplicate_count


def get_invalid_rows(rows: list[dict]) -> list[dict]:
    invalid_rows = []

    for row in rows:
        if not row["customer_id"] or not row["email"] or not row["phone"]:
            invalid_rows.append(row)

    return invalid_rows


def generate_dq_report() -> None:
    print("Generating DQ report...")

    rows = read_csv(RAW_DATA_FILE)

    raw_row_count = len(rows)
    duplicate_count = get_duplicate_count(rows)
    invalid_rows = get_invalid_rows(rows)
    invalid_row_count = len(invalid_rows)

    valid_row_count = raw_row_count - duplicate_count - invalid_row_count

    dq_status = "PASSED"
    if duplicate_count > 0 or invalid_row_count > 0:
        dq_status = "PASSED_WITH_WARNINGS"

    report = {
        "source_file": str(RAW_DATA_FILE),
        "report_generated_at": datetime.now().isoformat(timespec="seconds"),
        "raw_row_count": raw_row_count,
        "duplicate_count": duplicate_count,
        "invalid_row_count": invalid_row_count,
        "valid_row_count": valid_row_count,
        "dq_status": dq_status,
        "invalid_customer_ids": [
            row.get("customer_id") for row in invalid_rows
        ],
    }

    DQ_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with open(DQ_REPORT_FILE, mode="w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print(f"DQ report created at: {DQ_REPORT_FILE}")


if __name__ == "__main__":
    generate_dq_report()