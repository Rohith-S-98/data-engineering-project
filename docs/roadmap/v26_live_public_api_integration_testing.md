# V26.0.0 - Live Public API Integration Testing Framework

## Purpose

V26.0.0 adds a realistic live-public-API integration testing phase to the Data Engineering roadmap. This phase is designed to connect the existing API ingestion framework with selected external APIs so the pipeline can be tested against real HTTP responses, unstable upstream behavior, schema drift, latency, empty payloads, and failed API calls.

This phase should be treated as a controlled integration layer, not as a replacement for the existing mock API framework. Mocked responses remain mandatory for repeatable CI/CD tests, while live API calls are used for local practice, manual integration validation, and portfolio demonstrations.

## Why This Phase Matters

Most real Data Engineering projects do not receive perfectly clean files every time. They often depend on source APIs that may be slow, unavailable, inconsistent, rate limited, or changed without notice. V26 introduces those realities into the roadmap in a safe and structured way.

This phase supports the broader 12-month goal of becoming stronger in:

- API ingestion design
- Source system integration
- JSON response handling
- Schema validation
- Data quality checks
- Quarantine handling
- Retry and failure recovery
- Audit and observability
- CI/CD-safe testing
- Production-style explanation for interviews

## Supporting Repository

The existing `Rohith-S-98/Public-API` repository will be reused as a supporting source registry and practice repository.

Its purpose in V26 will be:

- Identify candidate public APIs for integration testing.
- Maintain notes on selected endpoints.
- Avoid relying on the old copied README list as a portfolio artifact.
- Support the main `data-engineering-project` as an external live-data reference.

The main implementation work should remain inside `Rohith-S-98/data-engineering-project`.

## Planned Scope

V26 should include the following implementation scope:

1. Create a configurable public API source registry.
2. Add endpoint metadata such as API name, URL, HTTP method, timeout, expected status code, response type, and enabled flag.
3. Build a reusable live API client.
4. Add timeout handling and structured API exceptions.
5. Add retry behavior for transient failures.
6. Store raw JSON responses in a raw landing area.
7. Validate API response schema contracts.
8. Separate valid responses from invalid responses.
9. Route failed, malformed, empty, or schema-invalid payloads to quarantine.
10. Normalize selected API responses into tabular Bronze/Silver-ready records.
11. Capture audit metrics such as endpoint name, status code, latency, response size, record count, and failure reason.
12. Add mocked unit tests so CI/CD does not depend on live internet calls.
13. Add optional manual live integration test commands for local/demo use.
14. Document how this maps to real Apexon/IQVIA-style API ingestion work.

## Planned Architecture

```text
Selected Live Public APIs
↓
Public API Source Registry
↓
Live API Client
↓
Timeout + Retry + Structured Exception Handling
↓
Raw JSON Landing
↓
Schema Contract Validation
↓
Valid Response Path / Quarantine Path
↓
Bronze + Silver Normalization
↓
Audit + Observability Metrics
↓
Existing Orchestration, Alerting, Retry, CI/CD, and Dashboard Layers
```

## Planned Repository Additions

Expected files and folders:

```text
config/api/live_public_api_sources.json
configs/schema_contracts/live_public_api_schema.json
scripts/live_public_api_ingestion.py
scripts/validate_live_public_api_sources.py
src/ingestion/live_api_client.py
src/ingestion/live_api_registry.py
src/validation/live_api_response_validator.py
src/transformations/live_api_normalizer.py
tests/test_live_api_client.py
tests/test_live_api_response_validator.py
tests/test_v26_live_public_api_integration.py
docs/roadmap/v26_live_public_api_integration_testing.md
```

## Candidate API Types

The selected APIs should be stable, simple, and safe for repeatable demonstrations. Good candidates include:

- Public country/reference APIs
- Currency/reference-rate APIs with no authentication, if stable
- Weather/demo APIs only if rate limits and response variability are controlled
- Public test APIs designed for integration practice
- Lightweight facts/reference APIs for JSON shape validation

Avoid APIs that require paid keys, expose sensitive data, are unreliable, or have unclear usage limits.

## CI/CD Rule

CI/CD should not depend on live internet availability.

Required approach:

- Unit tests must use mocked API responses.
- Live API calls should be optional and manually triggered.
- CI should validate configuration, schema contracts, client behavior, error handling, and normalization logic using fixtures.
- A failed external API should not break the regular release pipeline unless the live test is intentionally enabled.

## Interview Story

This phase can be explained in interviews as:

> I extended my Data Engineering pipeline to support live public API integration testing. The framework reads endpoint metadata from config, calls APIs using a reusable client, handles timeout and retry scenarios, lands raw JSON, validates schema contracts, routes invalid responses to quarantine, normalizes valid data into pipeline-ready records, and captures audit/observability metrics. For CI/CD safety, all automated tests use mocked responses, while live API calls are kept as manual integration checks.

## Completion Criteria

V26 should be considered complete only when:

- Source registry exists and validates successfully.
- At least two selected APIs are integrated in controlled mode.
- Raw response landing works.
- Schema validation works.
- Quarantine handling works for invalid responses.
- Normalization produces tabular records.
- Audit metrics capture API status, latency, and failure details.
- Unit tests pass without live internet calls.
- Manual live integration command is documented.
- README is updated from planned V26 to completed V26.
- Release verification passes before tagging `v26.0.0`.
