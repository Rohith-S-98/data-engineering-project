import json
import tempfile
import unittest
from pathlib import Path

from scripts.runtime_parameters import (
    load_default_runtime_parameters,
    merge_runtime_parameters,
    save_runtime_parameters_snapshot,
    validate_runtime_parameters,
)


class TestRuntimeParameters(unittest.TestCase):
    def test_validate_manual_runtime_parameters(self):
        parameters = validate_runtime_parameters(
            {
                "run_mode": "manual",
                "run_date": "2026-06-23",
                "dry_run": False,
                "triggered_by": "unit_test",
            }
        )

        self.assertEqual(parameters["run_mode"], "manual")
        self.assertEqual(parameters["run_date"], "2026-06-23")
        self.assertFalse(parameters["dry_run"])

    def test_backfill_requires_date_range(self):
        with self.assertRaises(ValueError):
            validate_runtime_parameters({"run_mode": "backfill"})

    def test_backfill_date_range_is_validated(self):
        with self.assertRaises(ValueError):
            validate_runtime_parameters(
                {
                    "run_mode": "backfill",
                    "backfill_start_date": "2026-06-24",
                    "backfill_end_date": "2026-06-23",
                }
            )

    def test_merge_runtime_parameters(self):
        merged = merge_runtime_parameters(
            {"run_mode": "manual", "dry_run": False},
            {"dry_run": True, "triggered_by": "unit_test"},
        )

        self.assertEqual(merged["run_mode"], "manual")
        self.assertTrue(merged["dry_run"])
        self.assertEqual(merged["triggered_by"], "unit_test")

    def test_save_runtime_parameters_snapshot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = save_runtime_parameters_snapshot(
                job_run_id="job-123",
                parameters={"run_mode": "manual", "dry_run": True},
                output_dir=temp_dir,
            )

            path = Path(output_file)
            self.assertTrue(path.exists())

            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved["run_mode"], "manual")
            self.assertTrue(saved["dry_run"])

    def test_load_default_runtime_parameters_from_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "runtime.json"
            config_path.write_text(
                json.dumps({"run_mode": "scheduled", "dry_run": False}),
                encoding="utf-8",
            )

            parameters = load_default_runtime_parameters(str(config_path))
            self.assertEqual(parameters["run_mode"], "scheduled")


if __name__ == "__main__":
    unittest.main()
