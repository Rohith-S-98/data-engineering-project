# V10.0.0 - Delta Lake / Lakehouse Storage Upgrade

## Objective

V10 upgrades the local medallion pipeline storage layer from Parquet-only paths to configurable Lakehouse storage using Delta Lake.

## What changed

- Added `storage_format` to centralized pipeline config.
- Added Delta Lake dependency through `delta-spark`.
- Upgraded local SparkSession to support Delta Lake.
- Added reusable Lakehouse IO helper.
- Replaced direct `.parquet()` reads/writes with format-driven reads/writes.
- Bronze, Silver, Gold, and Quarantine outputs now support Delta format.
- Reltio-style payload output remains JSON because it represents downstream API payload output.
- Added validation to confirm Delta transaction logs exist after writes.

## Storage format

Configured in:

```json
"storage_format": "delta"