from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

README_PATH = Path("README.md")


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def read_current_version(readme_path: Path = README_PATH) -> str:
    for line in readme_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("Current Version:"):
            return line.split(":", 1)[1].strip()
    raise ValueError("README Current Version line was not found")


def validate_release_tag(version: str, require_clean_tree: bool = True) -> list[str]:
    issues: list[str] = []

    try:
        current_version = read_current_version()
    except ValueError as error:
        issues.append(str(error))
        current_version = ""

    if current_version and current_version != version:
        issues.append(f"README version is {current_version}, expected {version}")

    tag_check = run_git(["rev-parse", "--verify", f"refs/tags/{version}"])
    if tag_check.returncode == 0:
        issues.append(f"tag already exists: {version}")

    if require_clean_tree:
        status = run_git(["status", "--short"])
        if status.stdout.strip():
            issues.append("working tree is not clean")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate release tag safety before tagging.")
    parser.add_argument("--version", required=True, help="Expected release version, for example v18.0.0.")
    parser.add_argument("--allow-dirty", action="store_true", help="Skip clean working tree validation.")
    args = parser.parse_args()

    issues = validate_release_tag(
        version=args.version,
        require_clean_tree=not args.allow_dirty,
    )

    if issues:
        print("Release tag validation FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Release tag validation SUCCESS")
    print(f"Version: {args.version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
