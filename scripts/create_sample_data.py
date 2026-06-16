import csv
from pathlib import Path


RAW_DATA_DIR = Path("data/raw")
RAW_DATA_FILE = RAW_DATA_DIR / "customer_data.csv"


sample_customers = [
    {
        "customer_id": "CUST001",
        "first_name": "Rohith",
        "last_name": "S",
        "email": "rohith@example.com",
        "phone": "9876543210",
        "city": "Bengaluru",
        "state": "Karnataka",
        "created_date": "2026-06-16",
        "source_system": "CSV",
    },
    {
        "customer_id": "CUST002",
        "first_name": "Anil",
        "last_name": "Kumar",
        "email": "anil@example.com",
        "phone": "9876543211",
        "city": "Kolar",
        "state": "Karnataka",
        "created_date": "2026-06-16",
        "source_system": "API",
    },
    {
        "customer_id": "CUST003",
        "first_name": "Megha",
        "last_name": "Rao",
        "email": "",
        "phone": "9876543212",
        "city": "Mysuru",
        "state": "Karnataka",
        "created_date": "2026-06-16",
        "source_system": "CSV",
    },
    {
        "customer_id": "CUST004",
        "first_name": "Suresh",
        "last_name": "M",
        "email": "suresh@example.com",
        "phone": "",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "created_date": "2026-06-16",
        "source_system": "API",
    },
    {
        "customer_id": "CUST002",
        "first_name": "Anil",
        "last_name": "Kumar",
        "email": "anil@example.com",
        "phone": "9876543211",
        "city": "Kolar",
        "state": "Karnataka",
        "created_date": "2026-06-16",
        "source_system": "API",
    },
]


def create_raw_customer_data() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(RAW_DATA_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=sample_customers[0].keys())
        writer.writeheader()
        writer.writerows(sample_customers)

    print(f"Raw customer data created successfully at: {RAW_DATA_FILE}")


if __name__ == "__main__":
    create_raw_customer_data()