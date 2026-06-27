# V17.0.0 - Retry Framework, Recovery Handling, and Failure Replay

## Purpose

V17 adds a retry, recovery, and failure replay layer on top of the existing production-style orchestration framework.

This builds on:

- V14 orchestration and job control
- V15 runtime parameters and dependency validation
- V16 alerting and SLA monitoring

## New Files

```text
config/retries/customer_medallion_retry_policy.json
scripts/pipeline_retry.py
tests/test_pipeline_retry.py
tests/test_v17_orchestrator_retry.py
docs/v17_retry_recovery_failure_replay.md
output/recovery/.gitkeep
```

## V17 Capabilities

- Config-driven retry policy
- Step-level retry enablement
- Step-level retry attempt limits
- Retry event logging
- Recovery success tracking
- Recovery exhausted tracking
- Non-retryable exception handling
- Replay request creation
- Orchestrator integration with retry wrapper

## Runtime Outputs

```text
output/recovery/retry_events.csv
output/recovery/retry_events.jsonl
output/recovery/replay_requests.jsonl
```

These files are runtime outputs and should not be committed.

## Run Commands

```bash
python -m unittest tests.test_pipeline_retry
python -m unittest tests.test_v17_orchestrator_retry
python -m unittest discover tests
python -m scripts.pipeline_orchestrator --dry-run --run-date 2026-06-23
python -m scripts.pipeline_orchestrator --run-date 2026-06-23
```

## Interview Explanation

In V17, I added a config-driven retry and recovery framework to the orchestrated PySpark pipeline.

Each pipeline step can now define whether retry is enabled, how many retry attempts are allowed, and how retry events should be logged. The framework records retry attempts, recovery success, exhausted recovery, and non-retryable failures.

This makes the project closer to production Databricks Workflows, Azure Data Factory, or Airflow behavior, where transient step failures can be retried safely and replay requests can be created for controlled recovery.
