# V28.0.0 - Performance Optimization and Partitioning Strategy

V28 adds a metadata-driven partitioning and table maintenance strategy for the customer medallion pipeline.

## Goal

The goal is to show lakehouse performance thinking without adding unsafe or unnecessary live infrastructure dependencies.

This version documents and validates:

```text
partition columns
clustering columns
target file sizes
retention windows
table maintenance actions
layer-specific strategy choices
```

## Added Files

```text
config/partitioning/customer_partition_strategy.json
scripts/validate_partition_strategy.py
tests/test_v28_partition_strategy.py
docs/v28_performance_optimization_partitioning_strategy.md
```

## Strategy Coverage

The partition strategy covers:

```text
bronze_customers
silver_customers
customer_history
gold_customer_canonical
pipeline_observability_metrics
```

## Why These Tables Matter

| Dataset | Reason |
|---|---|
| bronze_customers | Raw landing growth and ingestion-date pruning |
| silver_customers | Cleaned customer queries and data-quality analysis |
| customer_history | SCD Type 2 history growth and current/expired record access |
| gold_customer_canonical | Downstream canonical consumption |
| pipeline_observability_metrics | Dashboard-ready monitoring and refresh efficiency |

## Validation

Run:

```bash
python -m scripts.validate_partition_strategy
python -m unittest tests.test_v28_partition_strategy
```

The validator checks:

```text
required table strategies exist
required strategy keys are present
partition columns are non-empty and controlled
clustering columns are non-empty
target file sizes stay within accepted bounds
retention days are valid
customer_history partitions by effective_year
observability target files stay small enough for dashboard refresh
```

## Interview Explanation

I added a partitioning and table maintenance strategy to my data engineering project. The strategy defines how each major medallion layer table should be partitioned, clustered, retained, and monitored for file-size health. I also added a validator and tests so invalid table strategies, missing datasets, oversized/small target files, and incorrect SCD2 history partitioning are caught before release.

## Apexon / IQVIA Mapping

In an IQVIA-style Databricks project, large customer, HCP, HCO, activity, and history tables need thoughtful partitioning and clustering. Poor partitioning can cause expensive scans, slow jobs, and hard-to-debug pipeline delays. V28 demonstrates how a data engineer documents and validates table layout decisions before production deployment.

## Public API Backlog Note

Live public API integration testing is not part of V28. It is intentionally deferred to V31 as a final-phase enhancement after the core capstone release work.
