# V13.0.0 - Data Observability + Pipeline Metrics Mart

## Objective

V13 adds a production-style observability layer on top of the existing
data engineering pipeline.

The goal of this version is to summarize pipeline health, row counts,
data quality results, schema validation status, watermark movement,
SCD Type 2 activity, and audit metrics into reusable metrics outputs.

This version does not replace the existing V12 pipeline. Instead, it
adds an observability layer that reads the outputs produced by the
pipeline and generates a metrics mart.

---

## Why Data Observability Matters

A production data pipeline is not complete if it only moves and transforms
data.

A reliable production pipeline should also answer:

- Did the pipeline run successfully?
- How many records entered Bronze?
- How many valid records reached Silver?
- How many records were quarantined?
- How many records reached Gold?
- Did schema validation pass?
- Did data quality validation pass?
- Did the watermark move correctly?
- How many SCD2 records are current?
- How many SCD2 records are expired?
- How many customers changed?
- Where can pipeline health be checked without opening every output folder?

V13 solves this by creating centralized observability outputs.

---

## Current Pipeline Flow After V13

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

### V13 Observability Files

```text
scripts/metrics_collector.py
scripts/pipeline_observability.py
tests/test_metrics_collector.py
docs/v13_data_observability_metrics.md
output/observability/.gitkeep