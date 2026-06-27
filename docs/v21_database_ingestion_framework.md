# V21.0.0 - Database Ingestion Framework

V21 adds a local database ingestion framework to the data engineering project.

## Goal

The goal is to demonstrate how relational database data can be extracted through a configured SQL query, landed into the raw layer, and made available to the existing medallion processing framework.

This version uses SQLite from Python's standard library so the project remains deterministic, local, and CI-friendly without requiring an external database server.

## V21 Additions

- Database ingestion config at `config/database/customer_database_ingestion_config.json`
- SQLite source database seeding support
- Database ingestion runner at `scripts/database_ingestion.py`
- Raw database landing CSV at `data/raw/customer_data_db.csv`
- V21 unit tests at `tests/test_v21_database_ingestion.py`
- Database config validation in `scripts.validate_config_files`
- V21 targeted tests in release verification

## Data Flow

```text
Configured SQLite Source Database
↓
Seed source table for local reproducibility
↓
Configured SELECT extraction query
↓
Raw customer DB CSV
↓
Existing Bronze/Silver/Gold medallion framework
```

## Run Database Ingestion

```bash
python -m scripts.database_ingestion
```

Expected output:

```text
Database ingestion SUCCESS
Source name    : customer_sqlite_database
Database type  : sqlite
Source table   : source_customers
Records written: 3
Target CSV     : data/raw/customer_data_db.csv
```

## Validate V21

```bash
python -m scripts.validate_config_files
python -m unittest tests.test_v21_database_ingestion
python -m scripts.database_ingestion
python -m scripts.validate_runtime_cleanliness
```

## Production Explanation

In production, a database ingestion layer usually connects to SQL Server, PostgreSQL, Oracle, or another operational source system, runs a controlled extraction query, lands the result into raw storage, and then lets downstream medallion transformations handle validation and enrichment.

V21 models this same pattern using SQLite so the project can be run locally and tested in CI without external infrastructure.

## Interview Explanation

I added a database ingestion layer to my data engineering project. It uses a config-driven database source definition, supports a controlled SQL extraction query, seeds a local SQLite source for reproducibility, writes extracted records into a raw customer CSV landing file, and includes tests for config validation, missing database handling, invalid query protection, and output generation.
