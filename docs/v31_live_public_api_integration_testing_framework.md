# V31.0.0 - Live Public API Integration Testing Framework

V31 adds the final-phase public API integration framework to the Data Engineering roadmap.

## Goal

The goal is to show how the project can support real external API-style integration while keeping CI/CD safe and repeatable.

V31 uses two execution modes:

```text
mock mode     -> default, CI-safe, repeatable
manual mode   -> optional, local-only, requires --allow-live and endpoint variables
```

## Added Files

```text
config/api/live_public_api_sources.json
configs/schema_contracts/live_public_api_schema.json
data/api/mock_live_countries_response.json
data/api/mock_live_users_response.json
scripts/live_public_api_integration.py
scripts/validate_public_api_registry.py
tests/test_v31_public_api_integration.py
.github/workflows/v31-public-api-integration-ci.yml
```

## Why CI Uses Mock Mode

Automated CI should not fail because an external public API is slow, unavailable, rate limited, changed, or blocked.

For that reason:

```text
CI validates registry metadata
CI runs mocked API integration
CI runs V31 unit tests
manual live calls require explicit opt-in
```

## Manual Live Execution

Live execution is intentionally disabled by default.

To enable manual live execution locally:

```text
1. Copy .env.example to .env.
2. Set PUBLIC_COUNTRIES_API_URL and PUBLIC_TEST_USERS_API_URL locally.
3. Change the selected source live_enabled value to true in a local branch or local experiment.
4. Run python -m scripts.live_public_api_integration --allow-live.
```

Do not commit real endpoint secrets or credentials. The current V31 sources use public, no-auth style endpoint references only.

## Architecture

```text
Public API Registry
↓
Mock or Manual Live Fetch
↓
Raw JSON Landing
↓
Required Field Validation
↓
Normalized CSV Output
↓
Audit-style Summary
↓
CI and Release Verification Gates
```

## Validation

Run:

```bash
python -m scripts.validate_public_api_registry
python -m scripts.live_public_api_integration
python -m unittest tests.test_v31_public_api_integration
```

## Interview Explanation

I added a public API integration framework as the final phase of my Data Engineering roadmap. The framework reads public API source metadata from a registry, validates the configuration, uses mock responses for CI-safe automated testing, supports optional manual live execution, lands raw JSON, validates required fields, normalizes selected fields to CSV, and integrates the checks into CI and release verification.

## Apexon / IQVIA Mapping

In a real IQVIA-style pipeline, source APIs may be slow, unavailable, changed, or inconsistent. V31 demonstrates how I would separate repeatable mocked CI tests from manual integration checks, while still validating source metadata, response shape, landing behavior, and normalized downstream records.
