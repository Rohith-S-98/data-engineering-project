# V5.0.0 - Pipeline Audit Tracking

## Objective

V5 adds run-level audit tracking for the PySpark medallion pipeline.

## Features

- Unique pipeline run ID
- Pipeline start and end timestamps
- Environment tracking
- SUCCESS / FAILED status tracking
- Error message capture
- CSV-based audit log for local execution

## Audit Output

```text
output/audit/pipeline_runs.csv
```

## Key File

```text
scripts/run_metadata.py
```

## Why This Matters

In production data engineering, every pipeline run must be traceable. Audit tracking helps support monitoring, debugging, SLA reporting, and incident review.
