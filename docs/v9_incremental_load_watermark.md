# V9.0.0 - Incremental Load and Watermark Framework

## Objective

V9 introduces incremental processing using a committed watermark and pending watermark staging.

## Flow

```text
Raw input
    ↓
Read last committed watermark
    ↓
Filter records where created_date > last_watermark
    ↓
Write incremental data to Bronze
    ↓
Stage pending watermark
    ↓
Run Silver DQ
    ↓
Run Gold Canonical
    ↓
Commit watermark only after full pipeline success
```

## Key Files

```text
scripts/watermark_manager.py
tests/test_watermark_manager.py
data/audit/watermark_store.json
data/audit/pending_watermark_updates.json
```

## Why Pending Watermark Is Needed

The watermark must not be committed immediately after Bronze. If Bronze succeeds but Silver DQ or Gold fails, committing early would cause failed records to be skipped in the next run.
