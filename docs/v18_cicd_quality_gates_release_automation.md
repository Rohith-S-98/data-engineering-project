# V18.0.0 - CI/CD Hardening, Quality Gates, and Release Automation

V18 adds release-readiness checks on top of the V17 retry, recovery, and replay framework.

## Goal

The goal is to make the project safer to merge and release by validating code, configuration, tests, dry-run execution, and runtime-output cleanliness.

## V18 Additions

- Python syntax validation gate
- Config file validation gate
- Runtime-output cleanliness gate
- Release verification runner
- Release tag safety check
- Staged GitHub Actions workflow
- Pull request checklist

## Main Commands

```bash
python -m scripts.validate_python_project
python -m scripts.validate_config_files
python -m scripts.validate_runtime_cleanliness
python -m scripts.release_verification --version v18.0.0
python -m scripts.validate_release_tag --version v18.0.0
```

## Production Explanation

In production data engineering, CI/CD should catch broken code, invalid configs, failed tests, unsafe runtime files, and bad release tags before deployment.

## Interview Explanation

I hardened a PySpark medallion pipeline by adding CI/CD quality gates for syntax checks, configuration checks, targeted tests, full tests, dry-run orchestration, runtime-output cleanliness, release verification, and tag safety.
