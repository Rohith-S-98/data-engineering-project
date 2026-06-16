# End-to-End Data Engineering Pipeline Simulator

This project is a Python-based data engineering pipeline that simulates a real-world customer data processing flow.

It demonstrates how raw customer data can be generated, validated using config-driven data quality rules, split into valid and quarantined records, and summarized through a DQ report.

The project is inspired by enterprise data engineering workflows such as medallion architecture, config-driven validation, quarantine handling, and pipeline orchestration.

---

## Project Architecture

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

## V2: PySpark / Databricks-Style Pipeline

This project also includes a PySpark-based pipeline that simulates a Databricks-style medallion architecture.

The PySpark version processes customer data through Bronze, Silver, and Gold layers.

### V2 Architecture

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