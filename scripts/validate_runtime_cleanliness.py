from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RUNTIME_DIRS = (
    "data/bronze",
    "data/silver",
    "data/gold",
    "data/audit",
    "output/audit",
    "output/dq_reports",
    "output/quarantine",
    "output/reltio_payloads",
    "output/logs",
    "output/observability",
    "output/job_control",
    "output/runtime_parameters",
    "output/alerts",
    "output/recovery",
)


def _run_git_command(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def find_tracked_runtime_files() -> list[str]:
    files: list[str] = []
    for runtime_dir in RUNTIME_DIRS:
        tracked_files = _run_git_command(["ls-files", runtime_dir])
        for file_name in tracked_files:
            if not file_name.endswith("/.gitkeep"):
                files.append(file_name)
    return sorted(files)


def find_dirty_runtime_paths() -> list[str]:
    paths: list[str] = []
    for runtime_dir in RUNTIME_DIRS:
        status_lines = _run_git_command(["status", "--short", "--untracked-files=all", "--", runtime_dir])
        for line in status_lines:
            if not line.endswith(".gitkeep"):
                paths.append(line)
    return sorted(paths)


def validate_runtime_cleanliness() -> list[str]:
    issues: list[str] = []
    for file_name in find_tracked_runtime_files():
        issues.append(f"tracked runtime file should not be committed: {file_name}")
    for path in find_dirty_runtime_paths():
        issues.append(f"dirty runtime output found: {path}")
    return issues


def main() -> int:
    issues = validate_runtime_cleanliness()
    if issues:
        print("Runtime cleanliness validation FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Runtime cleanliness validation SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
