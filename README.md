# End-to-End Data Engineering Pipeline Simulator

This project is a portfolio-ready Data Engineering pipeline simulator built with Python, PySpark, Delta Lake, and production-style framework patterns.

It demonstrates how customer data can be generated, ingested, validated, quarantined, transformed into a canonical model, historically tracked using SCD Type 2, observed through pipeline metrics, and exported as downstream-ready Reltio-style JSON output.

```text
Current Version: v13.0.1
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
- JSON summary metrics output
- JSONL and CSV historical metrics logs
- Reltio-style JSON payload generation
- Unit testing
- GitHub Actions CI

---

## V12 - SCD Type 2 Historical Tracking

V12 adds a customer history Delta table:

```text
data/gold/customer_history
```

Tracked business key:

```text
customer_id
```

Tracked attributes:

```text
first_name
last_name
email
phone
city
state
source_system
```

SCD2 metadata columns:

```text
effective_start_date
effective_end_date
is_current
record_hash
created_at
updated_at
```

Documentation:

```text
docs/v12_scd_type2_historical_tracking.md
```

---

## V13 - Data Observability + Pipeline Metrics Mart

V13 adds a production-style observability layer that summarizes pipeline health and data movement across the lakehouse pipeline.

It captures:

- Latest pipeline audit status
- Bronze row count
- Silver row count
- Quarantine row count
- Gold row count
- Customer History row count
- Latest DQ validation status
- Latest schema validation status
- Current watermark value
- Pending watermark value
- SCD Type 2 total history rows
- SCD Type 2 current rows
- SCD Type 2 expired rows
- Changed customer count

V13 writes metrics to:

```text
output/observability/pipeline_metrics_summary.json
output/observability/pipeline_metrics_history.jsonl
output/observability/pipeline_metrics_history.csv
```

Run command:

```bash
python -m scripts.pipeline_observability
```

Documentation:

```text
docs/v13_data_observability_metrics.md
```

---

## Pre-V14 Roadmap Handoff

The pre-V14 cleanup adds a single roadmap progress document:

```text
docs/12_month_data_engineering_roadmap_progress.md
```

This document summarizes the completed roadmap from v0.0.0 through v13.0.0 and defines the next planned milestone:

```text
v14.0.0 - Pipeline Orchestration + Job Control Framework
```

---

## Key Configuration

Pipeline configuration is stored in:

```text
config/pipeline/local_config.json
```

Important current config keys:

```json
{
    "storage_format": "delta",
    "lakehouse_write_strategy": "merge",
    "customer_history_output_path": "data/gold/customer_history",
    "scd2_business_keys": ["customer_id"],
    "scd2_tracked_columns": [
        "first_name",
        "last_name",
        "email",
        "phone",
        "city",
        "state",
        "source_system"
    ],
    "scd2_effective_start_column": "created_date",
    "observability_enabled": true,
    "observability_output_dir": "output/observability",
    "observability_summary_file": "output/observability/pipeline_metrics_summary.json",
    "observability_history_jsonl_file": "output/observability/pipeline_metrics_history.jsonl",
    "observability_history_csv_file": "output/observability/pipeline_metrics_history.csv"
}
```

---

## Folder Structure

```text
data-engineering-project/
├── .github/workflows/python-ci.yml
├── config/pipeline/local_config.json
├── config/rules/customer_dq_rules.json
├── configs/schema_contracts/bronze_customers_schema.json
├── configs/schema_contracts/silver_customers_schema.json
├── data/raw/
├── data/bronze/
├── data/silver/
├── data/gold/
├── data/audit/
├── docs/12_month_data_engineering_roadmap_progress.md
├── docs/v12_scd_type2_historical_tracking.md
├── docs/v13_data_observability_metrics.md
├── output/audit/
├── output/dq_reports/
├── output/quarantine/
├── output/logs/
├── output/observability/
├── output/reltio_payloads/
├── scripts/metrics_collector.py
├── scripts/pipeline_observability.py
├── scripts/pyspark_pipeline_runner.py
├── scripts/pyspark_customer_history_scd2.py
├── tests/test_metrics_collector.py
├── tests/test_scd_type2.py
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

Create clean sample data:

```bash
python -m scripts.create_sample_data
```

Run the full PySpark pipeline:

```bash
python -m scripts.pyspark_pipeline_runner
```

Run V13 observability:

```bash
python -m scripts.pipeline_observability
```

Run the V1 Python-only pipeline:

```bash
python main.py
```

---

## Testing

Run all tests:

```bash
python -m unittest discover tests
```

Expected result:

```text
OK
```

Recommended validation before every release:

```bash
python -m py_compile scripts/metrics_collector.py
python -m py_compile scripts/pipeline_observability.py
python -m unittest tests.test_metrics_collector
python -m unittest discover tests
python -m scripts.pyspark_pipeline_runner
python -m scripts.pipeline_observability
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
- Unit testing
- GitHub Actions CI
- Reltio-style JSON payload generation

---

## Future Enhancements

- Pipeline orchestration and job control
- API ingestion source
- Database ingestion source
- Great Expectations-style checks
- Data observability dashboard
- Docker support
- Databricks Asset Bundle structure
- Deployment documentation
