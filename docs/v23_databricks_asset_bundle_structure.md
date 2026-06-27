# V23.0.0 - Databricks Asset Bundle Style Deployment Structure

V23 adds a Databricks Asset Bundle-style deployment structure to the data engineering project.

## Goal

The goal is to demonstrate how a production data engineering project can be organized for Databricks deployment using bundle-style metadata, environment targets, job resources, and deployment validation.

This version keeps all workspace URLs as placeholders so the project remains safe, local, and CI-friendly.

## V23 Additions

- Root bundle metadata in `databricks.yml`
- Job resource definition in `resources/customer_medallion_job.yml`
- Databricks deployment notes in `deployment/databricks/README.md`
- Local Databricks bundle structure validator in `scripts/validate_databricks_bundle_structure.py`
- V23 unit tests in `tests/test_v23_databricks_bundle_structure.py`
- V23 validation integrated into release verification

## Deployment Structure

```text
databricks.yml
resources/
└── customer_medallion_job.yml
deployment/
└── databricks/
    └── README.md
```

## Bundle Targets

```text
dev
prod
```

The `dev` target represents a development workspace deployment. The `prod` target represents a production workspace deployment.

## Local Validation

```bash
python -m scripts.validate_databricks_bundle_structure
```

Expected output:

```text
Databricks bundle structure validation SUCCESS
Validated files: 3
```

## Production Deployment Pattern

In a real Databricks environment, the deployment flow would look like:

```bash
databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle run customer_medallion_pipeline_job -t dev
```

For this project, the structure is validated locally without requiring a Databricks workspace.

## Interview Explanation

I added a Databricks Asset Bundle-style deployment structure to my data engineering project. It includes a root `databricks.yml`, separate job resource metadata, dev and prod targets, placeholder workspace paths, a customer medallion pipeline job definition, a local bundle structure validator, and tests to ensure deployment files and required deployment tokens are present.
