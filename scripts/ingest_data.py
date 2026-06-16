import csv
from pathlib import Path


RAW_DATA_FILE = Path("data/raw/customer_data.csv")
PROCESSED_DATA_DIR = Path("data/processed")
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "customer_data_processed.csv"

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
        reader = csv.DictReader(file)
        return list(reader)


def validate_columns(rows: list[dict]) -> None:
    if not rows:
        raise ValueError("Input file is empty.")

    actual_columns = list(rows[0].keys())
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in actual_columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def remove_duplicates(rows: list[dict]) -> list[dict]:
    seen_customer_ids = set()
    unique_rows = []

    for row in rows:
        customer_id = row["customer_id"]

        if customer_id not in seen_customer_ids:
            unique_rows.append(row)
            seen_customer_ids.add(customer_id)

    return unique_rows


def identify_invalid_rows(rows: list[dict]) -> list[dict]:
    invalid_rows = []

    for row in rows:
        if not row["customer_id"] or not row["email"] or not row["phone"]:
            invalid_rows.append(row)

    return invalid_rows


def write_csv(rows: list[dict], output_file: Path) -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def ingest_customer_data() -> None:
    print("Starting customer data ingestion...")

    rows = read_csv(RAW_DATA_FILE)
    print(f"Raw row count: {len(rows)}")

    validate_columns(rows)

    duplicate_removed_rows = remove_duplicates(rows)
    print(f"Row count after duplicate removal: {len(duplicate_removed_rows)}")

    invalid_rows = identify_invalid_rows(duplicate_removed_rows)
    print(f"Invalid row count: {len(invalid_rows)}")

    valid_rows = [
        row for row in duplicate_removed_rows
        if row not in invalid_rows
    ]

    write_csv(valid_rows, PROCESSED_DATA_FILE)

    print(f"Valid row count written: {len(valid_rows)}")
    print(f"Processed file created at: {PROCESSED_DATA_FILE}")


if __name__ == "__main__":
    ingest_customer_data()