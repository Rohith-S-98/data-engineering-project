# End-to-End Data Engineering Pipeline Simulator

This project is a portfolio-ready Data Engineering pipeline simulator built with Python, PySpark, Delta Lake, Docker, API ingestion, database ingestion, advanced data quality, Databricks deployment structure, repository hygiene gates, and production-style framework patterns.

It demonstrates how customer data can be generated, extracted from API-style sources, extracted from relational database sources, landed into raw storage, validated through metadata-driven DQ rules, quarantined, transformed into a canonical model, historically tracked using SCD Type 2, observed through pipeline metrics, protected with alerting/retry controls, validated through CI/CD quality gates, organized for Databricks-style deployment, protected by repository hygiene checks, and run through a containerized local runtime.

```text
Current Version: v23.0.1
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
| v22.0.0 | Advanced Data Quality Rule Catalog |
| v23.0.0 | Databricks Asset Bundle Style Deployment Structure |
| v23.0.1 | Pre-V24 Professional Repository Cleanup |

---

## Current Architecture

```text
Mock API / SQLite Database / Raw Customer CSV
↓
V20 API Ingestion + V21 Database Ingestion + Raw Landing
↓
V22 Advanced DQ Rule Catalog
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
↓
V23 Databricks Asset Bundle Style Deployment Structure
↓
V23.0.1 Repository Hygiene Validation
```

---

## Features

- Python config-driven DQ pipeline
- Advanced metadata-driven DQ rule catalog
- Config-driven API ingestion framework
- Config-driven database ingestion framework
- Databricks Asset Bundle-style deployment structure
- Local Databricks bundle structure validation
- Repository hygiene validation gate
- Hardened `.gitignore` and `.dockerignore`
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
databricks.yml
resources/customer_medallion_job.yml
config/pipeline/local_config.json
config/rules/customer_dq_rules.json
config/rules/advanced_customer_dq_rule_catalog.json
config/api/customer_api_ingestion_config.json
config/database/customer_database_ingestion_config.json
config/jobs/customer_medallion_job.json
config/alerts/customer_medallion_alerts.json
config/retries/customer_medallion_retry_policy.json
configs/schema_contracts/bronze_customers_schema.json
configs/schema_contracts/silver_customers_schema.json
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

Validate repository hygiene:

```bash
python -m scripts.validate_repo_hygiene
```

Validate Databricks bundle-style structure:

```bash
python -m scripts.validate_databricks_bundle_structure
```

Run API ingestion:

```bash
python -m scripts.api_ingestion
```

Run database ingestion:

```bash
python -m scripts.database_ingestion
```

Run advanced DQ catalog evaluation:

```bash
python -m scripts.advanced_dq_rule_catalog
```

Run dry-run orchestration:

```bash
python -m scripts.pipeline_orchestrator --dry-run --run-date 2026-06-23
```

---

## Databricks Bundle-Style Deployment

V23 adds a local Databricks Asset Bundle-style structure:

```text
databricks.yml
resources/customer_medallion_job.yml
deployment/databricks/README.md
```

A real Databricks deployment would use:

```bash
databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle run customer_medallion_pipeline_job -t dev
```

This portfolio project validates the structure locally without requiring a Databricks workspace.

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

Run V23.0.1 quality gates:

```bash
python -m scripts.validate_python_project
python -m scripts.validate_config_files
python -m scripts.validate_docker_artifacts
python -m scripts.validate_databricks_bundle_structure
python -m scripts.validate_repo_hygiene
python -m unittest tests.test_v23_0_1_repo_hygiene
python -m unittest discover tests
python -m scripts.pipeline_orchestrator --dry-run --run-date 2026-06-23
python -m scripts.validate_runtime_cleanliness
```

Run full release verification:

```bash
python -m scripts.release_verification --version v23.0.1
```

Validate release tag safety before tagging:

```bash
python -m scripts.validate_release_tag --version v23.0.1
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
output/dq_reports/advanced_dq_catalog_summary.json
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
- Advanced data quality rule catalog
- Metadata-driven validation
- Databricks Asset Bundles
- Databricks deployment structure
- Databricks job/resource metadata
- Unity Catalog-style environment variables
- Repository hygiene validation
- CI/CD repository quality gates
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

## V23.0.0 - Databricks Asset Bundle Style Deployment Structure

V23 adds a Databricks Asset Bundle-style deployment structure for the pipeline.

Documentation:

```text
docs/v23_databricks_asset_bundle_structure.md
```

---

## V23.0.1 - Pre-V24 Professional Repository Cleanup

V23.0.1 cleans and hardens the repository before V24.

Highlights:

- Hardened `.gitignore`
- Hardened `.dockerignore`
- Added repository hygiene validator
- Added repository hygiene tests
- Added repository hygiene gate to release verification
- Added repository hygiene job to GitHub Actions CI
- Preserved required docs, configs, tests, fixtures, and runtime placeholders

Documentation:

```text
docs/v23_0_1_pre_v24_professional_cleanup.md
```

V23.0.1 interview explanation:

```text
Before starting V24, I performed a professional repository cleanup release. I hardened .gitignore and .dockerignore, added a repository hygiene validator, added tests to prevent generated data or runtime artifacts from being tracked, integrated the hygiene gate into release verification and CI, and preserved all required docs, tests, configs, and sample fixtures.
```
