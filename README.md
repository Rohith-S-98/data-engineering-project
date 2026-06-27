# End-to-End Data Engineering Pipeline Simulator

This project is a portfolio-ready Data Engineering pipeline simulator built with Python, PySpark, Delta Lake, Docker, API ingestion, database ingestion, and production-style framework patterns.

It demonstrates how customer data can be generated, extracted from API-style sources, extracted from relational database sources, landed into raw storage, validated, quarantined, transformed into a canonical model, historically tracked using SCD Type 2, observed through pipeline metrics, protected with alerting/retry controls, validated through CI/CD quality gates, and run through a containerized local runtime.

```text
Current Version: v21.0.0
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
| v19.0.0 | Docker Containerized Local Runtime |
| v20.0.0 | API Ingestion Framework |
| v21.0.0 | Database Ingestion Framework |

---

## Current Architecture

```text
Mock API / SQLite Database / Raw Customer CSV
↓
V20 API Ingestion + V21 Database Ingestion + Raw Landing
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
↓
V19 Docker Containerized Runtime
```

---

## Features

- Python config-driven DQ pipeline
- Config-driven API ingestion framework
- Config-driven database ingestion framework
- Local SQLite source extraction for deterministic testing
- Mock paginated source API fixture
- API and database field landing into raw customer schema
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
- Docker artifact validation gate
- Release verification and tag safety checks
- Staged GitHub Actions CI
- Dockerfile and Docker Compose local runtime
- Reltio-style JSON payload generation

---

## Key Configuration

```text
config/pipeline/local_config.json
config/api/customer_api_ingestion_config.json
config/database/customer_database_ingestion_config.json
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
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── config/
├── configs/schema_contracts/
├── data/api/
├── data/database/
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

## How to Run Locally

Activate virtual environment:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run API ingestion:

```bash
python -m scripts.api_ingestion
```

Run database ingestion:

```bash
python -m scripts.database_ingestion
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

---

## How to Run with Docker

Build the image:

```bash
docker compose build
```

Run dry-run orchestration in Docker:

```bash
docker compose run --rm data-engineering-pipeline
```

Run Docker-based release verification:

```bash
docker compose run --rm release-verification
```

---

## Testing and Release Verification

Run the full test suite:

```bash
python -m unittest discover tests
```

Run V21 quality gates:

```bash
python -m scripts.validate_python_project
python -m scripts.validate_config_files
python -m scripts.validate_docker_artifacts
python -m unittest tests.test_v21_database_ingestion
python -m scripts.database_ingestion
python -m unittest discover tests
python -m scripts.pipeline_orchestrator --dry-run --run-date 2026-06-23
python -m scripts.validate_runtime_cleanliness
```

Run full release verification:

```bash
python -m scripts.release_verification --version v21.0.0
```

Validate release tag safety before tagging:

```bash
python -m scripts.validate_release_tag --version v21.0.0
```

---

## Runtime Outputs

Runtime outputs are generated locally and intentionally ignored by Git:

```text
data/database/customer_source.db
data/raw/customer_data.csv
data/raw/customer_data_clean.csv
data/raw/customer_data_dirty.csv
data/raw/customer_data_api.csv
data/raw/customer_data_db.csv
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
- API ingestion
- Database ingestion
- SQLite source extraction
- SQL query-based extraction
- Config-driven source extraction
- PySpark
- Delta Lake
- Docker
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
- Containerized runtime design
- Release verification
- GitHub Actions CI
- Reltio-style JSON payload generation

---

## V20.0.0 - API Ingestion Framework

V20 adds a config-driven API ingestion layer before the medallion pipeline.

Highlights:

- Added API ingestion source config
- Added mock paginated API response fixture
- Added reusable API ingestion runner
- Added API field mapping into raw customer schema
- Added generated raw API landing CSV output
- Added V20 API ingestion unit tests
- Added API config into config validation

Documentation:

```text
docs/v20_api_ingestion_framework.md
```

V20 interview explanation:

```text
I added an API ingestion layer to my data engineering project. It uses a config-driven source definition, supports paginated API-style payloads, maps source API fields into my raw customer schema, writes a raw CSV landing file, and includes unit tests for config validation, pagination, missing source handling, and output generation.
```

---

## V21.0.0 - Database Ingestion Framework

V21 adds a config-driven relational database ingestion layer before the medallion pipeline.

Highlights:

- Added database ingestion source config
- Added local SQLite source database seeding
- Added SQL query-based extraction
- Added reusable database ingestion runner
- Added generated raw DB landing CSV output
- Added V21 database ingestion unit tests
- Added database config into config validation
- Added V21 targeted tests into release verification

Documentation:

```text
docs/v21_database_ingestion_framework.md
```

V21 interview explanation:

```text
I added a database ingestion layer to my data engineering project. It uses a config-driven SQLite source definition, seeds a local source table for reproducibility, runs a controlled SQL SELECT extraction query, writes records into a raw customer landing CSV, and includes unit tests for config validation, invalid query protection, missing database handling, and output generation.
```
