# V31.0.0 - Live Public API Integration Testing Framework

## Status

V31 is now the final-phase implementation item for the Data Engineering roadmap.

It was originally drafted as a V26 roadmap note, but the implemented V26 release became Secrets, Environments, and Deployment Configuration. The public API integration testing work was intentionally deferred and is now implemented as V31.

## Purpose

V31 adds a controlled public API integration testing phase to the project. The framework connects source metadata, mocked API fixtures, optional manual endpoint execution, raw JSON landing, required-field validation, normalization, tests, CI, and release verification.

The implementation is intentionally CI-safe:

```text
mocked responses are used for automated CI/CD
manual endpoint execution requires explicit --allow-live opt-in
endpoint values are supplied locally through environment variables
```

## Implemented Files

```text
config/api/live_public_api_sources.json
configs/schema_contracts/live_public_api_schema.json
data/api/mock_live_countries_response.json
data/api/mock_live_users_response.json
scripts/live_public_api_integration.py
scripts/validate_public_api_registry.py
tests/test_v31_public_api_integration.py
.github/workflows/v31-public-api-integration-ci.yml
docs/v31_live_public_api_integration_testing_framework.md
docs/project_about.md
```

## Implemented Architecture

```text
Public API Source Registry
↓
Mock Fixture or Manual Endpoint Fetch
↓
Raw JSON Landing
↓
Required Field Validation
↓
Normalized CSV Output
↓
CI and Release Verification Gates
```

## CI/CD Rule

CI/CD must not depend on external internet availability.

V31 follows this rule by:

```text
validating registry metadata
using mock response files for automated runs
testing required-field validation
blocking unsafe endpoint references
allowing manual live mode only through explicit opt-in
```

## Manual Execution Note

Manual endpoint execution is optional. To run it locally, set the endpoint values in `.env`, enable the selected source locally, and pass:

```bash
python -m scripts.live_public_api_integration --allow-live
```

Do not commit real secrets or private endpoints.

## Interview Story

```text
I extended my Data Engineering project with a public API integration testing framework. It reads API source metadata from config, validates that the registry is CI-safe, uses mock fixtures for repeatable automated tests, optionally supports manual endpoint execution, lands raw JSON, validates required fields, normalizes selected fields into CSV output, and includes CI plus release verification gates.
```

## Completion Criteria

V31 is complete when:

```text
public API registry validation passes
mocked integration run succeeds
V31 targeted tests pass
full test suite passes
release verification passes
GitHub CI passes
PR is merged
tag v31.0.0 is created on the merge commit
main / origin/main / v31.0.0 all point to the same commit
working tree is clean
```
