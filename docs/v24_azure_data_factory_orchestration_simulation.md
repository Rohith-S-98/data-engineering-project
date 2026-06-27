# V24.0.0 - Azure Data Factory Orchestration Simulation

V24 adds an Azure Data Factory style orchestration simulation for the customer medallion data engineering pipeline.

## Goal

The goal is to explain how Azure Data Factory can orchestrate a Databricks-based data platform without requiring a live Azure subscription in this portfolio project.

## Why This Matters

In real client work, ADF is commonly used to trigger and monitor ingestion, data quality, transformation, and validation jobs. This version connects the local project to an Azure-style orchestration story.

## Added Artifacts

```text
azure/adf/pipelines/customer_medallion_adf_pipeline.json
azure/adf/linked_services/ls_databricks_customer_pipeline.json
azure/adf/datasets/customer_landing_metadata.json
azure/adf/README.md
scripts/validate_adf_artifacts.py
tests/test_v24_adf_artifacts.py
```

## Simulated ADF Flow

```text
Validate_Runtime_Parameters
↓
Run_API_Ingestion + Run_Database_Ingestion
↓
Run_Advanced_DQ_Catalog
↓
Run_Medallion_Orchestrator
↓
Validate_Runtime_Cleanliness
```

## Validation Rules

The validator checks:

```text
required ADF artifact files exist
pipeline JSON is valid
pipeline parameters exist
ADF activities exist
activity names are unique
Databricks linked service reference is consistent
activity dependency chain is valid
linked service is placeholder-only and secret-free
landing metadata contains required customer columns
```

## Commands

```bash
python -m scripts.validate_adf_artifacts
python -m unittest tests.test_v24_adf_artifacts
```

## Apexon / IQVIA Explanation Practice

In an IQVIA-style MDM pipeline, Azure Data Factory can orchestrate source ingestion from systems like OneKey or Veeva, trigger Databricks notebooks for raw landing, run metadata-driven DQ checks, continue only after critical validations pass, run medallion transformations, and finally validate runtime cleanliness and audit status.

## Interview Explanation

I added an Azure Data Factory style orchestration simulation to my data engineering project. It includes ADF-like pipeline metadata, Databricks linked service metadata, raw landing metadata, a validator, and tests. The pipeline shows how ADF would coordinate ingestion, DQ, medallion orchestration, and final validation in a production-style Azure data engineering workflow.
