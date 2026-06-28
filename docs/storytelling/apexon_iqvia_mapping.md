# Apexon / IQVIA Mapping

This document maps the portfolio project to real-world Apexon / IQVIA-style Data Engineering work.

## Real-Work Context

In an IQVIA MDM-style environment, data can arrive from systems such as OneKey, Veeva, file feeds, API connectors, or database extracts. The engineering flow usually includes landing, validation, quarantine, business-rule transformation, canonical modeling, downstream JSON payload generation, monitoring, and error triage.

## Portfolio Mapping

| Real Work Pattern | Project Implementation |
|---|---|
| Source ingestion from API, files, connectors, or databases | Config-driven API and database ingestion frameworks with raw landing |
| Landing to staging transformation | Bronze and Silver medallion layers |
| Data quality checks | Metadata-driven DQ rule catalog and severity-based control |
| Failed records | Quarantine path for invalid or rejected records |
| Incremental processing | Watermark framework and pending watermark staging |
| Golden or canonical output | Gold canonical customer model |
| Downstream MDM payload | Reltio-style JSON payload generation |
| Historical tracking | SCD Type 2 customer history layer |
| Operational monitoring | Audit logs, observability metrics, alerting, SLA monitoring |
| Recovery from failures | Retry, recovery, and failure replay framework |
| Release discipline | CI/CD, release verification, Docker, and repository hygiene checks |
| Cloud deployment style | Databricks Asset Bundle-style metadata and ADF-style orchestration metadata |
| Secure environment handling | Secret-safe dev/test/prod configuration references |
| System validation | Manifest-driven E2E integration gates |
| Table performance planning | Partition strategy, clustering columns, target file-size metadata, and retention windows |

## Interview Framing

I can explain this project using a real IQVIA-style flow:

```text
Source systems send customer or reference data.
The pipeline lands raw data, validates schema and DQ rules, separates failed records into quarantine, transforms valid records into clean and canonical layers, tracks history, builds downstream JSON payloads, and monitors every run using audit and observability outputs.
```

## Strong Answer For Interview

My current work and my portfolio connect around the same engineering pattern: reliable ingestion, data quality, quarantine, canonical modeling, downstream MDM integration, and operational controls. In the project, I recreated those patterns locally and added release gates, CI/CD, Databricks-style deployment metadata, ADF-style orchestration metadata, E2E validation, and partition strategy so I can explain both implementation and production-readiness.
