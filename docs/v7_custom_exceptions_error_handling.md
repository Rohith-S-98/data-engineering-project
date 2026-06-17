# V7.0.0 - Custom Exceptions and Structured Error Handling

## Objective

V7 introduces custom exception classes and cleaner pipeline error handling.

## Exception Classes

```text
PipelineError
PipelineConfigError
DataIngestionError
DQValidationError
PipelineExecutionError
```

## Key Files

```text
scripts/exceptions.py
scripts/pyspark_pipeline_runner.py
```

## Why This Matters

Production pipelines should fail clearly, consistently, and with meaningful error messages. Custom exceptions make failures easier to identify and debug.
