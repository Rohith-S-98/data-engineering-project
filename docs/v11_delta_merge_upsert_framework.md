# V11.0.0 - Delta MERGE / Upsert Framework

## Objective

V11 upgrades the Lakehouse write pattern from simple overwrite writes to configurable Delta MERGE upserts.

## What changed

- Added `lakehouse_write_strategy` to centralized pipeline config.
- Added layer-specific merge keys.
- Added reusable Delta MERGE helper in `lakehouse_io.py`.
- Bronze, Silver, Quarantine, and Gold Delta tables now support MERGE-based upserts.
- Added merge condition builder.
- Added unit tests for Lakehouse write strategy and merge condition generation.
- Improved watermark safety by skipping watermark staging when no incremental records exist.

## Config keys

```json
"lakehouse_write_strategy": "merge",
"bronze_merge_keys": ["customer_id"],
"silver_merge_keys": ["customer_id"],
"quarantine_merge_keys": ["customer_id"],
"gold_merge_keys": ["source_system", "source_id"]