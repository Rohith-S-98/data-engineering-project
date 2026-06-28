# Two-Minute Project Overview

## Script

I built an end-to-end Data Engineering pipeline simulator to show how a production-style pipeline works beyond simple transformation scripts.

The project starts with API, file, and database-style ingestion. Data lands in raw storage, moves through Bronze and Silver processing, and is validated using schema contracts and metadata-driven data quality rules. Invalid records are routed to quarantine while valid records continue to the Gold canonical model.

The project also includes incremental watermarking, Delta-style merge and upsert logic, SCD Type 2 history tracking, audit logging, observability metrics, alerting, SLA monitoring, retry, recovery, and failure replay.

From a production-readiness perspective, I added GitHub Actions CI/CD gates, Docker runtime support, Databricks Asset Bundle-style deployment metadata, Azure Data Factory-style orchestration metadata, Power BI-ready observability outputs, secret-safe dev/test/prod environment configuration, E2E integration testing, and partitioning strategy.

This project maps closely to my Apexon and IQVIA-style work because it follows the same type of flow: source ingestion, validation, quarantine, staging or silver transformation, canonical modeling, downstream MDM-style JSON payload generation, monitoring, and release discipline.

## Key Message

This is not a one-time ETL script. It is a versioned production-style Data Engineering platform that shows implementation, testing, operations, deployment thinking, and interview-ready explanation.
