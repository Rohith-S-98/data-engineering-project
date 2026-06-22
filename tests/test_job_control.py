import csv
import tempfile
import unittest
from pathlib import Path

from scripts.job_control import (
    create_job_run,
    create_step_run,
    update_job_run,
    update_step_run,
)


class TestJobControl(unittest.TestCase):
    def test_create_and_update_job_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            job_run_log_file = str(Path(temp_dir) / "job_runs.csv")

            job_run_id = create_job_run(
                job_name="unit_test_job",
                environment="test",
                job_run_log_file=job_run_log_file,
            )

            update_job_run(
                job_run_id=job_run_id,
                status="SUCCESS",
                total_steps=2,
                successful_steps=2,
                failed_steps=0,
                skipped_steps=0,
                job_run_log_file=job_run_log_file,
            )

            with open(job_run_log_file, mode="r", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["job_run_id"], job_run_id)
            self.assertEqual(rows[0]["status"], "SUCCESS")
            self.assertEqual(rows[0]["total_steps"], "2")
            self.assertEqual(rows[0]["successful_steps"], "2")
            self.assertEqual(rows[0]["failed_steps"], "0")
            self.assertEqual(rows[0]["skipped_steps"], "0")
            self.assertNotEqual(rows[0]["end_time"], "")

    def test_create_and_update_step_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            step_run_log_file = str(Path(temp_dir) / "step_runs.csv")
            job_run_id = "job-123"

            step_config = {
                "step_id": 1,
                "step_name": "unit_test_step",
                "module": "tests.fake_module",
                "function": "fake_function",
                "critical": True,
                "enabled": True,
            }

            create_step_run(
                job_run_id=job_run_id,
                step_config=step_config,
                step_run_log_file=step_run_log_file,
            )

            update_step_run(
                job_run_id=job_run_id,
                step_id=1,
                status="SUCCESS",
                result_status="SUCCESS",
                step_run_log_file=step_run_log_file,
            )

            with open(step_run_log_file, mode="r", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["job_run_id"], job_run_id)
            self.assertEqual(rows[0]["step_id"], "1")
            self.assertEqual(rows[0]["step_name"], "unit_test_step")
            self.assertEqual(rows[0]["status"], "SUCCESS")
            self.assertEqual(rows[0]["result_status"], "SUCCESS")
            self.assertNotEqual(rows[0]["end_time"], "")


if __name__ == "__main__":
    unittest.main()
