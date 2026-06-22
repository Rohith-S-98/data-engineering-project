# End-to-End Data Engineering Pipeline Simulator

This project is a portfolio-ready Data Engineering pipeline simulator built with Python, PySpark, Delta Lake, and production-style framework patterns.

It demonstrates how customer data can be generated, ingested, validated, quarantined, transformed into a canonical model, historically tracked using SCD Type 2, and exported as downstream-ready Reltio-style JSON output.

```text
Current Version: v12.0.0
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
```

---

## Features

- Python config-driven DQ pipeline
- PySpark medallion pipeline
- Bronze, Silver, Gold, and Quarantine layers
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

## Key Configuration

Pipeline configuration is stored in:

```text
config/pipeline/local_config.json
```

Important V12 config keys:

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
  "scd2_effective_start_column": "created_date"
}
```

---

## Folder Structure

```text
data-engineering-project/
├── .github/
│   └── workflows/
│       └── python-ci.yml
├── config/
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
│   ├── v9_incremental_load_watermark.md
│   ├── v10_delta_lakehouse_storage_upgrade.md
│   ├── v11_delta_merge_upsert_framework.md
│   └── v12_scd_type2_historical_tracking.md
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
│   ├── lakehouse_io.py
│   ├── pipeline_config.py
│   ├── pyspark_bronze_ingestion.py
│   ├── pyspark_customer_history_scd2.py
│   ├── pyspark_gold_canonical.py
│   ├── pyspark_pipeline_runner.py
│   ├── pyspark_silver_dq.py
│   ├── run_metadata.py
│   ├── scd_type2.py
│   ├── schema_validation_framework.py
│   ├── spark_session.py
│   └── watermark_manager.py
├── tests/
│   ├── test_config_driven_dq.py
│   ├── test_dq_decision.py
│   ├── test_lakehouse_io.py
│   ├── test_pipeline_config.py
│   ├── test_run_metadata.py
│   ├── test_scd_type2.py
│   ├── test_schema_validation_framework.py
│   └── test_watermark_manager.py
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
output/audit/pipeline_runs.csv
output/quarantine/pyspark_customer_quarantine
output/dq_reports/pyspark_customer_dq_report.json
output/reltio_payloads/customer_payload_json
```

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

- API ingestion source
- Database ingestion source
- Great Expectations-style checks
- Data observability dashboard
- Docker support
- Databricks Asset Bundle structure
- Deployment documentation
