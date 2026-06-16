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