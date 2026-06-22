# V15.0.0 - Scheduling, Dependency Management, and Runtime Parameterization

## Purpose

V15 upgrades the V14 config-driven orchestrator with production-style runtime control.

V14 introduced job control and step execution. V15 adds the next orchestration capabilities:

- Runtime parameters
- Manual, scheduled, and backfill run modes
- Dry-run execution mode
- Step dependency metadata
- Dependency validation before execution
- Schedule metadata
- Runtime parameter snapshots

## New Files

```text
config/runtime/default_runtime_parameters.json
config/schedules/customer_medallion_schedule.json
scripts/runtime_parameters.py
tests/test_runtime_parameters.py
tests/test_v15_orchestrator_runtime.py
docs/v15_scheduling_dependency_runtime_parameters.md
```

## Updated Files

```text
config/jobs/customer_medallion_job.json
scripts/pipeline_orchestrator.py
README.md
```

## Runtime Parameters

Default runtime parameters are stored in:

```text
config/runtime/default_runtime_parameters.json
```

Supported fields:

```text
run_mode
run_date
dry_run
backfill_start_date
backfill_end_date
triggered_by
allow_optional_step_failure
```

Supported run modes:

```text
manual
scheduled
backfill
```

## Dependency Management

Each job step can now define dependencies:

```json
"depends_on": ["bronze_ingestion"]
```

Before a step runs, the orchestrator checks whether all configured dependencies completed successfully.

If a critical step has unmet dependencies, the job fails.

## Schedule Metadata

Schedule metadata is stored in:

```text
config/schedules/customer_medallion_schedule.json
```

This is metadata only. V15 does not create a background scheduler.

## Run Commands

Manual run:

```bash
python -m scripts.pipeline_orchestrator --run-mode manual --run-date 2026-06-23
```

Dry run:

```bash
python -m scripts.pipeline_orchestrator --run-mode manual --run-date 2026-06-23 --dry-run
```

Scheduled-mode simulation:

```bash
python -m scripts.pipeline_orchestrator --run-mode scheduled --run-date 2026-06-23 --triggered-by local_schedule_simulation
```

Backfill-mode simulation:

```bash
python -m scripts.pipeline_orchestrator --run-mode backfill --backfill-start-date 2026-06-16 --backfill-end-date 2026-06-17
```

## Runtime Parameter Snapshots

Each orchestrator run writes the resolved runtime parameters to:

```text
output/runtime_parameters/runtime_parameters_<job_run_id>.json
```

## Validation Commands

```bash
python -m py_compile scripts/runtime_parameters.py
python -m py_compile scripts/pipeline_orchestrator.py
python -m unittest tests.test_runtime_parameters
python -m unittest tests.test_v15_orchestrator_runtime
python -m unittest discover tests
python -m scripts.pipeline_orchestrator --run-mode manual --run-date 2026-06-23 --dry-run
python -m scripts.pipeline_orchestrator --run-mode manual --run-date 2026-06-23
```

## Interview Explanation

In V15, the orchestration framework was upgraded from fixed job execution to runtime-controlled execution.

The pipeline can now accept runtime parameters, validate run modes, support dry runs, simulate scheduled and backfill execution, and enforce step dependencies before each stage executes.

This is closer to production orchestration tools like Databricks Workflows, Azure Data Factory, and Airflow, where jobs are parameterized, dependency-aware, and controlled by schedule or runtime context.
