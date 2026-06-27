from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.powerbi_observability_exporter import (
    build_dq_snapshot,
    build_kpi_snapshot,
    build_layer_row_count_records,
    export_powerbi_observability,
    pct,
    safe_int,
)
from scripts.validate_powerbi_dashboard_artifacts import (
    PowerBiDashboardValidationError,
    assert_valid_powerbi_dashboard_artifacts,
    validate_powerbi_dashboard_artifacts,
    validate_schema,
)


SAMPLE_METRICS = {
    "metrics_generated_at": "2026-06-23T00:00:00+00:00",
    "environment": "dev",
    "dataset_name": "customers",
    "pipeline_health": {
        "latest_pipeline_status": "SUCCESS",
        "schema_validation_status": "SUCCESS",
        "dq_status": "SUCCESS",
    },
    "row_counts": {
        "bronze_rows": 100,
        "silver_rows": 95,
        "quarantine_rows": 5,
        "gold_rows": 95,
        "customer_history_rows": 120,
    },
    "data_quality": {
        "dq_status": "SUCCESS",
        "total_input_rows": 100,
        "valid_rows": 95,
        "quarantined_rows": 5,
        "total_rules": 10,
        "failed_rule_count": 1,
    },
    "watermark": {"current_watermark": "2026-06-23", "pending_watermark": None},
    "scd2": {"total_history_rows": 120, "current_rows": 95, "expired_rows": 25, "changed_customer_count": 20},
}


class TestV25PowerBiObservabilityDashboard(unittest.TestCase):
    def test_current_powerbi_dashboard_artifacts_are_valid(self):
        self.assertEqual(validate_powerbi_dashboard_artifacts(), [])

    def test_safe_calculations(self):
        self.assertEqual(safe_int("10"), 10)
        self.assertEqual(safe_int(None), 0)
        self.assertEqual(pct(5, 0), 0.0)
        self.assertEqual(pct(5, 100), 5.0)

    def test_kpi_and_dq_snapshots_calculate_rates(self):
        kpi = build_kpi_snapshot(SAMPLE_METRICS)
        dq = build_dq_snapshot(SAMPLE_METRICS)

        self.assertEqual(kpi["dataset_name"], "customers")
        self.assertEqual(kpi["quarantine_rate_pct"], 5.0)
        self.assertEqual(kpi["dq_failure_rate_pct"], 10.0)
        self.assertEqual(dq["dq_pass_rate_pct"], 95.0)

    def test_layer_row_count_records_returns_expected_layers(self):
        rows = build_layer_row_count_records(SAMPLE_METRICS)
        self.assertEqual(len(rows), 5)
        self.assertIn("bronze", {row["layer_name"] for row in rows})
        self.assertIn("customer_history", {row["layer_name"] for row in rows})

    def test_export_powerbi_observability_writes_csv_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            summary_file = Path(tmp_dir) / "summary.json"
            output_dir = Path(tmp_dir) / "powerbi"
            summary_file.write_text(json.dumps(SAMPLE_METRICS), encoding="utf-8")

            outputs = export_powerbi_observability(summary_file, output_dir)

            for file_path in outputs.values():
                self.assertTrue(Path(file_path).exists())

            with Path(outputs["dashboard_kpi_snapshot"]).open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(rows[0]["dataset_name"], "customers")

    def test_schema_validator_reports_missing_fact_tables(self):
        issues = validate_schema({"version": "v25.0.0", "fact_tables": [], "recommended_visuals": []})
        self.assertTrue(any("fact_tables" in issue for issue in issues))

    def test_assert_valid_raises_when_validation_fails(self):
        with patch("scripts.validate_powerbi_dashboard_artifacts.validate_powerbi_dashboard_artifacts", return_value=["broken"]):
            with self.assertRaises(PowerBiDashboardValidationError):
                assert_valid_powerbi_dashboard_artifacts()


if __name__ == "__main__":
    unittest.main()
