# V27.0.0 - End-to-End Integration Testing Framework

V27 adds a manifest-driven end-to-end integration testing framework for the customer medallion pipeline project.

## Goal

The goal is to prove that the project can be validated as a connected system, not only as isolated scripts and unit tests.

## Added Files

```text
tests/integration/customer_pipeline_e2e_manifest.json
scripts/run_e2e_integration_tests.py
tests/test_v27_e2e_integration_framework.py
.github/workflows/v27-e2e-integration-ci.yml
docs/v27_end_to_end_integration_testing_framework.md
```

## What the Framework Does

The V27 runner reads an integration manifest and executes a controlled set of release-style gates.

The smoke-mode gates include:

```text
config validation
environment validation
V26 environment tests
dry-run orchestrator
runtime cleanliness validation
```

The full-mode manifest also includes:

```text
ADF artifact validation
Power BI dashboard artifact validation
```

## Commands

List smoke gates:

```bash
python -m scripts.run_e2e_integration_tests --mode smoke --list-gates
```

Run smoke E2E gates:

```bash
python -m scripts.run_e2e_integration_tests --mode smoke --run-date 2026-06-23
```

Run full E2E gates:

```bash
python -m scripts.run_e2e_integration_tests --mode full --run-date 2026-06-23
```

Run V27 framework tests:

```bash
python -m unittest tests.test_v27_e2e_integration_framework
```

## Why This Matters

Unit tests prove that individual components work. End-to-end integration checks prove that the pipeline framework can be validated as a system.

V27 connects existing production-style gates into a single integration runner:

```text
manifest -> selected gates -> command execution -> fail-fast behavior -> summary -> release gate
```

## CI/CD Integration

V27 adds a dedicated GitHub Actions workflow:

```text
.github/workflows/v27-e2e-integration-ci.yml
```

It runs the E2E smoke gates and the V27 framework tests.

The main release verification script also runs the E2E smoke gate before the targeted unit test suite.

## Interview Explanation

I added a manifest-driven end-to-end integration testing framework. Instead of only running independent unit tests, the framework reads a JSON manifest and executes system-level validation gates such as configuration validation, environment validation, dry-run orchestration, and runtime cleanliness checks. The runner supports smoke and full modes, fail-fast behavior, command rendering, local execution, CI execution, and unit tests for the framework itself.

## Apexon / IQVIA Mapping

In an IQVIA-style MDM pipeline, engineers need confidence that source ingestion, configuration, DQ controls, orchestration, deployment metadata, observability, and runtime hygiene work together. V27 simulates that integration validation pattern locally and makes it repeatable through CI/CD.
