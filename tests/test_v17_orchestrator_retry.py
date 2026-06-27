import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.pipeline_orchestrator import run_pipeline_orchestrator


class V17FlakyStep:
    call_count = 0

    @classmethod
    def reset(cls):
        cls.call_count = 0

    @classmethod
    def run(cls):
        cls.call_count += 1

        if cls.call_count == 1:
            raise RuntimeError("temporary orchestrator failure")

        return "SUCCESS"


class TestV17OrchestratorRetry(unittest.TestCase):
    def _pipeline_config(self):
        return {
            "environment": "test",
            "dataset_name": "customers",
            "watermark_store_file": "data/audit/watermark_store.json",
            "pending_watermark_file": "data/audit/pending_watermark_updates.json",
        }

    def test_orchestrator_recovers_after_retry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            V17FlakyStep.reset()

            retry_event_csv = Path(temp_dir) / "retry_events.csv"
            retry_policy_path = Path(temp_dir) / "retry_policy.json"
            job_config_path = Path(temp_dir) / "job.json"
            job_run_log_file = Path(temp_dir) / "job_runs.csv"
            step_run_log_file = Path(temp_dir) / "step_runs.csv"

            retry_policy = {
                "enabled": True,
                "default_max_retry_attempts": 2,
                "default_retry_delay_seconds": 0,
                "retry_event_csv_file": str(retry_event_csv),
                "retry_event_jsonl_file": str(Path(temp_dir) / "retry_events.jsonl"),
                "retryable_exceptions": ["RuntimeError", "Exception"],
                "non_retryable_exceptions": ["KeyboardInterrupt", "SystemExit"],
                "steps": {
                    "flaky_step": {
                        "retry_enabled": True,
                        "max_retry_attempts": 2,
                        "retry_delay_seconds": 0,
                    }
                },
            }

            retry_policy_path.write_text(
                json.dumps(retry_policy, indent=2),
                encoding="utf-8",
            )

            job_config = {
                "job_name": "v17_retry_test_job",
                "environment": "test",
                "job_run_log_file": str(job_run_log_file),
                "step_run_log_file": str(step_run_log_file),
                "retry_policy_path": str(retry_policy_path),
                "steps": [
                    {
                        "step_id": 1,
                        "step_name": "flaky_step",
                        "module": __name__,
                        "function": "V17FlakyStep.run",
                        "enabled": True,
                        "critical": True,
                        "expected_success_statuses": ["SUCCESS"],
                    }
                ],
            }

            job_config_path.write_text(
                json.dumps(job_config, indent=2),
                encoding="utf-8",
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
            self.assertEqual(V17FlakyStep.call_count, 2)

            with open(retry_event_csv, encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            event_types = [row["event_type"] for row in rows]
            self.assertIn("RETRY_ATTEMPT", event_types)
            self.assertIn("RECOVERY_SUCCESS", event_types)


if __name__ == "__main__":
    unittest.main()
