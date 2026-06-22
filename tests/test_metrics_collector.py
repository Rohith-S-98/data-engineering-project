"""
Unit tests for V13.0.0 Data Observability + Pipeline Metrics Mart.
"""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.metrics_collector import (
    MetricsCollector,
    calculate_scd2_metrics_from_rows,
    read_json_safely,
    read_latest_csv_record,
    read_latest_jsonl_record,
)


class TestMetricsCollector(unittest.TestCase):
    """
    Tests for V13 observability metrics helper functions.
    """

    def test_missing_json_file_returns_empty_dict(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_file = Path(temp_dir) / "missing.json"

            result = read_json_safely(missing_file)

            self.assertEqual(result, {})

    def test_missing_csv_file_returns_empty_dict(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_file = Path(temp_dir) / "missing.csv"

            result = read_latest_csv_record(missing_file)

            self.assertEqual(result, {})

    def test_missing_jsonl_file_returns_empty_dict(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_file = Path(temp_dir) / "missing.jsonl"

            result = read_latest_jsonl_record(missing_file)

            self.assertEqual(result, {})

    def test_latest_csv_record_is_returned(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = Path(temp_dir) / "pipeline_runs.csv"

            with audit_file.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "run_id",
                        "pipeline_name",
                        "environment",
                        "start_time",
                        "end_time",
                        "status",
                        "error_message",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "run_id": "run_001",
                        "pipeline_name": "customer_pipeline",
                        "environment": "local",
                        "start_time": "2026-06-22T10:00:00",
                        "end_time": "2026-06-22T10:01:00",
                        "status": "FAILED",
                        "error_message": "sample failure",
                    }
                )
                writer.writerow(
                    {
                        "run_id": "run_002",
                        "pipeline_name": "customer_pipeline",
                        "environment": "local",
                        "start_time": "2026-06-22T10:05:00",
                        "end_time": "2026-06-22T10:06:00",
                        "status": "SUCCESS",
                        "error_message": "",
                    }
                )

            result = read_latest_csv_record(audit_file)

            self.assertEqual(result["run_id"], "run_002")
            self.assertEqual(result["status"], "SUCCESS")

    def test_latest_valid_jsonl_record_is_returned(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            jsonl_file = Path(temp_dir) / "schema_validation_audit.jsonl"

            records = [
                {"status": "FAILED", "schema_name": "bronze_customers"},
                {"status": "PASSED", "schema_name": "silver_customers"},
            ]

            with jsonl_file.open("w", encoding="utf-8") as file:
                for record in records:
                    file.write(json.dumps(record) + "\n")

            result = read_latest_jsonl_record(jsonl_file)

            self.assertEqual(result["status"], "PASSED")
            self.assertEqual(result["schema_name"], "silver_customers")

    def test_scd2_metrics_calculation_from_rows(self) -> None:
        rows = [
            {
                "customer_id": "CUST001",
                "first_name": "Rahul",
                "is_current": False,
                "effective_start_date": "2026-06-01",
                "effective_end_date": "2026-06-18",
            },
            {
                "customer_id": "CUST001",
                "first_name": "Rahul Updated",
                "is_current": True,
                "effective_start_date": "2026-06-18",
                "effective_end_date": None,
            },
            {
                "customer_id": "CUST002",
                "first_name": "Priya",
                "is_current": True,
                "effective_start_date": "2026-06-01",
                "effective_end_date": None,
            },
        ]

        result = calculate_scd2_metrics_from_rows(rows)

        self.assertEqual(result["total_history_rows"], 3)
        self.assertEqual(result["current_rows"], 2)
        self.assertEqual(result["expired_rows"], 1)
        self.assertEqual(result["changed_customer_count"], 1)

    def test_pipeline_audit_missing_file_returns_missing_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "environment": "local",
                "dataset_name": "customers",
                "audit_log_file": str(Path(temp_dir) / "missing_pipeline_runs.csv"),
            }

            collector = MetricsCollector(
                spark=None,
                config=config,
            )

            result = collector.collect_latest_pipeline_audit_metrics()

            self.assertEqual(result["latest_pipeline_status"], "MISSING")
            self.assertIsNone(result["latest_run_id"])

    def test_schema_validation_missing_file_returns_missing_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "environment": "local",
                "dataset_name": "customers",
                "schema_validation_audit_file": str(
                    Path(temp_dir) / "missing_schema_validation_audit.jsonl"
                ),
            }

            collector = MetricsCollector(
                spark=None,
                config=config,
            )

            result = collector.collect_schema_validation_metrics()

            self.assertEqual(result["status"], "MISSING")
            self.assertEqual(result["total_issues"], 0)

    def test_metrics_summary_contains_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "environment": "local",
                "dataset_name": "customers",
                "storage_format": "delta",
                "bronze_output_path": str(Path(temp_dir) / "bronze"),
                "silver_output_path": str(Path(temp_dir) / "silver"),
                "quarantine_output_path": str(Path(temp_dir) / "quarantine"),
                "gold_output_path": str(Path(temp_dir) / "gold"),
                "customer_history_output_path": str(Path(temp_dir) / "history"),
                "dq_report_file": str(Path(temp_dir) / "dq_report.json"),
                "audit_log_file": str(Path(temp_dir) / "pipeline_runs.csv"),
                "schema_validation_audit_file": str(
                    Path(temp_dir) / "schema_validation_audit.jsonl"
                ),
                "watermark_store_file": str(Path(temp_dir) / "watermark_store.json"),
                "pending_watermark_file": str(
                    Path(temp_dir) / "pending_watermark_updates.json"
                ),
                "watermark_column": "created_date",
                "scd2_business_keys": ["customer_id"],
            }

            collector = MetricsCollector(
                spark=None,
                config=config,
            )

            metrics = collector.collect_all_metrics()

            self.assertIn("pipeline_health", metrics)
            self.assertIn("row_counts", metrics)
            self.assertIn("pipeline_audit", metrics)
            self.assertIn("data_quality", metrics)
            self.assertIn("schema_validation", metrics)
            self.assertIn("watermark", metrics)
            self.assertIn("scd2", metrics)

            self.assertEqual(metrics["pipeline_health"]["latest_pipeline_status"], "MISSING")
            self.assertEqual(metrics["pipeline_health"]["schema_validation_status"], "MISSING")
            self.assertEqual(metrics["pipeline_health"]["dq_status"], "MISSING")

            self.assertEqual(metrics["row_counts"]["bronze_rows"], 0)
            self.assertEqual(metrics["row_counts"]["silver_rows"], 0)
            self.assertEqual(metrics["row_counts"]["quarantine_rows"], 0)
            self.assertEqual(metrics["row_counts"]["gold_rows"], 0)
            self.assertEqual(metrics["row_counts"]["customer_history_rows"], 0)


if __name__ == "__main__":
    unittest.main()