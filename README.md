# End-to-End Data Engineering Pipeline Simulator

This project is a portfolio-ready Data Engineering pipeline simulator built with Python, PySpark, Delta Lake, and production-style framework patterns.

It demonstrates how customer data can be generated, ingested, validated, quarantined, transformed into a canonical model, historically tracked using SCD Type 2, observed through pipeline metrics, protected with alerting/retry controls, and validated through CI/CD quality gates.

```text
Current Version: v18.0.0
```

---

## Project Versions

| Version | Feature |
|---|---|
| v0.0.0 | Project foundation and local repository setup |
| v1.0.0 | Python config-driven DQ pipeline |
| v2.0.0 | PySpark Bronze/Silver/Gold medallion pipeline |
| v3.0.0 | Databricks-style documentation and notebook structure |
| v4.0.0 | Production-style centralized pipeline configuration |
| v5.0.0 | Pipeline audit tracking |
| v6.0.0 | Severity-based DQ failure control |
| v7.0.0 | Custom exceptions and structured error handling |
| v8.0.0 | Schema Validation Framework |
| v9.0.0 | Incremental Load and Watermark Framework |
| v10.0.0 | Delta Lake / Lakehouse Storage Upgrade |
| v11.0.0 | Delta MERGE / Upsert Framework |
| v12.0.0 | SCD Type 2 / Historical Dimension Tracking |
| v13.0.0 | Data Observability + Pipeline Metrics Mart |
| v13.0.1 | Pre-V14 repository review and roadmap handoff cleanup |
| v13.0.2 | Markdown formatting cleanup before V14 |
| v14.0.0 | Pipeline Orchestration + Job Control Framework |
| v15.0.0 | Scheduling, Dependency Management, and Runtime Parameterization |
| v16.0.0 | Pipeline Alerting, Failure Notification, and SLA Monitoring |
| v17.0.0 | Retry Framework, Recovery Handling, and Failure Replay |
| v18.0.0 | CI/CD Hardening, Quality Gates, and Release Automation |

---

## Current Architecture

```text
Raw Customer CSV
↓
Bronze Schema Validation
↓
Incremental Watermark Filter
↓
Bronze Delta Table
↓
Silver Delta Table + Quarantine Delta Table
↓
Customer History SCD2 Delta Table
↓
Gold Canonical Delta Table
↓
Reltio-style JSON Payload
↓
Commit Watermark After Success
↓
Pipeline Audit Update
↓
V13 Observability Metrics Mart
↓
V14 Job Orchestration + Job Control
↓
V15 Runtime Parameters + Dependency Validation
↓
V16 Alerting + SLA Monitoring
↓
V17 Retry + Recovery + Failure Replay
↓
V18 CI/CD Quality Gates + Release Verification
```

---

## Features

- Python config-driven DQ pipeline
- PySpark medallion pipeline
- Bronze, Silver, Gold, Quarantine, and Customer History layers
- Delta Lake storage support
- Config-driven Delta MERGE / Upsert support
- Schema validation using JSON contracts
- Incremental load using watermark tracking
- Pending watermark staging to prevent data loss
- Severity-based DQ failure control
- Quarantine handling
- Pipeline audit tracking
- Custom exception handling
- SCD Type 2 customer history tracking
- Data observability metrics mart
- Alerting and SLA monitoring
- Retry, recovery, and replay handling
- Runtime parameterization and dry-run support
- Python syntax validation gate
- Config validation gate
- Runtime-output cleanliness validation gate
- Release verification and tag safety checks
- Staged GitHub Actions CI
- Reltio-style JSON payload generation

---

## Key Configuration

Pipeline configuration is stored in:

```text
config/pipeline/local_config.json
```

Main supporting configuration files:

```text
config/jobs/customer_medallion_job.json
config/rules/customer_dq_rules.json
config/alerts/customer_medallion_alerts.json
config/retries/customer_medallion_retry_policy.json
configs/schema_contracts/bronze_customers_schema.json
configs/schema_contracts/silver_customers_schema.json
```

---

## Folder Structure

