# V20.0.0 - API Ingestion Framework

V20 adds a local API ingestion framework to the data engineering project.

## Goal

The goal is to demonstrate how source API data can be extracted, normalized, and landed into the existing raw customer data shape before medallion processing.

This version intentionally uses a local mock API payload instead of making external internet calls. That keeps the project deterministic, testable, and CI-friendly.

## V20 Additions

- API ingestion config at `config/api/customer_api_ingestion_config.json`
- Mock paginated customer API response at `data/api/mock_customer_api_response.json`
- API ingestion runner at `scripts/api_ingestion.py`
- V20 unit tests at `tests/test_v20_api_ingestion.py`
- Config validation now includes the V20 API config
- Generated API raw output is ignored by Git and Docker build context

## Data Flow

```text
Mock Customer API JSON
↓
API ingestion config
↓
Field mapping and default enrichment
↓
Raw customer API CSV
↓
Existing Bronze/Silver/Gold medallion framework
```

## Run API Ingestion

```bash
python -m scripts.api_ingestion
```

Expected output:

```text
API ingestion SUCCESS
Source name    : customer_mock_api
Pages read     : 2
Records written: 3
Target CSV     : data/raw/customer_data_api.csv
```

## Validate V20

```bash
python -m scripts.validate_config_files
python -m unittest tests.test_v20_api_ingestion
python -m scripts.api_ingestion
python -m scripts.validate_runtime_cleanliness
```

## Production Explanation

In production, an API ingestion layer usually handles authentication, pagination, rate limits, retries, schema mapping, and landing raw source data before transformation. V20 models that pattern using deterministic local fixtures so the framework can be tested without network dependency.

## Interview Explanation

I added an API ingestion layer to my data engineering project. It uses a config-driven source definition, supports paginated API-style payloads, maps source API fields into my raw customer schema, writes a raw CSV landing file, and includes unit tests for config validation, pagination, missing source handling, and output generation.
