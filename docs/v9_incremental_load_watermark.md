# V9.0.0 - Incremental Load and Watermark Framework

## Objective

V9 introduces incremental data processing using a configurable watermark framework.

The pipeline reads only new records based on the `created_date` watermark column.

## Key Features

- Watermark store
- Pending watermark staging
- Incremental dataframe filtering
- Max watermark calculation
- Watermark commit only after full pipeline success
- Protection against data loss when DQ or Gold fails

## New Files

```text
scripts/watermark_manager.py
tests/test_watermark_manager.py
docs/v9_incremental_load_watermark.md
data/audit/watermark_store.json
data/audit/pending_watermark_updates.json

# V9.0.0 - Incremental Load and Watermark Framework

## Objective

V9 introduces incremental data processing using a configurable watermark framework.

The pipeline reads only new records based on the `created_date` watermark column.

## Key Features

- Watermark store
- Pending watermark staging
- Incremental dataframe filtering
- Max watermark calculation
- Watermark commit only after full pipeline success
- Protection against data loss when DQ or Gold fails

## New Files

```text
scripts/watermark_manager.py
tests/test_watermark_manager.py
docs/v9_incremental_load_watermark.md
data/audit/watermark_store.json
data/audit/pending_watermark_updates.json