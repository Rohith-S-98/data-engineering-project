# Architecture

## Current V1-V9 Architecture

```text
Raw Customer CSV
        ↓
Bronze Schema Validation
        ↓
Incremental Watermark Filter
        ↓
Bronze Parquet
        ↓
Silver DQ Validation
        ↓
Silver Schema Validation
        ↓
Severity-Based DQ Decision
        ↓
Gold Canonical Transformation
        ↓
Reltio-Style JSON Payload
        ↓
Commit Watermark After Success
        ↓
Pipeline Audit Update
```

## Main Layers

### Bronze

Raw customer data is read from CSV and written as Parquet after schema validation and incremental filtering.

### Silver

Data quality rules are applied. Valid records are written to Silver and failed records are written to quarantine.

### Gold

Silver valid records are transformed into a canonical customer structure and exported as a Reltio-style JSON payload.

## Control Frameworks

### Schema Validation

Schema contracts are stored in:

```text
configs/schema_contracts/
```

Schema audit output is stored in:

```text
data/audit/schema_validation_audit.jsonl
```

### Watermark Management

Committed watermark file:

```text
data/audit/watermark_store.json
```

Pending watermark file:

```text
data/audit/pending_watermark_updates.json
```

### Pipeline Audit

Pipeline run audit file:

```text
output/audit/pipeline_runs.csv
```