```text
data-engineering-project/
├── .github/workflows/python-ci.yml
├── config/
├── configs/schema_contracts/
├── data/raw/
├── data/bronze/
├── data/silver/
├── data/gold/
├── data/audit/
├── docs/
├── output/
├── scripts/
├── tests/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## How to Run

Activate virtual environment:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create sample data:

```bash
python -m scripts.create_sample_data
```

Run the orchestrated pipeline:

```bash
python -m scripts.pipeline_orchestrator --run-date 2026-06-23
```

Run dry-run orchestration:

```bash
python -m scripts.pipeline_orchestrator --dry-run --run-date 2026-06-23
```

Run independent alerting:

```bash
python -m scripts.pipeline_alerting
```

---

## Testing and Release Verification

Run the full test suite:

```bash
python -m unittest discover tests
```

Run V18 quality gates:

```bash
python -m scripts.validate_python_project
python -m scripts.validate_config_files
python -m unittest tests.test_v18_quality_gates
python -m scripts.pipeline_orchestrator --dry-run --run-date 2026-06-23
python -m scripts.validate_runtime_cleanliness
```

Run full release verification:

```bash
python -m scripts.release_verification --version v18.0.0
```

Validate release tag safety before tagging:

```bash
python -m scripts.validate_release_tag --version v18.0.0
```

---

## Runtime Outputs

Runtime outputs are generated locally and intentionally ignored by Git:

```text
data/bronze/customer_bronze
data/silver/customer_valid
data/gold/customer_canonical
data/gold/customer_history
data/audit/schema_validation_audit.jsonl
data/audit/watermark_store.json
data/audit/pending_watermark_updates.json
output/audit/pipeline_runs.csv
output/quarantine/pyspark_customer_quarantine
output/dq_reports/pyspark_customer_dq_report.json
output/reltio_payloads/customer_payload_json
output/observability/pipeline_metrics_summary.json
output/observability/pipeline_metrics_history.jsonl
output/observability/pipeline_metrics_history.csv
output/job_control/job_runs.csv
output/job_control/step_runs.csv
output/runtime_parameters/runtime_parameters_<job_run_id>.json
output/alerts/alert_events.jsonl
output/alerts/alert_events.csv
output/alerts/notification_summary.txt
output/recovery/retry_events.csv
output/recovery/retry_events.jsonl
output/recovery/replay_requests.jsonl
```

Only `.gitkeep` placeholders are committed for runtime output folders.

---

## Skills Demonstrated

- Python
- PySpark
- Delta Lake
- Data Engineering
- Medallion architecture
- Config-driven framework design
- Delta MERGE / Upsert
- SCD Type 2 history tracking
- Data observability
- Pipeline metrics mart
- Data quality validation
- Schema validation
- Incremental loading
- Watermark management
- Quarantine handling
- Audit logging
- Structured exception handling
- Alerting and SLA monitoring
- Retry and recovery handling
- CI/CD quality gates
- Release verification
- GitHub Actions CI
- Reltio-style JSON payload generation

---

## V14.0.0 - Pipeline Orchestration + Job Control Framework

V14 adds a config-driven orchestration and job-control layer on top of the existing PySpark medallion pipeline.

Highlights:

- Job-level orchestration configuration
- Step-level execution control
- Enabled/disabled step handling
- Critical vs optional step handling
- Expected status validation
- Job and step run audit logging

Documentation:

```text
docs/v14_pipeline_orchestration_job_control.md
```

---

## V15.0.0 - Scheduling, Dependency Management, and Runtime Parameterization

V15 upgrades orchestration with runtime parameters, dependency validation, dry-run support, and schedule metadata.

Highlights:

- Runtime parameter defaults
- Manual, scheduled, and backfill run modes
- Dry-run execution mode
- Step dependency metadata
- Runtime parameter snapshots

Documentation:

```text
docs/v15_scheduling_dependency_runtime_parameters.md
```

---

## V16.0.0 - Pipeline Alerting, Failure Notification, and SLA Monitoring

V16 adds a production-style alerting and SLA monitoring layer to the orchestration framework.

Highlights:

- Alerting configuration
- Pipeline failure alert generation
- Critical and optional step failure alerts
- Pipeline and step duration SLA monitoring
- DQ, schema, and quarantine threshold checks
- Alert event JSONL and CSV outputs
- Notification summary output

---

## V17.0.0 - Retry Framework, Recovery Handling, and Failure Replay

V17 adds retry, recovery, and replay handling to the production-style pipeline orchestration framework.

Highlights:

- Config-driven retry policy
- Step-level retry enablement
- Retry attempt limits
- Retry event logging
- Recovery success and exhausted tracking
- Non-retryable exception handling
- Replay request creation utility
- Retry wrapper integration into the orchestrator

Documentation:

```text
docs/v17_retry_recovery_failure_replay.md
```

---

## V18.0.0 - CI/CD Hardening, Quality Gates, and Release Automation

V18 adds release-readiness controls on top of the V17 retry, recovery, and replay framework.

Highlights:

- Hardened GitHub Actions into staged CI quality gates
- Added Python syntax validation
- Added config file validation
- Added targeted V17/V18 tests
- Added full test gate
- Added dry-run orchestrator gate
- Added runtime-output cleanliness validation
- Added release verification runner
- Added release tag safety check
- Added pull request checklist
- Hardened Delta table existence detection for clean local runs
- Ignored generated raw sample input files

Documentation:

```text
docs/v18_cicd_quality_gates_release_automation.md
docs/pull_request_checklist.md
```

V18 interview explanation:

```text
I hardened the CI/CD process for my PySpark medallion pipeline by splitting validation into staged quality gates. The release process now validates Python syntax, JSON configs, targeted framework tests, full tests, dry-run orchestration, runtime-output cleanliness, release verification, and tag safety before a version is released.
```
