from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATH = Path("config/database/customer_database_ingestion_config.json")


@dataclass(frozen=True)
class DatabaseIngestionSummary:
    source_name: str
    database_type: str
    source_table: str
    records_written: int
    target_csv_path: str


class DatabaseIngestionConfigError(ValueError):
    """Raised when database ingestion configuration is invalid."""


class DatabaseIngestionSourceError(RuntimeError):
    """Raised when source database extraction fails."""


REQUIRED_CONFIG_KEYS = {
    "source_name",
    "enabled",
    "database_type",
    "database_path",
    "source_table",
    "extract_query",
    "target_csv_path",
    "target_columns",
}


CREATE_CUSTOMER_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS source_customers (
    customer_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    created_date TEXT NOT NULL,
    source_system TEXT NOT NULL
)
"""


def load_json(path: Path | str) -> dict[str, Any]:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_database_config(config: dict[str, Any]) -> None:
    missing_keys = sorted(REQUIRED_CONFIG_KEYS - set(config))
    if missing_keys:
        raise DatabaseIngestionConfigError(f"Missing database config keys: {missing_keys}")

    if config["database_type"] != "sqlite":
        raise DatabaseIngestionConfigError("Only sqlite database_type is supported for local V21 validation")

    if not isinstance(config["target_columns"], list) or not config["target_columns"]:
        raise DatabaseIngestionConfigError("target_columns must be a non-empty list")

    extract_query = str(config["extract_query"]).strip().lower()
    if not extract_query.startswith("select"):
        raise DatabaseIngestionConfigError("extract_query must be a SELECT statement")


def load_database_config(config_path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    config = load_json(config_path)
    validate_database_config(config)
    return config


def seed_sqlite_source_database(config: dict[str, Any]) -> None:
    seed_config = config.get("seed_source", {})
    if not seed_config.get("enabled", False):
        return

    database_path = Path(config["database_path"])
    database_path.parent.mkdir(parents=True, exist_ok=True)

    rows = seed_config.get("rows", [])
    if not isinstance(rows, list):
        raise DatabaseIngestionConfigError("seed_source.rows must be a list")

    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(f"DROP TABLE IF EXISTS {config['source_table']}")
        connection.execute(CREATE_CUSTOMER_TABLE_SQL.replace("source_customers", config["source_table"]))
        connection.executemany(
            f"""
            INSERT INTO {config['source_table']} (
                customer_id,
                first_name,
                last_name,
                email,
                phone,
                city,
                state,
                created_date,
                source_system
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row["customer_id"],
                    row["first_name"],
                    row["last_name"],
                    row["email"],
                    row["phone"],
                    row["city"],
                    row["state"],
                    row["created_date"],
                    row["source_system"],
                )
                for row in rows
            ],
        )
        connection.commit()


def extract_database_records(config: dict[str, Any]) -> list[dict[str, str]]:
    if not config.get("enabled", False):
        return []

    database_path = Path(config["database_path"])
    if not database_path.exists():
        raise DatabaseIngestionSourceError(f"Source database file not found: {database_path}")

    try:
        with closing(sqlite3.connect(database_path)) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(config["extract_query"]).fetchall()
    except sqlite3.Error as exc:
        raise DatabaseIngestionSourceError(f"Database extraction failed: {exc}") from exc

    records: list[dict[str, str]] = []
    for row in rows:
        records.append({column: "" if row[column] is None else str(row[column]) for column in config["target_columns"]})
    return records


def write_records_to_csv(records: list[dict[str, str]], target_columns: list[str], target_path: Path | str) -> None:
    file_path = Path(target_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=target_columns)
        writer.writeheader()
        writer.writerows(records)


def run_database_ingestion(config_path: Path | str = DEFAULT_CONFIG_PATH) -> DatabaseIngestionSummary:
    config = load_database_config(config_path)
    seed_sqlite_source_database(config)
    records = extract_database_records(config)
    write_records_to_csv(records, config["target_columns"], config["target_csv_path"])

    return DatabaseIngestionSummary(
        source_name=config["source_name"],
        database_type=config["database_type"],
        source_table=config["source_table"],
        records_written=len(records),
        target_csv_path=config["target_csv_path"],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V21 database ingestion framework.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to database ingestion config JSON.")
    args = parser.parse_args()

    summary = run_database_ingestion(args.config)
    print("Database ingestion SUCCESS")
    print(f"Source name    : {summary.source_name}")
    print(f"Database type  : {summary.database_type}")
    print(f"Source table   : {summary.source_table}")
    print(f"Records written: {summary.records_written}")
    print(f"Target CSV     : {summary.target_csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
