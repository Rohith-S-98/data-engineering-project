from __future__ import annotations

import csv
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from scripts.database_ingestion import (
    DatabaseIngestionConfigError,
    DatabaseIngestionSourceError,
    extract_database_records,
    load_database_config,
    run_database_ingestion,
    validate_database_config,
)


class TestV21DatabaseIngestion(unittest.TestCase):
    def test_run_database_ingestion_seeds_and_writes_customer_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            database_path = root / "customer_source.db"
            target_path = root / "customer_data_db.csv"
            config_path = root / "customer_database_ingestion_config.json"
            config_path.write_text(json.dumps(_build_config(database_path, target_path)), encoding="utf-8")

            summary = run_database_ingestion(config_path)

            self.assertEqual(summary.source_name, "unit_test_customer_db")
            self.assertEqual(summary.database_type, "sqlite")
            self.assertEqual(summary.source_table, "source_customers")
            self.assertEqual(summary.records_written, 2)
            self.assertTrue(database_path.exists())
            self.assertTrue(target_path.exists())

            with target_path.open("r", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["customer_id"], "CUST701")
            self.assertEqual(rows[0]["source_system"], "DB")

    def test_extract_database_records_reads_existing_sqlite_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            database_path = root / "existing.db"
            target_path = root / "target.csv"
            config = _build_config(database_path, target_path)
            config["seed_source"]["enabled"] = False

            _create_existing_database(database_path)

            records = extract_database_records(config)

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["customer_id"], "CUST801")
            self.assertEqual(records[0]["city"], "Pune")

    def test_load_database_config_validates_required_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "bad_config.json"
            config_path.write_text(json.dumps({"source_name": "bad"}), encoding="utf-8")

            with self.assertRaises(DatabaseIngestionConfigError):
                load_database_config(config_path)

    def test_missing_database_file_raises_source_error(self):
        config = _build_config(Path("missing.db"), Path("target.csv"))
        config["seed_source"]["enabled"] = False

        with self.assertRaises(DatabaseIngestionSourceError):
            extract_database_records(config)

    def test_validate_database_config_rejects_non_select_query(self):
        config = _build_config(Path("source.db"), Path("target.csv"))
        config["extract_query"] = "DELETE FROM source_customers"

        with self.assertRaises(DatabaseIngestionConfigError):
            validate_database_config(config)

    def test_validate_database_config_rejects_non_sqlite_source(self):
        config = _build_config(Path("source.db"), Path("target.csv"))
        config["database_type"] = "postgres"

        with self.assertRaises(DatabaseIngestionConfigError):
            validate_database_config(config)


def _build_config(database_path: Path, target_path: Path) -> dict:
    return {
        "source_name": "unit_test_customer_db",
        "enabled": True,
        "database_type": "sqlite",
        "database_path": str(database_path),
        "source_table": "source_customers",
        "extract_query": "SELECT customer_id, first_name, last_name, email, phone, city, state, created_date, source_system FROM source_customers ORDER BY customer_id",
        "target_csv_path": str(target_path),
        "target_columns": [
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "state",
            "created_date",
            "source_system",
        ],
        "seed_source": {
            "enabled": True,
            "rows": [
                {
                    "customer_id": "CUST701",
                    "first_name": "Arjun",
                    "last_name": "N",
                    "email": "arjun.n@example.com",
                    "phone": "9876500701",
                    "city": "Bengaluru",
                    "state": "Karnataka",
                    "created_date": "2026-06-26",
                    "source_system": "DB",
                },
                {
                    "customer_id": "CUST702",
                    "first_name": "Meera",
                    "last_name": "Joshi",
                    "email": "meera.joshi@example.com",
                    "phone": "9876500702",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "created_date": "2026-06-26",
                    "source_system": "DB",
                },
            ],
        },
    }


def _create_existing_database(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            """
            CREATE TABLE source_customers (
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
        )
        connection.execute(
            """
            INSERT INTO source_customers VALUES (
                'CUST801',
                'Neha',
                'Patil',
                'neha.patil@example.com',
                '9876500801',
                'Pune',
                'Maharashtra',
                '2026-06-26',
                'DB'
            )
            """
        )
        connection.commit()


if __name__ == "__main__":
    unittest.main()
