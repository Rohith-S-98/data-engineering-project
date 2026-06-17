import csv
import shutil
from pathlib import Path

RAW_DATA_DIR = Path("data/raw")
RAW_DATA_FILE = RAW_DATA_DIR / "customer_data.csv"
CLEAN_RAW_DATA_FILE = RAW_DATA_DIR / "customer_data_clean.csv"
DIRTY_RAW_DATA_FILE = RAW_DATA_DIR / "customer_data_dirty.csv"

CUSTOMER_COLUMNS = [
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

CLEAN_CUSTOMERS = [
    ["CUST001", "Rohith", "S", "rohith@example.com", "9876543210", "Bengaluru", "Karnataka", "2026-06-16", "CSV"],
    ["CUST002", "Anil", "Kumar", "anil@example.com", "9876543211", "Kolar", "Karnataka", "2026-06-16", "API"],
    ["CUST003", "Megha", "Rao", "megha@example.com", "9876543212", "Mysuru", "Karnataka", "2026-06-16", "CSV"],
    ["CUST004", "Suresh", "M", "suresh@example.com", "9876543213", "Chennai", "Tamil Nadu", "2026-06-16", "API"],
]

DIRTY_CUSTOMERS = [
    ["CUST001", "Rohith", "S", "rohith@example.com", "9876543210", "Bengaluru", "Karnataka", "2026-06-16", "CSV"],
    ["CUST002", "Anil", "Kumar", "anil@example.com", "9876543211", "Kolar", "Karnataka", "2026-06-16", "API"],
    ["CUST003", "Megha", "Rao", "", "9876543212", "Mysuru", "Karnataka", "2026-06-16", "CSV"],
    ["CUST004", "Suresh", "M", "suresh@example.com", "", "Chennai", "Tamil Nadu", "2026-06-16", "API"],
    ["CUST002", "Anil", "Kumar", "anil@example.com", "9876543211", "Kolar", "Karnataka", "2026-06-16", "API"],
]


def write_customer_csv(file_path: Path, rows: list[list[str]]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(CUSTOMER_COLUMNS)
        writer.writerows(rows)


def create_raw_customer_data(use_dirty_data: bool = False) -> None:
    """
    Create clean and dirty sample datasets.

    The default active file is clean so the end-to-end PySpark pipeline can reach Gold.
    Dirty data remains available for demonstrating DQ quarantine and failure control.
    """
    write_customer_csv(CLEAN_RAW_DATA_FILE, CLEAN_CUSTOMERS)
    write_customer_csv(DIRTY_RAW_DATA_FILE, DIRTY_CUSTOMERS)

    source_file = DIRTY_RAW_DATA_FILE if use_dirty_data else CLEAN_RAW_DATA_FILE
    shutil.copyfile(source_file, RAW_DATA_FILE)

    print(f"Clean sample data available at: {CLEAN_RAW_DATA_FILE}")
    print(f"Dirty sample data available at: {DIRTY_RAW_DATA_FILE}")
    print(f"Active raw customer data created at: {RAW_DATA_FILE}")


if __name__ == "__main__":
    create_raw_customer_data()
