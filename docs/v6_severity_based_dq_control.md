# V6.0.0 - Severity-Based DQ Failure Control

## Objective

V6 adds severity-based decisioning to determine whether the pipeline should continue or stop after data quality validation.

## Severity Behavior

| Severity | Behavior |
|---|---|
| HIGH | Stops the pipeline if failed |
| MEDIUM | Allows continuation with warning |
| LOW | Allows continuation with warning |

## Status Values

- `SUCCESS`
- `SUCCESS_WITH_WARNINGS`
- `FAILED`

## Key File

```text
scripts/dq_decision.py
```

## Why This Matters

Not all DQ failures should stop a pipeline. HIGH severity issues protect downstream consumers from critical data problems, while lower-severity issues can be reported without blocking the full flow.
