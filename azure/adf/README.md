# Azure Data Factory Orchestration Simulation

This folder contains Azure Data Factory style metadata for V24.

The artifacts are intentionally local and portfolio-safe. They show how ADF would orchestrate Databricks notebooks for the customer medallion pipeline without requiring a real Azure subscription or Databricks workspace.

## Artifacts

```text
azure/adf/pipelines/customer_medallion_adf_pipeline.json
azure/adf/linked_services/ls_databricks_customer_pipeline.json
azure/adf/datasets/customer_landing_metadata.json
```

## Pipeline Flow

```text
Validate_Runtime_Parameters
Run_API_Ingestion + Run_Database_Ingestion
Run_Advanced_DQ_Catalog
Run_Medallion_Orchestrator
Validate_Runtime_Cleanliness
```

## Validation

```bash
python -m scripts.validate_adf_artifacts
```
