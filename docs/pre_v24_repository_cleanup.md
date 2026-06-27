# Pre-V24 Repository Cleanup

This cleanup prepares the repository for V24 without changing the released V23 feature baseline.

## Cleanup Goals

- Keep runtime-generated outputs out of Git.
- Keep static sample data in fixture-style locations.
- Keep validation commands stable before starting V24.
- Document safe branch cleanup after merged version PRs.

## Changes

- Moved the committed V22 DQ catalog sample input from `data/raw/` to `tests/fixtures/`.
- Updated `scripts/advanced_dq_rule_catalog.py` to read the sample fixture from `tests/fixtures/customer_data_dq_catalog_sample.csv`.
- Deleted `data/raw/customer_data_dq_catalog_sample.csv` from the repository because `data/raw/` is a runtime landing zone.
- Tightened `.gitignore` and `.dockerignore` so runtime raw/database outputs remain local.
- Updated V22 documentation to clarify that committed sample inputs belong under `tests/fixtures/`.

## Professional Repository Convention

```text
config/              committed metadata and configs
docs/                committed documentation
scripts/             committed executable framework code
tests/               committed tests
tests/fixtures/      committed small deterministic test inputs
data/raw/            runtime landing outputs, not committed
output/              runtime reports/logs, not committed
```

## Safe Branch Cleanup

After this cleanup PR is merged and validated, stale merged remote branches can be deleted.

Recommended remote branch cleanup commands:

```bash
git fetch --all --prune

git push origin --delete v23-databricks-asset-bundle-structure
git push origin --delete v22-advanced-data-quality-rule-catalog
git push origin --delete v21-database-ingestion-framework
git push origin --delete v20-api-ingestion-framework
git push origin --delete v19-docker-containerized-local-runtime
git push origin --delete v18-cicd-quality-gates-release-automation
git push origin --delete v15-scheduling-dependency-runtime-parameters
git push origin --delete v13.0.2-markdown-cleanup
git push origin --delete pre-v14-repo-review-cleanup
git push origin --delete cleanup/v9-before-v10
git push origin --delete hotfix/v9-baseline-before-v10
```

Do not delete `main` or release tags such as `v23.0.0`.

## Pre-V24 Validation Commands

```bash
python3 -m scripts.validate_python_project
python3 -m scripts.validate_config_files
python3 -m scripts.validate_docker_artifacts
python3 -m scripts.validate_databricks_bundle_structure
python3 -m unittest tests.test_v23_databricks_bundle_structure
python3 -m unittest tests.test_v22_advanced_dq_rule_catalog
python3 -m scripts.advanced_dq_rule_catalog
python3 -m unittest discover tests
python3 -m scripts.pipeline_orchestrator --dry-run --run-date 2026-06-23
python3 -m scripts.validate_runtime_cleanliness
```
