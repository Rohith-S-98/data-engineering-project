# V14.0.0 - Pipeline Orchestration + Job Control Framework

## Purpose

V14 converts the earlier fixed PySpark pipeline runner into a config-driven orchestration and job-control framework.

Before V14, the medallion pipeline execution order was hardcoded in `scripts/pyspark_pipeline_runner.py`.

V14 introduces production-style execution control where every pipeline stage is represented as a configurable job step.

## New Files

```text
config/jobs/customer_medallion_job.json
scripts/job_control.py
scripts/pipeline_orchestrator.py
tests/test_job_control.py
tests/test_pipeline_orchestrator.py
docs/v14_pipeline_orchestration_job_control.md
```

## Orchestrated Flow

```text
Bronze Ingestion
↓
Silver DQ Validation
↓
Customer History SCD Type 2
↓
Gold Canonical Transformation
↓
Commit Watermark
↓
Pipeline Observability
```

## Job Control Features

- Job-level configuration
- Step-level configuration
- Enabled/disabled step control
- Critical vs optional step handling
- Expected status validation
- Job run audit logging
- Step run audit logging
- Observability as an orchestrated step

## Runtime Outputs

```text
output/job_control/job_runs.csv
output/job_control/step_runs.csv
```

These files are runtime logs and should not be committed to Git.

## Run Command

```bash
python -m scripts.pipeline_orchestrator
```

## Validation Commands

```bash
python -m py_compile scripts/job_control.py
python -m py_compile scripts/pipeline_orchestrator.py
python -m unittest tests.test_job_control
python -m unittest tests.test_pipeline_orchestrator
python -m unittest discover tests
python -m scripts.pipeline_orchestrator
python -m scripts.pipeline_observability
```

## Verified Result

The V14 orchestrator should successfully execute all six configured steps:

```text
Final Status    : SUCCESS
Total Steps     : 6
Successful Steps: 6
Failed Steps    : 0
Skipped Steps   : 0
```

## Interview Explanation

In V14, the earlier hardcoded PySpark medallion pipeline was upgraded into a config-driven orchestration framework.

Each stage is represented as a job step with metadata such as step ID, step name, module, function, enabled flag, criticality, and expected statuses.

The framework records both job-level and step-level audit logs, supports optional step continuation, validates returned statuses, and integrates observability as part of the overall pipeline execution.

This is similar to how production pipelines are managed in Databricks Workflows, Azure Data Factory, or Airflow, where each task has execution control, logging, dependency order, and failure handling.
