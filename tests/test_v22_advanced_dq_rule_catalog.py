from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.advanced_dq_rule_catalog import (
    DqRuleCatalogConfigError,
    DqRuleCatalogExecutionError,
    evaluate_rule_catalog,
    load_rule_catalog,
    run_advanced_dq_rule_catalog,
    validate_rule_catalog,
)


class TestV22AdvancedDqRuleCatalog(unittest.TestCase):
    def test_run_advanced_dq_rule_catalog_success_for_clean_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            catalog_path = root / "catalog.json"
            input_path = root / "customers.csv"
            output_path = root / "summary.json"
            catalog_path.write_text(json.dumps(_build_catalog()), encoding="utf-8")
            _write_customer_csv(input_path, _clean_rows())

            summary = run_advanced_dq_rule_catalog(catalog_path, input_path, output_path)

            self.assertEqual(summary.status, "SUCCESS")
            self.assertEqual(summary.total_records, 2)
            self.assertEqual(summary.rules_evaluated, 5)
            self.assertEqual(summary.critical_failures, 0)
            self.assertEqual(summary.warning_failures, 0)
            self.assertTrue(output_path.exists())

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["status"], "SUCCESS")
            self.assertEqual(len(payload["rules"]), 5)

    def test_evaluate_rule_catalog_returns_failed_when_critical_rule_fails(self):
        catalog = _build_catalog()
        records = _clean_rows()
        records.append(
            {
                "customer_id": "CUST1003",
                "email": "bad-email",
                "phone": "9876501003",
                "source_system": "API",
                "created_date": "2026-06-27",
            }
        )

        summary, results = evaluate_rule_catalog(records, catalog)

        self.assertEqual(summary.status, "FAILED")
        self.assertEqual(summary.critical_failures, 1)
        failed_rule_ids = {result.rule_id for result in results if result.failed_count > 0}
        self.assertIn("EMAIL_FORMAT_VALID", failed_rule_ids)

    def test_evaluate_rule_catalog_returns_warning_status_for_warning_only_failure(self):
        catalog = _build_catalog()
        records = _clean_rows()
        records[0]["source_system"] = "LEGACY"

        summary, results = evaluate_rule_catalog(records, catalog)

        self.assertEqual(summary.status, "SUCCESS_WITH_WARNINGS")
        self.assertEqual(summary.critical_failures, 0)
        self.assertEqual(summary.warning_failures, 1)
        failed_rule_ids = {result.rule_id for result in results if result.failed_count > 0}
        self.assertIn("SOURCE_SYSTEM_ALLOWED", failed_rule_ids)

    def test_unique_rule_detects_duplicate_customer_ids(self):
        catalog = _build_catalog()
        records = _clean_rows()
        records.append(records[0].copy())

        summary, results = evaluate_rule_catalog(records, catalog)

        self.assertEqual(summary.status, "FAILED")
        unique_result = next(result for result in results if result.rule_id == "CUST_ID_UNIQUE")
        self.assertEqual(unique_result.failed_count, 2)

    def test_validate_rule_catalog_rejects_missing_regex_pattern(self):
        catalog = _build_catalog()
        catalog["rules"][2].pop("pattern")

        with self.assertRaises(DqRuleCatalogConfigError):
            validate_rule_catalog(catalog)

    def test_load_rule_catalog_rejects_missing_required_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "bad_catalog.json"
            catalog_path.write_text(json.dumps({"catalog_name": "bad"}), encoding="utf-8")

            with self.assertRaises(DqRuleCatalogConfigError):
                load_rule_catalog(catalog_path)

    def test_run_catalog_raises_for_missing_input_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            catalog_path = root / "catalog.json"
            catalog_path.write_text(json.dumps(_build_catalog()), encoding="utf-8")

            with self.assertRaises(DqRuleCatalogExecutionError):
                run_advanced_dq_rule_catalog(catalog_path, root / "missing.csv", root / "summary.json")


def _build_catalog() -> dict:
    return {
        "catalog_name": "unit_test_customer_dq_catalog",
        "dataset_name": "customers",
        "rules": [
            {
                "rule_id": "CUST_ID_REQUIRED",
                "rule_name": "Customer ID must be present",
                "column": "customer_id",
                "rule_type": "not_null",
                "severity": "critical",
                "enabled": True,
            },
            {
                "rule_id": "CUST_ID_UNIQUE",
                "rule_name": "Customer ID must be unique",
                "column": "customer_id",
                "rule_type": "unique",
                "severity": "critical",
                "enabled": True,
            },
            {
                "rule_id": "EMAIL_FORMAT_VALID",
                "rule_name": "Email must match valid email pattern",
                "column": "email",
                "rule_type": "regex",
                "severity": "critical",
                "enabled": True,
                "pattern": r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            },
            {
                "rule_id": "PHONE_LENGTH_VALID",
                "rule_name": "Phone must have minimum 10 characters",
                "column": "phone",
                "rule_type": "min_length",
                "severity": "warning",
                "enabled": True,
                "min_length": 10,
            },
            {
                "rule_id": "SOURCE_SYSTEM_ALLOWED",
                "rule_name": "Source system must be allowed",
                "column": "source_system",
                "rule_type": "allowed_values",
                "severity": "warning",
                "enabled": True,
                "allowed_values": ["CSV", "API", "DB"],
            },
        ],
    }


def _clean_rows() -> list[dict[str, str]]:
    return [
        {
            "customer_id": "CUST1001",
            "email": "customer1@example.com",
            "phone": "9876501001",
            "source_system": "CSV",
            "created_date": "2026-06-27",
        },
        {
            "customer_id": "CUST1002",
            "email": "customer2@example.com",
            "phone": "9876501002",
            "source_system": "API",
            "created_date": "2026-06-27",
        },
    ]


def _write_customer_csv(file_path: Path, rows: list[dict[str, str]]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["customer_id", "email", "phone", "source_system", "created_date"]
    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
