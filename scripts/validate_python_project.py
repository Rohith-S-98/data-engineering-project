from __future__ import annotations

import argparse
import py_compile
import sys
from pathlib import Path

DEFAULT_PATHS = ("main.py", "scripts", "tests")
EXCLUDED_PARTS = {".venv", "venv", "__pycache__", ".git", ".pytest_cache"}


def iter_python_files(paths: tuple[str, ...] = DEFAULT_PATHS) -> list[Path]:
    python_files: list[Path] = []

    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue

        if path.is_file() and path.suffix == ".py":
            python_files.append(path)
            continue

        if path.is_dir():
            for file_path in path.rglob("*.py"):
                if EXCLUDED_PARTS.intersection(file_path.parts):
                    continue
                python_files.append(file_path)

    return sorted(python_files)


def validate_python_files(paths: tuple[str, ...] = DEFAULT_PATHS) -> list[str]:
    errors: list[str] = []

    for file_path in iter_python_files(paths):
        try:
            py_compile.compile(str(file_path), doraise=True)
        except py_compile.PyCompileError as error:
            errors.append(f"{file_path}: {error.msg}")

    return errors


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Python syntax for the project.")
    parser.add_argument(
        "paths",
        nargs="*",
        default=list(DEFAULT_PATHS),
        help="Files or folders to validate. Defaults to main.py, scripts, and tests.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    errors = validate_python_files(tuple(args.paths))

    if errors:
        print("Python syntax validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Python syntax validation SUCCESS")
    print(f"Validated files: {len(iter_python_files(tuple(args.paths)))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
