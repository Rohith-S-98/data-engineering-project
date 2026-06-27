import csv
import tempfile
import unittest
from pathlib import Path

from scripts.pipeline_retry import (
    create_replay_request,
    execute_step_with_retry,
    get_step_retry_config,
    load_retry_policy,
)


def success_step():
    return "SUCCESS"


def failed_status_step():
    return "FAILED"


class FlakyStep:
    def __init__(self):
        self.call_count = 0

    def __call__(self):
        self.call_count += 1

        if self.call_count == 1:
            raise RuntimeError("temporary failure")

        return "SUCCESS"


class TestPipelineRetry(unittest.TestCase):
    def _policy(self, temp_dir):
        return {
            "enabled": True,
            "default_max_retry_attempts": 2,
            "default_retry_delay_seconds": 0,
            "retry_event_jsonl_file": str(Path(temp_dir) / "retry_events.jsonl"),
            "retry_event_csv_file": str(Path(temp_dir) / "retry_events.csv"),
            "retryable_exceptions": ["RuntimeError", "Exception"],
            "non_retryable_exceptions": ["KeyboardInterrupt", "SystemExit"],
            "steps": {
                "unit_step": {
                    "retry_enabled": True,
                    "max_retry_attempts": 2,
                    "retry_delay_seconds": 0,
                }
            },
        }

    def _step_config(self):
        return {
            "step_id": 1,
            "step_name": "unit_step",
            "expected_success_statuses": ["SUCCESS"],
        }

    def test_get_step_retry_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config = get_step_retry_config(
                step_config=self._step_config(),
                retry_policy=self._policy(temp_dir),
            )

            self.assertTrue(config["retry_enabled"])
            self.assertEqual(config["max_retry_attempts"], 2)

    def test_success_step_does_not_create_retry_events(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            policy = self._policy(temp_dir)

            result = execute_step_with_retry(
                step_function=success_step,
                step_config=self._step_config(),
                step_kwargs={},
                job_run_id="job-1",
                retry_policy=policy,
            )

            self.assertEqual(result, "SUCCESS")
            self.assertFalse(Path(policy["retry_event_csv_file"]).exists())

    def test_transient_failure_recovers_after_retry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            policy = self._policy(temp_dir)
            flaky_step = FlakyStep()

            result = execute_step_with_retry(
                step_function=flaky_step,
                step_config=self._step_config(),
                step_kwargs={},
                job_run_id="job-1",
                retry_policy=policy,
            )

            self.assertEqual(result, "SUCCESS")
            self.assertEqual(flaky_step.call_count, 2)

            with open(policy["retry_event_csv_file"], encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            event_types = [row["event_type"] for row in rows]
            self.assertIn("RETRY_ATTEMPT", event_types)
            self.assertIn("RECOVERY_SUCCESS", event_types)

    def test_failed_status_exhausts_retries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            policy = self._policy(temp_dir)

            result = execute_step_with_retry(
                step_function=failed_status_step,
                step_config=self._step_config(),
                step_kwargs={},
                job_run_id="job-1",
                retry_policy=policy,
            )

            self.assertEqual(result, "FAILED")

            with open(policy["retry_event_csv_file"], encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            event_types = [row["event_type"] for row in rows]
            self.assertIn("RECOVERY_EXHAUSTED", event_types)

    def test_create_replay_request(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            replay_file = str(Path(temp_dir) / "replay_requests.jsonl")

            request = create_replay_request(
                job_run_id="job-1",
                failed_step_name="unit_step",
                replay_reason="unit test replay",
                replay_request_file=replay_file,
            )

            self.assertEqual(request["status"], "REQUESTED")
            self.assertTrue(Path(replay_file).exists())

    def test_load_missing_retry_policy_returns_disabled_policy(self):
        policy = load_retry_policy("does/not/exist.json")

        self.assertFalse(policy["enabled"])


if __name__ == "__main__":
    unittest.main()
