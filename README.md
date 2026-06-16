# End-to-End Data Engineering Pipeline Simulator

This project is a data engineering pipeline simulator that demonstrates how customer data can be generated, ingested, validated, separated into valid and quarantined records, transformed into a canonical model, and exported as downstream-ready output.

The project is inspired by real enterprise data engineering workflows such as:

* Medallion architecture
* Config-driven data quality validation
* Quarantine handling
* DQ reporting
* Pipeline orchestration
* PySpark-based transformation
* Reltio-style payload generation

---

## Project Versions

This repository contains two versions of the pipeline:

| Version | Description                                                  |
| ------- | ------------------------------------------------------------ |
| V1      | Python-based config-driven DQ pipeline                       |
| V2      | PySpark / Databricks-style Bronze, Silver, and Gold pipeline |

---

# V1: Python Config-Driven DQ Pipeline

## V1 Architecture

```text
Raw Customer Data
        ↓
Sample Data Generator
        ↓
Config-Driven DQ Rules
        ↓
DQ Validation Engine
        ↓
Valid Records + Quarantine Records
        ↓
DQ Summary Report
        ↓
End-to-End Pipeline Runner
```

## V1 Features

* Generates sample customer source data
* Reads raw CSV input
* Applies JSON-based configurable data quality rules
* Supports not-null validation
* Supports unique key validation
* Supports allowed values validation
* Splits data into valid and quarantined records
* Generates DQ summary report in JSON format
* Provides an end-to-end runner through `main.py`
* Includes logging
* Includes unit tests
* Includes GitHub Actions CI

## V1 Main Components

```text
scripts/create_sample_data.py
scripts/ingest_data.py
scripts/generate_dq_report.py
scripts/config_driven_dq.py
scripts/logger_config.py
main.py
```

## How to Run V1 Pipeline

```bash
python3 main.py
```

This executes:

```text
Create raw customer data
        ↓
Run config-driven DQ validation
        ↓
Generate valid records
        ↓
Generate quarantine records
        ↓
Generate DQ report
```

---

# V2: PySpark / Databricks-Style Pipeline

This project also includes a PySpark-based pipeline that simulates a Databricks-style medallion architecture.

The PySpark version processes customer data through Bronze, Silver, and Gold layers.

## V2 Architecture

```text
Raw Customer CSV
        ↓
Bronze Layer
Raw data is ingested using PySpark and stored as Parquet
        ↓
Silver Layer
Config-driven DQ rules are applied using PySpark
Valid and quarantined records are separated
        ↓
Gold Layer
Valid customer records are transformed into a canonical customer model
        ↓
Reltio-Style Payload
Gold data is exported as JSON payload output
```

## V2 Features

* Reads raw customer CSV using PySpark
* Writes Bronze data as Parquet
* Reads DQ rules from JSON config
* Applies PySpark-based DQ validation
* Uses window functions for duplicate detection
* Separates valid and quarantined records
* Writes Silver valid records
* Writes quarantine records
* Generates DQ report
* Transforms Silver records into Gold canonical customer model
* Exports Reltio-style JSON payload
* Provides an end-to-end PySpark pipeline runner

## V2 Main Components

```text
scripts/spark_session.py
scripts/pyspark_smoke_test.py
scripts/pyspark_bronze_ingestion.py
scripts/pyspark_silver_dq.py
scripts/pyspark_gold_canonical.py
scripts/pyspark_pipeline_runner.py
```

## How to Run V2 Pipeline

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Run the full PySpark pipeline:

```bash
python -m scripts.pyspark_pipeline_runner
```

This executes:

```text
Bronze ingestion
        ↓
Silver DQ validation
        ↓
Gold canonical transformation
        ↓
Reltio-style JSON payload generation
```
---

## V4: Production-Style Pipeline Configuration

The project now includes a production-style pipeline configuration layer.

Instead of hardcoding input and output paths inside the PySpark scripts, the pipeline reads runtime paths and settings from a JSON config file.

### Config File

```text
config/pipeline/local_config.json
```

### Config Loader

```text
scripts/pipeline_config.py
```

### Why This Matters

This makes the pipeline easier to maintain and prepares it for environment-based execution such as:

```text
local
dev
qa
prod
```

With this approach, Bronze, Silver, and Gold scripts can use the same core logic while changing only the configuration file for different environments.

### V4 Improvements

* Added centralized pipeline config file
* Added config loader with required-key validation
* Refactored Bronze ingestion to use config paths
* Refactored Silver DQ validation to use config paths
* Refactored Gold canonical transformation to use config paths
* Added unit tests for config loader


---

# Data Quality Rules

The DQ rules are stored in:

```text
config/rules/customer_dq_rules.json
```

Example rule:

```json
{
  "rule_name": "email_not_null",
  "column": "email",
  "rule_type": "not_null",
  "severity": "HIGH"
}
```

Supported rule types:

```text
not_null
unique
allowed_values
```

---

# Folder Structure

```text
data-engineering-project/
│
├── .github/
│   └── workflows/
│       └── python-ci.yml
│
├── config/
│   └── rules/
│       └── customer_dq_rules.json
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── docs/
├── notebooks/
│
├── output/
│   ├── dq_reports/
│   ├── quarantine/
│   ├── logs/
│   └── reltio_payloads/
│
├── scripts/
│   ├── __init__.py
│   ├── create_sample_data.py
│   ├── ingest_data.py
│   ├── generate_dq_report.py
│   ├── config_driven_dq.py
│   ├── logger_config.py
│   ├── spark_session.py
│   ├── pyspark_smoke_test.py
│   ├── pyspark_bronze_ingestion.py
│   ├── pyspark_silver_dq.py
│   ├── pyspark_gold_canonical.py
│   └── pyspark_pipeline_runner.py
│
├── tests/
│   ├── __init__.py
│   └── test_config_driven_dq.py
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Outputs

## V1 Outputs

```text
data/processed/customer_valid.csv
output/quarantine/customer_quarantine.csv
output/dq_reports/config_driven_customer_dq_report.json
output/logs/pipeline.log
```

## V2 Outputs

```text
data/bronze/customer_bronze
data/silver/customer_valid
data/gold/customer_canonical
output/quarantine/pyspark_customer_quarantine
output/dq_reports/pyspark_customer_dq_report.json
output/reltio_payloads/customer_payload_json
```

---

# Testing

Run unit tests:

```bash
python3 -m unittest discover tests
```

Expected result:

```text
OK
```

---

# CI/CD

This project uses GitHub Actions to run unit tests automatically on:

```text
push to main
pull request to main
```

Workflow file:

```text
.github/workflows/python-ci.yml
```

---

# Skills Demonstrated

* Python
* PySpark
* CSV processing
* JSON config handling
* Data quality validation
* Config-driven framework design
* Quarantine handling
* DQ reporting
* Logging
* Unit testing
* GitHub Actions CI
* Parquet read/write
* Medallion architecture
* Bronze, Silver, Gold layer design
* Window functions
* Canonical data modeling
* Reltio-style JSON payload generation
* Git and GitHub version control

---

# Future Enhancements

* Add Delta Lake support
* Add Databricks notebook version
* Add Databricks Asset Bundle structure
* Add schema validation
* Add Great Expectations-style checks
* Add API ingestion source
* Add database ingestion source
* Add dashboard for DQ metrics
* Add Docker support
* Add deployment documentation