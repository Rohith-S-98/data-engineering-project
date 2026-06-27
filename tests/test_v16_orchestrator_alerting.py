import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.pipeline_orchestrator import run_pipeline_orchestrator


def dummy_success():
    return "SUCCESS"


class TestV16OrchestratorAlerting(unittest.TestCase):
    def _pipeline_config(self):
        return {
            "environment": "test",
            "dataset_name": "customers",
            "watermark_store_file": "data/audit/watermark_store.json",
            "pending_watermark_file": "data/audit/pending_watermark_updates.json",
        }

    def test_orchestrator_runs_alerting_after_job_completion(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            alert_config_path = temp_path / "alerts.json"
            job_config_path = temp_path / "job.json"
            job_run_log_file = temp_path / "job_runs.csv"
            step_run_log_file = temp_path / "step_runs.csv"
            observability_summary_file = temp_path / "summary.json"
            notification_summary_file = temp_path / "notification_summary.txt"

            observability_summary_file.write_text(
                json.dumps(
                    {
                        "schema_validation_status": "PASSED",
                        "dq_status": "SUCCESS",
                        "quarantine_rows": 0,
                    }
                ),
                encoding="utf-8",
            )

            alert_config_path.write_text(
                json.dumps(
                    {
                        "alerting_enabled": True,
                        "pipeline_name": "v16_alerting_test_job",
                        "environment": "test",
                        "severity_mapping": {
                            "pipeline_failure": "CRITICAL",
                            "critical_step_failure": "CRITICAL",
                            "optional_step_failure": "WARNING",
                            "pipeline_sla_breach": "WARNING",
                            "step_sla_breach": "WARNING",
                            "dq_failure": "CRITICAL",
                            "schema_failure": "CRITICAL",
                            "quarantine_threshold_breach": "WARNING",
                        },
                        "sla_thresholds": {
                            "max_pipeline_duration_seconds": 999,
                            "max_step_duration_seconds": 999,
                            "max_quarantine_rows": 0,
                        },
                        "input_paths": {
                            "job_run_log_file": str(job_run_log_file),
                            "step_run_log_file": str(step_run_log_file),
                            "observability_summary_file": str(
                                observability_summary_file
                            ),
                        },
                        "output_paths": {
                            "alert_events_jsonl": str(
                                temp_path / "alert_events.jsonl"
                            ),
                            "alert_events_csv": str(temp_path / "alert_events.csv"),
                            "notification_summary_file": str(
                                notification_summary_file
                            ),
                        },
                        "notification_channels": [
                            {
                                "channel_name": "file_summary",
                                "channel_type": "file",
                                "enabled": True,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            job_config_path.write_text(
                json.dumps(
                    {
                        "job_name": "v16_alerting_test_job",
                        "environment": "test",
                        "job_run_log_file": str(job_run_log_file),
                        "step_run_log_file": str(step_run_log_file),
                        "continue_on_optional_step_failure": True,
                        "alerting": {
                            "enabled": True,
                            "alert_config_path": str(alert_config_path),
                        },
                        "steps": [
                            {
                                "step_id": 1,
                                "step_name": "success_step",
                                "module": __name__,
                                "function": "dummy_success",
                                "enabled": True,
                                "critical": True,
                                "depends_on": [],
                                "expected_success_statuses": ["SUCCESS"],
                            }
                        ],
                    },
                    indent=4,
                ),
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
            self.assertTrue(notification_summary_file.exists())

            summary_text = notification_summary_file.read_text(encoding="utf-8")
            self.assertIn("No alerts generated", summary_text)

            with job_run_log_file.open(mode="r", encoding="utf-8") as file:
                job_rows = list(csv.DictReader(file))

            self.assertEqual(job_rows[0]["status"], "SUCCESS")


if __name__ == "__main__":
    unittest.main()
