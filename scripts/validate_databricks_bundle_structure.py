from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_FILES = [
    "databricks.yml",
    "resources/customer_medallion_job.yml",
    "deployment/databricks/README.md",
]

DATABRICKS_ROOT_REQUIRED_TOKENS = [
    "bundle:",
    "name: data-engineering-project",
    "include:",
    "resources/*.yml",
    "targets:",
    "dev:",
    "prod:",
]

JOB_RESOURCE_REQUIRED_TOKENS = [
    "resources:",
    "jobs:",
    "customer_medallion_pipeline_job:",
    "tasks:",
    "validate_python_project",
    "validate_config_files",
    "run_pipeline_dry_run",
    "run_runtime_cleanliness",
]


class DatabricksBundleValidationError(ValueError):
    """Raised when the Databricks bundle-style structure is invalid."""


def validate_required_files(root: Path | str = Path(".")) -> list[str]:
    root_path = Path(root)
    issues: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root_path / relative_path).exists():
            issues.append(f"missing file: {relative_path}")

    return issues


def validate_file_contains_tokens(file_path: Path, tokens: list[str]) -> list[str]:
    content = file_path.read_text(encoding="utf-8")
    return [f"missing token in {file_path}: {token}" for token in tokens if token not in content]


def validate_databricks_bundle_structure(root: Path | str = Path(".")) -> list[str]:
    root_path = Path(root)
    issues = validate_required_files(root_path)

    if issues:
        return issues

    issues.extend(validate_file_contains_tokens(root_path / "databricks.yml", DATABRICKS_ROOT_REQUIRED_TOKENS))
    issues.extend(validate_file_contains_tokens(root_path / "resources/customer_medallion_job.yml", JOB_RESOURCE_REQUIRED_TOKENS))
    return issues


def assert_valid_databricks_bundle_structure(root: Path | str = Path(".")) -> None:
    issues = validate_databricks_bundle_structure(root)
    if issues:
        raise DatabricksBundleValidationError("; ".join(issues))


def main() -> int:
    issues = validate_databricks_bundle_structure()
    if issues:
        print("Databricks bundle structure validation FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Databricks bundle structure validation SUCCESS")
    print(f"Validated files: {len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
