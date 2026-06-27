# Databricks Deployment Structure

This folder documents the Databricks Asset Bundle-style deployment layout used by V23.

The project keeps the deployment metadata local and deterministic so it can be reviewed and validated without requiring a real Databricks workspace.

## Files

```text
databricks.yml
resources/customer_medallion_job.yml
deployment/databricks/README.md
```

## Intended Deployment Flow

```bash
databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle run customer_medallion_pipeline_job -t dev
```

For this portfolio project, local validation is handled by:

```bash
python -m scripts.validate_databricks_bundle_structure
```

## Targets

```text
dev  - development deployment target
prod - production deployment target
```

The workspace hosts in `databricks.yml` are placeholders and should be replaced with real workspace URLs in an actual deployment.
