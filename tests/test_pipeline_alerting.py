import json
import tempfile
import unittest
from pathlib import Path

from scripts.pipeline_alerting import collect_alert_events, load_alert_config


class TestPipelineAlerting(unittest.TestCase):
    def _alert_config(self):
        return {
            "alerting_enabled": True,
            "pipeline_name": "unit_test_pipeline",
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
                "max_pipeline_duration_seconds": 60,
                "max_step_duration_seconds": 30,
                "max_quarantine_rows": 0,
            },
            "input_paths": {},
            "output_paths": {},
        }

    def test_load_alert_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "alerts.json"
            config_path.write_text(
                json.dumps(self._alert_config(), indent=4),
                encoding="utf-8",
            )

            config = load_alert_config(str(config_path))

            self.assertEqual(config["pipeline_name"], "unit_test_pipeline")
            self.assertTrue(config["alerting_enabled"])

    def test_no_alerts_for_successful_run_within_sla(self):
        job_rows = [
            {
                "job_run_id": "job-1",
                "status": "SUCCESS",
                "start_time": "2026-06-27T10:00:00",
                "end_time": "2026-06-27T10:00:30",
            }
        ]
        step_rows = [
            {
                "job_run_id": "job-1",
                "step_name": "bronze_ingestion",
                "status": "SUCCESS",
                "critical": "True",
                "start_time": "2026-06-27T10:00:00",
                "end_time": "2026-06-27T10:00:10",
            }
        ]

        alerts = collect_alert_events(
            alert_config=self._alert_config(),
            job_rows=job_rows,
            step_rows=step_rows,
            observability_summary={
                "schema_validation_status": "PASSED",
                "dq_status": "SUCCESS",
                "quarantine_rows": 0,
            },
        )

        self.assertEqual(alerts, [])

    def test_pipeline_failure_generates_critical_alert(self):
        job_rows = [
            {
                "job_run_id": "job-1",
                "status": "FAILED",
                "start_time": "2026-06-27T10:00:00",
                "end_time": "2026-06-27T10:00:30",
            }
        ]
        step_rows = []

        alerts = collect_alert_events(
            alert_config=self._alert_config(),
            job_rows=job_rows,
            step_rows=step_rows,
            observability_summary={},
        )

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["alert_type"], "PIPELINE_FAILURE")
        self.assertEqual(alerts[0]["severity"], "CRITICAL")

    def test_step_failure_generates_step_alert(self):
        job_rows = [
            {
                "job_run_id": "job-1",
                "status": "SUCCESS_WITH_WARNINGS",
                "start_time": "2026-06-27T10:00:00",
                "end_time": "2026-06-27T10:00:30",
            }
        ]
        step_rows = [
            {
                "job_run_id": "job-1",
                "step_name": "optional_observability",
                "status": "FAILED",
                "critical": "False",
                "start_time": "2026-06-27T10:00:00",
                "end_time": "2026-06-27T10:00:10",
            }
        ]

        alerts = collect_alert_events(
            alert_config=self._alert_config(),
            job_rows=job_rows,
            step_rows=step_rows,
            observability_summary={},
        )

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["alert_type"], "OPTIONAL_STEP_FAILURE")
        self.assertEqual(alerts[0]["severity"], "WARNING")

    def test_sla_breach_generates_warning_alerts(self):
        job_rows = [
            {
                "job_run_id": "job-1",
                "status": "SUCCESS",
                "start_time": "2026-06-27T10:00:00",
                "end_time": "2026-06-27T10:03:00",
            }
        ]
        step_rows = [
            {
                "job_run_id": "job-1",
                "step_name": "silver_dq_validation",
                "status": "SUCCESS",
                "critical": "True",
                "start_time": "2026-06-27T10:00:00",
                "end_time": "2026-06-27T10:01:00",
            }
        ]

        alerts = collect_alert_events(
            alert_config=self._alert_config(),
            job_rows=job_rows,
            step_rows=step_rows,
            observability_summary={},
        )

        alert_types = {alert["alert_type"] for alert in alerts}

        self.assertIn("PIPELINE_SLA_BREACH", alert_types)
        self.assertIn("STEP_SLA_BREACH", alert_types)

    def test_observability_failure_generates_alerts(self):
        job_rows = [
            {
                "job_run_id": "job-1",
                "status": "SUCCESS",
                "start_time": "2026-06-27T10:00:00",
                "end_time": "2026-06-27T10:00:30",
            }
        ]
        step_rows = []

        alerts = collect_alert_events(
            alert_config=self._alert_config(),
            job_rows=job_rows,
            step_rows=step_rows,
            observability_summary={
                "schema_validation_status": "FAILED",
                "dq_status": "FAILED",
                "quarantine_rows": 5,
            },
        )

        alert_types = {alert["alert_type"] for alert in alerts}

        self.assertIn("SCHEMA_FAILURE", alert_types)
        self.assertIn("DQ_FAILURE", alert_types)
        self.assertIn("QUARANTINE_THRESHOLD_BREACH", alert_types)


if __name__ == "__main__":
    unittest.main()
