# Interview Explanation

## Project Summary

This project is an end-to-end Data Engineering pipeline simulator that demonstrates config-driven data quality, PySpark medallion processing, schema validation, incremental loading, audit tracking, and Reltio-style payload generation.

## How to Explain It

I built a local PySpark pipeline that simulates a Databricks-style Bronze/Silver/Gold architecture. Raw customer data is ingested into Bronze, data quality rules are applied in Silver, valid records are transformed into a Gold canonical model, and the final output is exported as a Reltio-style JSON payload.

## Key Engineering Features

### Config-Driven Design

Runtime paths, DQ rule files, schema contracts, and watermark settings are controlled through JSON configuration rather than hardcoded values.

### Data Quality Framework

DQ rules are stored in JSON and support not-null, allowed-values, and unique-key checks. Failed records are quarantined with error details.

### Severity-Based Control

HIGH severity DQ failures stop the pipeline. MEDIUM and LOW severity failures allow continuation with warnings.

### Audit Tracking

Every pipeline run gets a unique run ID and records STARTED, SUCCESS, or FAILED status in an audit file.

### Structured Error Handling

Custom exceptions separate configuration errors, DQ errors, ingestion errors, and full pipeline execution errors.

### Schema Validation

Bronze and Silver DataFrames are validated against JSON schema contracts. Validation results are written to an audit JSONL file.

### Incremental Load

The pipeline reads only new records using a `created_date` watermark. The watermark is staged after Bronze and committed only after the full pipeline succeeds, preventing data loss when DQ or Gold fails.

## Business Value

This project demonstrates how enterprise data pipelines protect downstream systems by combining DQ validation, schema contracts, quarantine handling, audit logs, and safe incremental processing.
