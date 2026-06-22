# 12-Month Data Engineering Roadmap Progress

## Current Status

The project has completed versions v0.0.0 through v13.0.0.

The current stable functional release is:

```text
v13.0.0 - Data Observability + Pipeline Metrics Mart
```

The pre-V14 cleanup release is:

```text
v13.0.1 - Pre-V14 Repository Review and Roadmap Handoff Cleanup
```

Latest confirmed Git state before the pre-V14 cleanup branch:

```text
main / HEAD = df9265f
v13.0.0    = df9265f
v12.0.0    = 1791602
v11.0.0    = 37ae3b4
```

---

## Completed Versions

### v0.0.0 - Project Foundation and Local Repository Setup

Established the base repository structure, Git workflow, Python environment, and local project foundation.

### v1.0.0 - Python Config-Driven DQ Pipeline

Built the first Python-based data quality pipeline using configuration-driven rules.

### v2.0.0 - PySpark Bronze/Silver/Gold Medallion Pipeline

Introduced PySpark and created a medallion-style pipeline with Bronze, Silver, and Gold layers.

### v3.0.0 - Databricks-Style Documentation and Notebook Structure

Added Databricks-style documentation and notebook-oriented structure for future cloud migration.

### v4.0.0 - Production-Style Centralized Pipeline Configuration

Centralized pipeline paths, rule files, output paths, and environment settings into a reusable config file.

### v5.0.0 - Pipeline Audit Tracking

Added pipeline run metadata and audit tracking to capture pipeline status, timestamps, run IDs, and failures.

### v6.0.0 - Severity-Based DQ Failure Control

Introduced severity-based DQ handling so critical rules can fail the pipeline while warning-level rules can continue.

### v7.0.0 - Custom Exceptions and Structured Error Handling

Added custom exception classes and structured error handling for cleaner production-style failure management.

### v8.0.0 - Schema Validation Framework

Added JSON-based schema contracts and validation logic for Bronze and Silver datasets.

### v9.0.0 - Incremental Load and Watermark Framework

Added incremental loading using watermark tracking and pending watermark staging to avoid committing watermarks before successful pipeline completion.

### v10.0.0 - Delta Lake / Lakehouse Storage Upgrade

Upgraded storage from normal file outputs to Delta Lake-style lakehouse paths.

### v11.0.0 - Delta MERGE / Upsert Framework

Added Delta MERGE/upsert support for Bronze, Silver, Quarantine, and Gold layers.

### v12.0.0 - SCD Type 2 / Historical Dimension Tracking

Added Customer History SCD2 Delta table with current and expired record tracking.

Validated behavior:

```text
Initial load:
Total history rows = 4
Current rows       = 4

Changed-data validation:
Total history rows = 6
Current rows       = 5
Expired rows       = 1
```

### v13.0.0 - Data Observability + Pipeline Metrics Mart

Added a production-style observability layer.

Captured metrics:

```text
Pipeline status
Schema validation status
DQ status
Bronze row count
Silver row count
Quarantine row count
Gold row count
Customer History row count
Current watermark
Pending watermark
SCD2 total rows
SCD2 current rows
SCD2 expired rows
Changed customer count
```

Generated outputs:

```text
output/observability/pipeline_metrics_summary.json
output/observability/pipeline_metrics_history.jsonl
output/observability/pipeline_metrics_history.csv
```

### v13.0.1 - Pre-V14 Repository Review and Roadmap Handoff Cleanup

Prepared the repository for V14 by cleaning documentation and creating a roadmap handoff baseline.

Cleanup scope:

```text
README cleanup
local_config.json formatting
.gitignore cleanup
runtime folder .gitkeep placeholders
12-month roadmap progress document
pre-V14 handoff notes
```

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

## Current Core Files

```text
README.md
requirements.txt
config/pipeline/local_config.json
config/rules/customer_dq_rules.json
configs/schema_contracts/bronze_customers_schema.json
configs/schema_contracts/silver_customers_schema.json
scripts/create_sample_data.py
scripts/pipeline_config.py
scripts/lakehouse_io.py
scripts/pyspark_bronze_ingestion.py
scripts/pyspark_silver_dq.py
scripts/pyspark_customer_history_scd2.py
scripts/pyspark_gold_canonical.py
scripts/pyspark_pipeline_runner.py
scripts/scd_type2.py
scripts/watermark_manager.py
scripts/run_metadata.py
scripts/schema_validation_framework.py
scripts/exceptions.py
scripts/metrics_collector.py
scripts/pipeline_observability.py
tests/test_scd_type2.py
tests/test_metrics_collector.py
docs/v12_scd_type2_historical_tracking.md
docs/v13_data_observability_metrics.md
docs/12_month_data_engineering_roadmap_progress.md
```

---

## Validation Commands

```bash
python -m py_compile scripts/metrics_collector.py
python -m py_compile scripts/pipeline_observability.py
python -m unittest tests.test_metrics_collector
python -m unittest discover tests
python -m scripts.pyspark_pipeline_runner
python -m scripts.pipeline_observability
```

Expected result:

```text
Unit tests pass
Full test suite passes
Pipeline completes successfully
Observability completes successfully
```

---

## New Chat Handoff Summary

Use this before starting V14 in a new chat:

```text
Continue my 12-month Data Engineering roadmap project in the Career group.

Repo:
https://github.com/Rohith-S-98/data-engineering-project.git

Project:
data-engineering-project

Do not restart from basics. Continue exactly from the completed V13/V13.0.1 baseline and start V14 only after verifying the repo state.

Completed versions:
v0.0.0  → Project foundation and local repository setup
v1.0.0  → Python config-driven DQ pipeline
v2.0.0  → PySpark Bronze/Silver/Gold medallion pipeline
v3.0.0  → Databricks-style docs and notebook structure
v4.0.0  → Production-style centralized config
v5.0.0  → Pipeline audit tracking
v6.0.0  → Severity-based DQ failure control
v7.0.0  → Custom exceptions and structured error handling
v8.0.0  → Schema Validation Framework
v9.0.0  → Incremental Load + Watermark Framework
v10.0.0 → Delta Lake / Lakehouse Storage Upgrade
v11.0.0 → Delta MERGE / Upsert Framework
v12.0.0 → SCD Type 2 / Historical Dimension Tracking
v13.0.0 → Data Observability + Pipeline Metrics Mart
v13.0.1 → Pre-V14 repository review and roadmap handoff cleanup

Current architecture:
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

Before giving V14 implementation steps, first verify:
main / HEAD
v13.0.1 tag
v13.0.0 tag
v12.0.0 tag
v11.0.0 tag

Then start:
V14.0.0 → Pipeline Orchestration + Job Control Framework
```

---

## Next Version

```text
v14.0.0 - Pipeline Orchestration + Job Control Framework
```

V14 should add:

- Config-driven job execution
- Pipeline step registry
- Step dependency control
- Retry logic
- Run modes
- CLI entry point
- Better production job control
