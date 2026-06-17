# End-to-End Data Engineering Pipeline Simulator

This project is a portfolio-ready Data Engineering pipeline simulator built with Python and PySpark. It demonstrates how customer data can be generated, ingested, validated, separated into valid and quarantined records, transformed into a canonical model, and exported as downstream-ready Reltio-style JSON output.

The project is inspired by real enterprise workflows such as medallion architecture, config-driven data quality, schema validation, incremental loading, audit tracking, exception handling, and MDM-style payload generation.

---

Current Version: v10.0.0

---

## Project Versions

| Version | Feature |
|---|---|
| v1.0.0 | Python config-driven DQ pipeline |
| v2.0.0 | PySpark Bronze/Silver/Gold medallion pipeline |
| v3.0.0 | Databricks-style documentation and interview explanation |
| v4.0.0 | Production-style centralized pipeline configuration |
| v5.0.0 | Pipeline audit tracking |
| v6.0.0 | Severity-based DQ failure control |
| v7.0.0 | Custom exceptions and structured error handling |
| v8.0.0 | Schema Validation Framework |
| v9.0.0 | Incremental Load and Watermark Framework |
| v10.0.0 | Delta Lake / Lakehouse Storage Upgrade | Upgraded Bronze, Silver, Gold, and Quarantine outputs from Parquet-only paths to configurable Delta Lake storage with Delta transaction log validation. |

---

## Current Architecture

```text
Raw Customer CSV
        ↓
Bronze Schema Validation
        ↓
Incremental Watermark Filter
        ↓
Bronze Parquet
        ↓
Silver DQ Validation
        ↓
Silver Schema Validation
        ↓
Severity-Based DQ Decision
        ↓
Gold Canonical Transformation
        ↓
Reltio-Style JSON Payload
        ↓
Commit Watermark After Success
        ↓
Pipeline Audit Update
```

---

## Features

- Python config-driven DQ pipeline
- PySpark medallion pipeline
- Bronze, Silver, and Gold layer processing
- JSON-based DQ rules
- Not-null, unique-key, and allowed-values validation
- Quarantine handling
- DQ summary reporting
- Severity-based pipeline stop control
- Pipeline audit tracking
- Custom exception handling
- JSON schema validation framework
- Incremental load using watermark tracking
- Pending watermark staging to prevent data loss
- Reltio-style JSON payload generation
- GitHub Actions CI

---

## Folder Structure

```text
data-engineering-project/
├── .github/
│   └── workflows/
│       └── python-ci.yml
├── config/
│   ├── log4j2.properties
│   ├── pipeline/
│   │   └── local_config.json
│   └── rules/
│       └── customer_dq_rules.json
├── configs/
│   └── schema_contracts/
│       ├── bronze_customers_schema.json
│       └── silver_customers_schema.json
├── data/
│   ├── raw/
│   │   ├── customer_data.csv
│   │   ├── customer_data_clean.csv
│   │   └── customer_data_dirty.csv
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── audit/
├── docs/
│   ├── architecture.md
│   ├── interview_explanation.md
│   ├── v5_pipeline_audit_tracking.md
│   ├── v6_severity_based_dq_control.md
│   ├── v7_custom_exceptions_error_handling.md
│   ├── v8_schema_validation_framework.md
│   └── v9_incremental_load_watermark.md
├── output/
│   ├── audit/
│   ├── dq_reports/
│   ├── quarantine/
│   ├── logs/
│   └── reltio_payloads/
├── scripts/
│   ├── config_driven_dq.py
│   ├── create_sample_data.py
│   ├── dq_decision.py
│   ├── exceptions.py
│   ├── pipeline_config.py
│   ├── pyspark_bronze_ingestion.py
│   ├── pyspark_silver_dq.py
│   ├── pyspark_gold_canonical.py
│   ├── pyspark_pipeline_runner.py
│   ├── run_metadata.py
│   ├── schema_validation_framework.py
│   ├── spark_session.py
│   └── watermark_manager.py
├── tests/
│   ├── test_config_driven_dq.py
│   ├── test_dq_decision.py
│   ├── test_pipeline_config.py
│   ├── test_run_metadata.py
│   ├── test_schema_validation_framework.py
│   └── test_watermark_manager.py
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Data Quality Rules

DQ rules are stored in:

```text
config/rules/customer_dq_rules.json
```

Supported rule types:

```text
not_null
unique
allowed_values
```

Severity behavior:

| Severity | Behavior |
|---|---|
| HIGH | Stops the pipeline if failed |
| MEDIUM | Allows continuation with warning |
| LOW | Allows continuation with warning |

---

## Schema Validation

Schema contracts are stored in:

```text
configs/schema_contracts/
```

Schema validation checks:

- Required columns
- Unexpected columns
- Data type mismatches
- Nullability violations

Audit output:

```text
data/audit/schema_validation_audit.jsonl
```

---

## Incremental Load and Watermark

V9 adds incremental processing using:

```text
created_date
```

Watermark files:

```text
data/audit/watermark_store.json
data/audit/pending_watermark_updates.json
```

The watermark is staged after Bronze and committed only after the full pipeline succeeds.

---

## How to Run

Activate virtual environment:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create clean sample data:

```bash
python -m scripts.create_sample_data
```

Run the full PySpark pipeline:

```bash
python -m scripts.pyspark_pipeline_runner
```

Run V1 Python pipeline:

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

---

## Outputs

```text
data/bronze/customer_bronze
data/silver/customer_valid
data/gold/customer_canonical
data/audit/schema_validation_audit.jsonl
data/audit/watermark_store.json
output/audit/pipeline_runs.csv
output/quarantine/pyspark_customer_quarantine
output/dq_reports/pyspark_customer_dq_report.json
output/reltio_payloads/customer_payload_json
```

---

## Dirty Data Demo

To test DQ failure behavior, replace the active raw file with dirty data:

```bash
cp data/raw/customer_data_dirty.csv data/raw/customer_data.csv
rm -f data/audit/watermark_store.json data/audit/pending_watermark_updates.json
python -m scripts.pyspark_pipeline_runner
```

Expected behavior:

```text
Bronze schema validation PASSED
Watermark staged
Silver DQ status FAILED
Pipeline stopped because HIGH severity DQ rules failed
Watermark NOT committed
```

Restore clean data:

```bash
cp data/raw/customer_data_clean.csv data/raw/customer_data.csv
rm -f data/audit/watermark_store.json data/audit/pending_watermark_updates.json
python -m scripts.pyspark_pipeline_runner
```

---

## CI/CD

GitHub Actions runs unit tests on push and pull request to `main`.

Workflow file:

```text
.github/workflows/python-ci.yml
```

---

## Skills Demonstrated

- Python
- PySpark
- Data Engineering
- Medallion architecture
- Config-driven framework design
- Data quality validation
- Quarantine handling
- Audit logging
- Schema validation
- Incremental loading
- Watermark management
- Structured exception handling
- Unit testing
- GitHub Actions CI
- Reltio-style JSON payload generation

---

## Future Enhancements

- Delta Lake support
- Databricks notebook version
- Databricks Asset Bundle structure
- Great Expectations-style checks
- API ingestion source
- Database ingestion source
- DQ metrics dashboard
- Docker support
- Deployment documentation

## V10 - Delta Lake / Lakehouse Upgrade

The pipeline now supports configurable Lakehouse storage through the `storage_format` config key.

Supported values:

- `parquet`
- `delta`

For local V10 execution, the project uses Delta Lake by default:

```json
"storage_format": "delta"