from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_partition_strategy import (
    load_partition_strategy,
    validate_partition_strategy,
    validate_table_strategy,
)


class TestV28PartitionStrategy(unittest.TestCase):
    def test_current_partition_strategy_is_valid(self):
        self.assertEqual(validate_partition_strategy(), [])

    def test_current_strategy_contains_required_tables(self):
        strategy = load_partition_strategy()
        datasets = {table["dataset"] for table in strategy["tables"]}

        self.assertIn("bronze_customers", datasets)
        self.assertIn("silver_customers", datasets)
        self.assertIn("customer_history", datasets)
        self.assertIn("gold_customer_canonical", datasets)
        self.assertIn("pipeline_observability_metrics", datasets)

    def test_invalid_file_size_is_rejected(self):
        table = {
            "dataset": "bronze_customers",
            "layer": "bronze",
            "expected_volume": "medium",
            "partition_columns": ["ingestion_date"],
            "clustering_columns": ["customer_id"],
            "target_file_size_mb": 16,
            "retention_days": 30,
            "maintenance_actions": ["collect-row-counts"],
        }

        issues = validate_table_strategy(table)

        self.assertTrue(any("target_file_size_mb" in issue for issue in issues))

    def test_too_many_partition_columns_are_rejected(self):
        table = {
            "dataset": "silver_customers",
            "layer": "silver",
            "expected_volume": "medium",
            "partition_columns": ["run_date", "country", "source_system", "extra_col"],
            "clustering_columns": ["customer_id"],
            "target_file_size_mb": 128,
            "retention_days": 30,
            "maintenance_actions": ["collect-row-counts"],
        }

        issues = validate_table_strategy(table)

        self.assertTrue(any("partition_columns must not exceed" in issue for issue in issues))

    def test_customer_history_requires_effective_year_partition(self):
        table = {
            "dataset": "customer_history",
            "layer": "history",
            "expected_volume": "large",
            "partition_columns": ["run_date"],
            "clustering_columns": ["customer_id"],
            "target_file_size_mb": 256,
            "retention_days": 365,
            "maintenance_actions": ["collect-row-counts"],
        }

        issues = validate_table_strategy(table)

        self.assertTrue(any("effective_year" in issue for issue in issues))

    def test_missing_required_dataset_is_rejected(self):
        strategy = {
            "version": "v28.0.0",
            "strategy_name": "test_strategy",
            "tables": [
                {
                    "dataset": "bronze_customers",
                    "layer": "bronze",
                    "expected_volume": "medium",
                    "partition_columns": ["ingestion_date"],
                    "clustering_columns": ["customer_id"],
                    "target_file_size_mb": 128,
                    "retention_days": 30,
                    "maintenance_actions": ["collect-row-counts"],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "strategy.json"
            path.write_text(json.dumps(strategy), encoding="utf-8")
            issues = validate_partition_strategy(path)

        self.assertTrue(any("missing required dataset strategy" in issue for issue in issues))

    def test_duplicate_dataset_is_rejected(self):
        table = {
            "dataset": "bronze_customers",
            "layer": "bronze",
            "expected_volume": "medium",
            "partition_columns": ["ingestion_date"],
            "clustering_columns": ["customer_id"],
            "target_file_size_mb": 128,
            "retention_days": 30,
            "maintenance_actions": ["collect-row-counts"],
        }
        strategy = {
            "version": "v28.0.0",
            "strategy_name": "test_strategy",
            "tables": [table, table],
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "strategy.json"
            path.write_text(json.dumps(strategy), encoding="utf-8")
            issues = validate_partition_strategy(path)

        self.assertTrue(any("duplicate dataset" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
