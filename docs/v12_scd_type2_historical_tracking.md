# V12.0.0 - SCD Type 2 / Historical Dimension Tracking

## Goal

V12 adds historical customer attribute tracking on top of the existing Delta Lake and Delta MERGE foundation.

Before V12, the pipeline maintained only the latest current customer state in Bronze, Silver, and Gold Delta tables.

After V12, the pipeline also maintains a Customer History SCD Type 2 Delta table.

## New Table

```text
data/gold/customer_history
```

## Tracked Business Key

```text
customer_id
```

## Tracked Columns

```text
first_name
last_name
email
phone
city
state
source_system
```

## SCD2 Metadata Columns

```text
effective_start_date
effective_end_date
is_current
record_hash
created_at
updated_at
```

## Behavior

### Initial Load

All valid Silver records are inserted into the history table with:

```text
is_current = true
effective_end_date = null
```

### New Customer

A new business key is inserted as a new current history record.

### Changed Customer

When a tracked attribute changes:

1. Existing current record is expired.
2. `effective_end_date` is populated.
3. `is_current` becomes false.
4. A new current version is inserted.

### Unchanged Customer

No new history row is inserted.

## Pipeline Placement

```text
Bronze
↓
Silver + Quarantine
↓
Customer History SCD2
↓
Gold Canonical
↓
Reltio JSON
```

## Why this matters

This simulates real enterprise MDM and warehouse behavior where downstream consumers need both:

- latest customer state
- historical customer changes over time

## Validation

Run initial load:

```bash
python -m scripts.create_sample_data
python -m scripts.pyspark_pipeline_runner
```

Then change a tracked customer field and run again:

```bash
python -m scripts.pyspark_pipeline_runner
```

Expected result:

- old record becomes `is_current = false`
- old record gets `effective_end_date`
- new version becomes `is_current = true`
- `record_hash` changes
