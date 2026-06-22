import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.pipeline_orchestrator import run_pipeline_orchestrator


def runtime_success():
    return "SUCCESS"


def runtime_failure():
    return "FAILED"


class TestV15OrchestratorRuntime(unittest.TestCase):
    def _pipeline_config(self):
        return {
            "environment": "test",
            "dataset_name": "customers",
            "watermark_store_file": "data/audit/watermark_store.json",
            "pending_watermark_file": "data/audit/pending_watermark_updates.json",
        }

    def _write_job_config(self, temp_dir, steps):
        job_config_path = Path(temp_dir) / "job.json"
        job_run_log_file = Path(temp_dir) / "job_runs.csv"
        step_run_log_file = Path(temp_dir) / "step_runs.csv"

        job_config = {
            "job_name": "v15_runtime_test_job",
            "environment": "test",
            "job_run_log_file": str(job_run_log_file),
            "step_run_log_file": str(step_run_log_file),
            "runtime_parameters": {
                "run_mode": "manual",
                "dry_run": False,
                "triggered_by": "unit_test",
            },
            "steps": steps,
        }

        job_config_path.write_text(json.dumps(job_config), encoding="utf-8")
        return job_config_path, job_run_log_file, step_run_log_file

    def test_dry_run_does_not_execute_failure_function(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            job_config_path, job_run_log_file, step_run_log_file = self._write_job_config(
                temp_dir=temp_dir,
                steps=[
                    {
                        "step_id": 1,
                        "step_name": "dry_run_failure_step",
                        "module": __name__,
                        "function": "runtime_failure",
                        "enabled": True,
                        "critical": True,
                        "depends_on": [],
                        "expected_success_statuses": ["SUCCESS"],
                    }
                ],
            )

            with patch(
                "scripts.pipeline_orchestrator.load_pipeline_config",
                return_value=self._pipeline_config(),
            ), patch(
                "scripts.pipeline_orchestrator.save_runtime_parameters_snapshot",
                return_value=str(Path(temp_dir) / "runtime.json"),
            ):
                status = run_pipeline_orchestrator(
                    job_config_path=str(job_config_path),
                    raise_on_failure=False,
                    runtime_parameters={"dry_run": True, "run_date": "2026-06-23"},
                )

            self.assertEqual(status, "SUCCESS")

            with open(step_run_log_file, mode="r", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(rows[0]["status"], "DRY_RUN")
            self.assertEqual(rows[0]["result_status"], "DRY_RUN")

    def test_step_dependency_success_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            job_config_path, job_run_log_file, step_run_log_file = self._write_job_config(
                temp_dir=temp_dir,
                steps=[
                    {
                        "step_id": 1,
                        "step_name": "first_step",
                        "module": __name__,
                        "function": "runtime_success",
                        "enabled": True,
                        "critical": True,
                        "depends_on": [],
                        "expected_success_statuses": ["SUCCESS"],
                    },
                    {
                        "step_id": 2,
                        "step_name": "second_step",
                        "module": __name__,
                        "function": "runtime_success",
                        "enabled": True,
                        "critical": True,
                        "depends_on": ["first_step"],
                        "expected_success_statuses": ["SUCCESS"],
                    },
                ],
            )

            with patch(
                "scripts.pipeline_orchestrator.load_pipeline_config",
                return_value=self._pipeline_config(),
            ), patch(
                "scripts.pipeline_orchestrator.save_runtime_parameters_snapshot",
                return_value=str(Path(temp_dir) / "runtime.json"),
            ):
                status = run_pipeline_orchestrator(
                    job_config_path=str(job_config_path),
                    raise_on_failure=False,
                    runtime_parameters={"run_mode": "manual"},
                )

            self.assertEqual(status, "SUCCESS")

            with open(job_run_log_file, mode="r", encoding="utf-8") as file:
                job_rows = list(csv.DictReader(file))

            self.assertEqual(job_rows[0]["successful_steps"], "2")

    def test_unmet_critical_dependency_fails_job(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            job_config_path, job_run_log_file, step_run_log_file = self._write_job_config(
                temp_dir=temp_dir,
                steps=[
                    {
                        "step_id": 1,
                        "step_name": "dependent_step",
                        "module": __name__,
                        "function": "runtime_success",
                        "enabled": True,
                        "critical": True,
                        "depends_on": ["missing_step"],
                        "expected_success_statuses": ["SUCCESS"],
                    }
                ],
            )

            with patch(
                "scripts.pipeline_orchestrator.load_pipeline_config",
                return_value=self._pipeline_config(),
            ), patch(
                "scripts.pipeline_orchestrator.save_runtime_parameters_snapshot",
                return_value=str(Path(temp_dir) / "runtime.json"),
            ):
                status = run_pipeline_orchestrator(
                    job_config_path=str(job_config_path),
                    raise_on_failure=False,
                    runtime_parameters={"run_mode": "manual"},
                )

            self.assertEqual(status, "FAILED")

            with open(step_run_log_file, mode="r", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(rows[0]["status"], "SKIPPED")
            self.assertEqual(rows[0]["result_status"], "DEPENDENCY_NOT_MET")


if __name__ == "__main__":
    unittest.main()
