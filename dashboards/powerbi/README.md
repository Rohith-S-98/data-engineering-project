# Power BI Observability Dashboard

V25 adds a Power BI-ready observability layer on top of the existing pipeline metrics mart.

## Purpose

The dashboard artifacts convert nested observability metrics into clean CSV files that can be imported into Power BI.

## Export Command

Run the V13 observability collector first:

```bash
python -m scripts.pipeline_observability
```

Then export Power BI-ready files:

```bash
python -m scripts.powerbi_observability_exporter
```

## Generated Files

```text
output/observability/powerbi/dashboard_kpi_snapshot.csv
output/observability/powerbi/dashboard_data_quality_snapshot.csv
output/observability/powerbi/dashboard_layer_row_counts.csv
```

## Recommended Dashboard Pages

```text
1. Executive Pipeline Health
2. Data Quality and Quarantine
3. Layer Row Counts
4. Watermark and Incremental Load Status
5. SCD2 History Health
```

## Validation

```bash
python -m scripts.validate_powerbi_dashboard_artifacts
python -m unittest tests.test_v25_powerbi_observability_dashboard
```
