from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REQUIRED_REPOSITORY_FILES = [
    "README.md",
    ".gitignore",
    ".dockerignore",
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    "databricks.yml",
    "scripts/release_verification.py",
    "scripts/validate_python_project.py",
    "scripts/validate_config_files.py",
    "scripts/validate_runtime_cleanliness.py",
    "scripts/validate_databricks_bundle_structure.py",
]

REQUIRED_PLACEHOLDERS = [
    "data/bronze/.gitkeep",
    "data/silver/.gitkeep",
    "data/gold/.gitkeep",
    "data/audit/.gitkeep",
    "output/audit/.gitkeep",
    "output/dq_reports/.gitkeep",
    "output/quarantine/.gitkeep",
    "output/reltio_payloads/.gitkeep",
    "output/logs/.gitkeep",
    "output/observability/.gitkeep",
    "output/job_control/.gitkeep",
    "output/runtime_parameters/.gitkeep",
    "output/alerts/.gitkeep",
    "output/recovery/.gitkeep",
]

REQUIRED_GITIGNORE_TOKENS = [
    "__pycache__/",
    ".venv/",
    ".env.*",
    "!/data/bronze/.gitkeep",
    "/output/runtime_parameters/*",
    "!/output/runtime_parameters/.gitkeep",
    "/data/raw/customer_data_api.csv",
    "/data/raw/customer_data_db.csv",
    "/data/database/*.db",
]

REQUIRED_DOCKERIGNORE_TOKENS = [
    ".git",
    ".venv",
    ".env.*",
    "__pycache__",
    "data/raw/customer_data_api.csv",
    "data/raw/customer_data_db.csv",
    "data/database/*.db",
    "output/runtime_parameters/*",
]

TRACKED_RUNTIME_OUTPUT_PREFIXES = [
    "data/bronze/",
    "data/silver/",
    "data/gold/",
    "data/audit/",
    "output/audit/",
    "output/dq_reports/",
    "output/quarantine/",
    "output/reltio_payloads/",
    "output/logs/",
    "output/observability/",
    "output/job_control/",
    "output/runtime_parameters/",
    "output/alerts/",
    "output/recovery/",
]

ALLOWED_RUNTIME_PLACEHOLDERS = set(REQUIRED_PLACEHOLDERS)

DISALLOWED_TRACKED_PATHS = {
    "data/raw/customer_data.csv",
    "data/raw/customer_data_clean.csv",
    "data/raw/customer_data_dirty.csv",
    "data/raw/customer_data_api.csv",
    "data/raw/customer_data_db.csv",
    "data/database/customer_source.db",
}

DISALLOWED_TRACKED_SUFFIXES = (
    ".pyc",
    ".pyo",
    ".log",
    ".crc",
    ".snappy.parquet",
    ".db",
)

DISALLOWED_TRACKED_PARTS = (
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
    "_delta_log",
)


class RepoHygieneValidationError(ValueError):
    """Raised when repository hygiene validation fails."""


def validate_required_files(root: Path | str = Path(".")) -> list[str]:
    root_path = Path(root)
    issues: list[str] = []

    for relative_path in REQUIRED_REPOSITORY_FILES + REQUIRED_PLACEHOLDERS:
        if not (root_path / relative_path).exists():
            issues.append(f"missing required repository file: {relative_path}")

    return issues


def validate_required_tokens(root: Path | str = Path(".")) -> list[str]:
    root_path = Path(root)
    issues: list[str] = []
    gitignore = (root_path / ".gitignore").read_text(encoding="utf-8") if (root_path / ".gitignore").exists() else ""
    dockerignore = (root_path / ".dockerignore").read_text(encoding="utf-8") if (root_path / ".dockerignore").exists() else ""

    for token in REQUIRED_GITIGNORE_TOKENS:
        if token not in gitignore:
            issues.append(f"missing .gitignore token: {token}")

    for token in REQUIRED_DOCKERIGNORE_TOKENS:
        if token not in dockerignore:
            issues.append(f"missing .dockerignore token: {token}")

    return issues


def list_tracked_files(root: Path | str = Path(".")) -> list[str]:
    root_path = Path(root)
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RepoHygieneValidationError(f"Unable to list tracked files: {result.stderr.strip()}")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def validate_tracked_files(tracked_files: list[str]) -> list[str]:
    issues: list[str] = []

    for tracked_file in tracked_files:
        if tracked_file in DISALLOWED_TRACKED_PATHS:
            issues.append(f"generated runtime file is tracked: {tracked_file}")

        if tracked_file.endswith(DISALLOWED_TRACKED_SUFFIXES):
            issues.append(f"generated/cache file is tracked: {tracked_file}")

        if any(part in tracked_file.split("/") for part in DISALLOWED_TRACKED_PARTS):
            issues.append(f"cache/generated folder content is tracked: {tracked_file}")

        if _is_tracked_runtime_output(tracked_file):
            issues.append(f"runtime output is tracked instead of placeholder only: {tracked_file}")

    return issues


def _is_tracked_runtime_output(tracked_file: str) -> bool:
    if tracked_file in ALLOWED_RUNTIME_PLACEHOLDERS:
        return False
    return any(tracked_file.startswith(prefix) for prefix in TRACKED_RUNTIME_OUTPUT_PREFIXES)


def validate_repo_hygiene(root: Path | str = Path(".")) -> list[str]:
    issues: list[str] = []
    issues.extend(validate_required_files(root))
    issues.extend(validate_required_tokens(root))
    issues.extend(validate_tracked_files(list_tracked_files(root)))
    return issues


def assert_valid_repo_hygiene(root: Path | str = Path(".")) -> None:
    issues = validate_repo_hygiene(root)
    if issues:
        raise RepoHygieneValidationError("; ".join(issues))


def main() -> int:
    issues = validate_repo_hygiene()
    if issues:
        print("Repository hygiene validation FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Repository hygiene validation SUCCESS")
    print(f"Required files checked: {len(REQUIRED_REPOSITORY_FILES)}")
    print(f"Runtime placeholders checked: {len(REQUIRED_PLACEHOLDERS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
