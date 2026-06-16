import csv
import tempfile
import unittest
from pathlib import Path

from scripts.run_metadata import create_pipeline_run, update_pipeline_run


class TestRunMetadata(unittest.TestCase):

    def test_create_pipeline_run_writes_started_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = Path(temp_dir) / "pipeline_runs.csv"

            run_id = create_pipeline_run(
                pipeline_name="test_pipeline",
                environment="local",
                audit_log_file=str(audit_file),
            )

            self.assertTrue(audit_file.exists())
            self.assertTrue(run_id)

            with open(audit_file, mode="r", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["pipeline_name"], "test_pipeline")
            self.assertEqual(rows[0]["environment"], "local")
            self.assertEqual(rows[0]["status"], "STARTED")

    def test_update_pipeline_run_marks_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = Path(temp_dir) / "pipeline_runs.csv"

            run_id = create_pipeline_run(
                pipeline_name="test_pipeline",
                environment="local",
                audit_log_file=str(audit_file),
            )

            update_pipeline_run(
                run_id=run_id,
                audit_log_file=str(audit_file),
                status="SUCCESS",
            )

            with open(audit_file, mode="r", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(rows[0]["status"], "SUCCESS")
            self.assertNotEqual(rows[0]["end_time"], "")


if __name__ == "__main__":
    unittest.main()