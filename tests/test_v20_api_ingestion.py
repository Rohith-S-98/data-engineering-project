from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_ingestion import (
    ApiIngestionConfigError,
    ApiIngestionSourceError,
    extract_api_records,
    load_api_config,
    run_api_ingestion,
    validate_api_config,
)


class TestV20ApiIngestion(unittest.TestCase):
    def test_run_api_ingestion_writes_customer_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            mock_path = root / "mock_customer_api_response.json"
            target_path = root / "customer_data_api.csv"
            config_path = root / "customer_api_ingestion_config.json"

            mock_path.write_text(
                json.dumps(
                    {
                        "pages": [
                            {
                                "page_number": 1,
                                "records": [
                                    {
                                        "id": "CUST201",
                                        "firstName": "Kiran",
                                        "lastName": "R",
                                        "emailAddress": "kiran.r@example.com",
                                        "mobileNumber": "9876500201",
                                        "city": "Bengaluru",
                                        "state": "Karnataka",
                                        "createdDate": "2026-06-22",
                                    }
                                ],
                            },
                            {
                                "page_number": 2,
                                "records": [
                                    {
                                        "id": "CUST202",
                                        "firstName": "Leela",
                                        "lastName": "Nair",
                                        "emailAddress": "leela.nair@example.com",
                                        "mobileNumber": "9876500202",
                                        "city": "Kochi",
                                        "state": "Kerala",
                                        "createdDate": "2026-06-23",
                                    }
                                ],
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            config_path.write_text(json.dumps(_build_config(mock_path, target_path)), encoding="utf-8")

            summary = run_api_ingestion(config_path)

            self.assertEqual(summary.source_name, "unit_test_customer_api")
            self.assertEqual(summary.pages_read, 2)
            self.assertEqual(summary.records_written, 2)
            self.assertTrue(target_path.exists())

            with target_path.open("r", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["customer_id"], "CUST201")
            self.assertEqual(rows[0]["source_system"], "API")

    def test_extract_api_records_respects_max_pages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            mock_path = root / "mock.json"
            target_path = root / "target.csv"
            mock_path.write_text(
                json.dumps(
                    {
                        "pages": [
                            {"page_number": 1, "records": [{"id": "CUST301"}]},
                            {"page_number": 2, "records": [{"id": "CUST302"}]},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            config = _build_config(mock_path, target_path)
            config["pagination"]["max_pages"] = 1

            pages_read, records = extract_api_records(config)

            self.assertEqual(pages_read, 1)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["customer_id"], "CUST301")

    def test_load_api_config_validates_required_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "bad_config.json"
            config_path.write_text(json.dumps({"source_name": "bad"}), encoding="utf-8")

            with self.assertRaises(ApiIngestionConfigError):
                load_api_config(config_path)

    def test_missing_mock_api_response_raises_source_error(self):
        config = _build_config(Path("missing_mock.json"), Path("target.csv"))

        with self.assertRaises(ApiIngestionSourceError):
            extract_api_records(config)

    def test_validate_api_config_rejects_invalid_pagination(self):
        config = _build_config(Path("mock.json"), Path("target.csv"))
        config["pagination"]["max_pages"] = 0

        with self.assertRaises(ApiIngestionConfigError):
            validate_api_config(config)


def _build_config(mock_path: Path, target_path: Path) -> dict:
    return {
        "source_name": "unit_test_customer_api",
        "enabled": True,
        "base_url": "mock://unit-test/customers",
        "http_method": "GET",
        "auth_type": "none",
        "pagination": {
            "type": "page_number",
            "page_param": "page",
            "page_size": 2,
            "max_pages": 2,
        },
        "mock_response_path": str(mock_path),
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
        "field_mapping": {
            "id": "customer_id",
            "firstName": "first_name",
            "lastName": "last_name",
            "emailAddress": "email",
            "mobileNumber": "phone",
            "city": "city",
            "state": "state",
            "createdDate": "created_date",
        },
        "default_values": {
            "first_name": "",
            "last_name": "",
            "email": "",
            "phone": "",
            "city": "",
            "state": "",
            "created_date": "",
            "source_system": "API",
        },
    }


if __name__ == "__main__":
    unittest.main()
