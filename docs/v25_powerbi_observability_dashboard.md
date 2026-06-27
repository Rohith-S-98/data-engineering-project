# V25.0.0 - Observability Dashboard / Power BI-Ready Metrics

V25 adds a Power BI-ready observability layer to the data engineering project.

## Goal

The goal is to convert existing pipeline observability outputs into clean dashboard-ready CSV files that can be loaded into Power BI.

## Why This Matters

A production data engineering pipeline should not only run successfully. It should also be explainable through metrics, trends, statuses, and operational KPIs. V25 connects engineering outputs to business-facing dashboard consumption.

## Added Files

```text
scripts/powerbi_observability_exporter.py
scripts/validate_powerbi_dashboard_artifacts.py
dashboards/powerbi/observability_dashboard_schema.json
dashboards/powerbi/README.md
tests/test_v25_powerbi_observability_dashboard.py
docs/v25_powerbi_observability_dashboard.md
```

## Export Flow

```text
V13 pipeline metrics summary JSON
↓
V25 Power BI exporter
↓
dashboard_kpi_snapshot.csv
dashboard_data_quality_snapshot.csv
dashboard_layer_row_counts.csv
↓
Power BI dashboard import
```

## Dashboard Outputs

```text
output/observability/powerbi/dashboard_kpi_snapshot.csv
output/observability/powerbi/dashboard_data_quality_snapshot.csv
output/observability/powerbi/dashboard_layer_row_counts.csv
```

## Metrics Included

```text
pipeline status
schema validation status
DQ status
bronze row count
silver row count
quarantine row count
gold row count
customer history row count
quarantine rate percent
DQ failure rate percent
DQ pass rate percent
current watermark
pending watermark
SCD2 current rows
SCD2 expired rows
changed customer count
```

## Commands

Run pipeline observability first:

```bash
python -m scripts.pipeline_observability
```

Export dashboard-ready CSV files:

```bash
python -m scripts.powerbi_observability_exporter
```

Validate V25 artifacts:

```bash
python -m scripts.validate_powerbi_dashboard_artifacts
python -m unittest tests.test_v25_powerbi_observability_dashboard
```

## Power BI Story

The dashboard can be explained as an operational monitoring layer for a medallion pipeline. It gives stakeholders visibility into pipeline health, row count movement across Bronze/Silver/Gold, DQ performance, quarantine impact, watermark status, and SCD2 history health.

## Apexon / IQVIA Explanation Practice

In an IQVIA-style MDM pipeline, dashboard-ready observability helps explain whether OneKey/Veeva ingestion completed, whether DQ passed, how many records were quarantined, whether canonical/gold outputs were produced, and whether incremental processing advanced correctly through watermarks.

## Interview Explanation

I added a Power BI-ready observability dashboard layer to my data engineering project. The existing pipeline already produced observability metrics, and V25 converts those nested metrics into dashboard-friendly CSV datasets. I added KPI, DQ, and layer row-count exports, a dashboard schema contract, validation checks, tests, and documentation. This shows how data engineers can make pipeline health visible to both engineering and business stakeholders.
