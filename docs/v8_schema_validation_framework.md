# V8.0.0 - Schema Validation Framework

## Objective

V8 introduces a reusable schema validation framework to validate DataFrame structure before data moves across pipeline layers.

## Features

- JSON-based schema contracts
- Required column validation
- Unexpected column validation
- Data type validation
- Nullability validation
- Schema validation audit logging
- Structured schema validation exception

## Main Files

```text
configs/schema_contracts/bronze_customers_schema.json
configs/schema_contracts/silver_customers_schema.json
scripts/schema_validation_framework.py
tests/test_schema_validation_framework.py
```

## Audit Output

```text
data/audit/schema_validation_audit.jsonl
```

## Pipeline Placement

- Bronze schema validation runs after raw CSV read.
- Silver schema validation runs after DQ filtering and before Silver write.
