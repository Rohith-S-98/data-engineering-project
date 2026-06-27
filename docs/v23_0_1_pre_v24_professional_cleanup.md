# V23.0.1 - Pre-V24 Professional Repository Cleanup

V23.0.1 is a professional repository hygiene release before starting V24.

## Goal

The goal is to keep the repository clean, portfolio-ready, and production-style before adding Azure orchestration simulation in V24.

## Cleanup Scope

- Hardened `.gitignore`
- Hardened `.dockerignore`
- Added repository hygiene validator
- Added repository hygiene tests
- Added repository hygiene gate to release verification
- Added repository hygiene job to GitHub Actions CI
- Preserved all required version history, tests, docs, configs, and committed fixtures

## What Must Stay in the Repo

The following categories are intentionally kept:

```text
source code
unit tests
configuration files
sample fixtures required by tests
documentation
Databricks bundle-style metadata
Docker/CI/CD files
.gitkeep placeholders for runtime output folders
```

## What Must Not Be Tracked

The repository hygiene validator protects against accidentally tracking:

```text
Python cache files
local virtual environments
local secrets
runtime output files
Spark/Delta generated files
locally generated raw landing outputs
SQLite database files
logs and coverage artifacts
```

## Validation Command

```bash
python -m scripts.validate_repo_hygiene
```

Expected output:

```text
Repository hygiene validation SUCCESS
Required files checked: 12
Runtime placeholders checked: 14
```

## Full Pre-V24 Validation

```bash
python -m scripts.validate_python_project
python -m scripts.validate_config_files
python -m scripts.validate_docker_artifacts
python -m scripts.validate_databricks_bundle_structure
python -m scripts.validate_repo_hygiene
python -m unittest tests.test_v23_0_1_repo_hygiene
python -m unittest discover tests
python -m scripts.pipeline_orchestrator --dry-run --run-date 2026-06-23
python -m scripts.validate_runtime_cleanliness
```

## Interview Explanation

Before starting V24, I performed a professional repository cleanup release. I hardened `.gitignore` and `.dockerignore`, added a repository hygiene validator, added tests to prevent generated data or runtime artifacts from being tracked, integrated the hygiene gate into release verification and CI, and preserved all required docs, tests, configs, and sample fixtures.
