import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.pipeline_orchestrator import (
    load_job_config,
    run_pipeline_orchestrator,
)


def dummy_success():
    return "SUCCESS"


def dummy_none_success():
    return None


def dummy_failed_status():
    return "FAILED"


def dummy_raise_error():
    raise RuntimeError("dummy optional failure")


class TestPipelineOrchestrator(unittest.TestCase):
    def _write_job_config(
        self,
        temp_dir,
        steps,
        continue_on_optional_step_failure=True,
    ):
        job_config_path = Path(temp_dir) / "job.json"
        job_run_log_file = Path(temp_dir) / "job_runs.csv"
        step_run_log_file = Path(temp_dir) / "step_runs.csv"

        job_config = {
            "job_name": "unit_test_orchestration_job",
            "environment": "test",
            "job_run_log_file": str(job_run_log_file),
            "step_run_log_file": str(step_run_log_file),
            "continue_on_optional_step_failure": continue_on_optional_step_failure,
            "steps": steps,
        }

        job_config_path.write_text(
            json.dumps(job_config, indent=4),
            encoding="utf-8",
        )

        return job_config_path, job_run_log_file, step_run_log_file

    def _pipeline_config(self):
        return {
            "environment": "test",
            "dataset_name": "customers",
            "watermark_store_file": "data/audit/watermark_store.json",
            "pending_watermark_file": "data/audit/pending_watermark_updates.json",
        }

    def test_load_job_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            job_config_path, _, _ = self._write_job_config(
                temp_dir=temp_dir,
                steps=[
                    {
                        "step_id": 1,
                        "step_name": "success_step",
                        "module": __name__,
                        "function": "dummy_success",
                    }
                ],
            )

            job_config = load_job_config(str(job_config_path))

            self.assertEqual(
                job_config["job_name"],
                "unit_test_orchestration_job",
            )
            self.assertEqual(len(job_config["steps"]), 1)

    def test_orchestrator_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            job_config_path, job_run_log_file, step_run_log_file = self._write_job_config(
                temp_dir=temp_dir,
                steps=[
                    {
                        "step_id": 1,
                        "step_name": "success_step",
                        "module": __name__,
                        "function": "dummy_success",
                        "enabled": True,
                        "critical": True,
                        "expected_success_statuses": ["SUCCESS"],
                    },
                    {
                        "step_id": 2,
                        "step_name": "none_success_step",
                        "module": __name__,
                        "function": "dummy_none_success",
                        "enabled": True,
                        "critical": True,
                        "expected_success_statuses": ["SUCCESS", None],
                    },
                ],
            )

            with patch(
                "scripts.pipeline_orchestrator.load_pipeline_config",
                return_value=self._pipeline_config(),
            ):
                status = run_pipeline_orchestrator(
                    job_config_path=str(job_config_path),
                    raise_on_failure=False,
                )

            self.assertEqual(status, "SUCCESS")

            with open(job_run_log_file, mode="r", encoding="utf-8") as file:
                job_rows = list(csv.DictReader(file))

            with open(step_run_log_file, mode="r", encoding="utf-8") as file:
                step_rows = list(csv.DictReader(file))

            self.assertEqual(job_rows[0]["status"], "SUCCESS")
            self.assertEqual(job_rows[0]["successful_steps"], "2")
            self.assertEqual(len(step_rows), 2)
            self.assertEqual(step_rows[0]["status"], "SUCCESS")
            self.assertEqual(step_rows[1]["status"], "SUCCESS")

    def test_orchestrator_skips_disabled_step(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            job_config_path, job_run_log_file, step_run_log_file = self._write_job_config(
                temp_dir=temp_dir,
                steps=[
                    {
                        "step_id": 1,
                        "step_name": "disabled_step",
                        "module": __name__,
                        "function": "dummy_success",
                        "enabled": False,
                        "critical": False,
                        "expected_success_statuses": ["SUCCESS"],
                    }
                ],
            )

            with patch(
                "scripts.pipeline_orchestrator.load_pipeline_config",
                return_value=self._pipeline_config(),
            ):
                status = run_pipeline_orchestrator(
                    job_config_path=str(job_config_path),
                    raise_on_failure=False,
                )

            self.assertEqual(status, "SUCCESS")

            with open(job_run_log_file, mode="r", encoding="utf-8") as file:
                job_rows = list(csv.DictReader(file))

            with open(step_run_log_file, mode="r", encoding="utf-8") as file:
                step_rows = list(csv.DictReader(file))

            self.assertEqual(job_rows[0]["skipped_steps"], "1")
            self.assertEqual(step_rows[0]["status"], "SKIPPED")

    def test_critical_failure_returns_failed_without_raising_when_disabled(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            job_config_path, job_run_log_file, step_run_log_file = self._write_job_config(
                temp_dir=temp_dir,
                steps=[
                    {
                        "step_id": 1,
                        "step_name": "critical_failed_step",
                        "module": __name__,
                        "function": "dummy_failed_status",
                        "enabled": True,
                        "critical": True,
                        "expected_success_statuses": ["SUCCESS"],
                    }
                ],
            )

            with patch(
                "scripts.pipeline_orchestrator.load_pipeline_config",
                return_value=self._pipeline_config(),
            ):
                status = run_pipeline_orchestrator(
                    job_config_path=str(job_config_path),
                    raise_on_failure=False,
                )

            self.assertEqual(status, "FAILED")

            with open(job_run_log_file, mode="r", encoding="utf-8") as file:
                job_rows = list(csv.DictReader(file))

            with open(step_run_log_file, mode="r", encoding="utf-8") as file:
                step_rows = list(csv.DictReader(file))

            self.assertEqual(job_rows[0]["status"], "FAILED")
            self.assertEqual(job_rows[0]["failed_steps"], "1")
            self.assertEqual(step_rows[0]["status"], "FAILED")

    def test_optional_failure_continues(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            job_config_path, job_run_log_file, step_run_log_file = self._write_job_config(
                temp_dir=temp_dir,
                steps=[
                    {
                        "step_id": 1,
                        "step_name": "optional_failed_step",
                        "module": __name__,
                        "function": "dummy_raise_error",
                        "enabled": True,
                        "critical": False,
                        "expected_success_statuses": ["SUCCESS"],
                    },
                    {
                        "step_id": 2,
                        "step_name": "success_step_after_optional_failure",
                        "module": __name__,
                        "function": "dummy_success",
                        "enabled": True,
                        "critical": True,
                        "expected_success_statuses": ["SUCCESS"],
                    },
                ],
                continue_on_optional_step_failure=True,
            )

            with patch(
                "scripts.pipeline_orchestrator.load_pipeline_config",
                return_value=self._pipeline_config(),
            ):
                status = run_pipeline_orchestrator(
                    job_config_path=str(job_config_path),
                    raise_on_failure=False,
                )

            self.assertEqual(status, "SUCCESS_WITH_WARNINGS")

            with open(job_run_log_file, mode="r", encoding="utf-8") as file:
                job_rows = list(csv.DictReader(file))

            with open(step_run_log_file, mode="r", encoding="utf-8") as file:
                step_rows = list(csv.DictReader(file))

            self.assertEqual(job_rows[0]["status"], "SUCCESS_WITH_WARNINGS")
            self.assertEqual(job_rows[0]["failed_steps"], "1")
            self.assertEqual(job_rows[0]["successful_steps"], "1")
            self.assertEqual(step_rows[0]["status"], "FAILED")
            self.assertEqual(step_rows[1]["status"], "SUCCESS")


if __name__ == "__main__":
    unittest.main()
