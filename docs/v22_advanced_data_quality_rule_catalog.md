# V22.0.0 - Advanced Data Quality Rule Catalog

V22 adds an advanced data quality rule catalog to the data engineering project.

## Goal

The goal is to move beyond hard-coded DQ checks and demonstrate a reusable, metadata-driven rule catalog that can evaluate different rule types, severities, and output a structured DQ summary.

## V22 Additions

- Advanced DQ rule catalog at `config/rules/advanced_customer_dq_rule_catalog.json`
- Clean sample input fixture at `tests/fixtures/customer_data_dq_catalog_sample.csv`
- Rule catalog evaluator at `scripts/advanced_dq_rule_catalog.py`
- V22 unit tests at `tests/test_v22_advanced_dq_rule_catalog.py`
- Config validation now includes the advanced DQ catalog
- Release verification now includes targeted V22 tests

## Supported Rule Types

```text
not_null
regex
allowed_values
unique
min_length
```

## Supported Severities

```text
critical
warning
```

Critical failures produce a final status of `FAILED`. Warning-only failures produce `SUCCESS_WITH_WARNINGS`. If no failures are found, the final status is `SUCCESS`.

## Data Flow

```text
Customer CSV fixture/input
↓
Advanced DQ rule catalog JSON
↓
Rule evaluator
↓
Per-rule results
↓
DQ summary JSON runtime output
```

## Run Advanced DQ Catalog

```bash
python -m scripts.advanced_dq_rule_catalog
```

Expected output for the committed clean fixture:

```text
Advanced DQ rule catalog evaluation SUCCESS
Catalog name     : advanced_customer_dq_rule_catalog
Dataset name     : customers
Total records    : 3
Rules evaluated  : 7
Critical failures: 0
Warning failures : 0
Final status     : SUCCESS
Summary file     : output/dq_reports/advanced_dq_catalog_summary.json
```

## Validate V22

```bash
python -m scripts.validate_config_files
python -m unittest tests.test_v22_advanced_dq_rule_catalog
python -m scripts.advanced_dq_rule_catalog
python -m scripts.validate_runtime_cleanliness
```

## Production Explanation

In production, data quality rules are often maintained as metadata rather than hard-coded logic. A central rule catalog makes it easier to add, disable, audit, and reuse validation checks across pipelines and datasets.

V22 models that pattern by using JSON-based rule metadata and a reusable evaluator that supports required checks, regex format validation, allowed values, uniqueness, and minimum length rules.

Static sample input belongs under `tests/fixtures/`; runtime landing data belongs under `data/raw/` and should not be committed.

## Interview Explanation

I added an advanced data quality rule catalog to my data engineering project. It uses metadata-driven JSON rules, supports multiple rule types and severity levels, evaluates rules against customer landing data, produces a structured DQ summary, and includes tests for clean data, critical failures, warning-only failures, uniqueness, missing input, and invalid catalog configuration.
