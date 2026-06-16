# Interview Explanation

## Project Introduction

I built an end-to-end data engineering pipeline that simulates a customer data processing workflow.

The project has two versions.

V1 is a Python-based config-driven DQ framework.

V2 is a PySpark-based medallion architecture pipeline with Bronze, Silver, and Gold layers.

---

## How Data Flows

Raw customer data is first generated as a CSV file.

In the PySpark version, the raw CSV is ingested into the Bronze layer as Parquet.

Then the Silver layer applies data quality rules from a JSON config file.

Records that pass all rules are written as valid Silver records.

Records that fail rules are written into quarantine.

A DQ report is generated to show total rows, valid rows, quarantined rows, and failed rule counts.

Finally, the Gold layer transforms valid records into a canonical customer model and exports a Reltio-style JSON payload.

---

## Why I Used Config-Driven DQ

I used config-driven DQ because hardcoding validation logic is not scalable.

With a JSON config file, new rules can be added or modified without changing the core engine logic.

This makes the pipeline more flexible and closer to enterprise data engineering patterns.

---

## Why Bronze, Silver, and Gold Layers Are Used

Bronze keeps raw ingested data.

Silver applies validation, cleansing, and quality checks.

Gold prepares business-ready canonical output for downstream systems.

This separation improves traceability, debugging, replay, and maintainability.

---

## Key Technical Highlights

- Python pipeline implementation
- PySpark pipeline implementation
- JSON-based DQ rule config
- Duplicate detection using PySpark window functions
- Valid and quarantine split
- DQ report generation
- Gold canonical transformation
- Reltio-style JSON payload output
- Unit testing
- GitHub Actions CI
- Git branching, pull requests, and version tags

---

## Resume-Ready Summary

Built an end-to-end config-driven data quality pipeline using Python and PySpark. Implemented Bronze, Silver, and Gold layers, JSON-based validation rules, quarantine handling, DQ reporting, canonical customer transformation, Reltio-style JSON payload generation, unit tests, and GitHub Actions CI.