from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class VerificationCommand:
    name: str
    command: list[str]


def build_commands(skip_real_run: bool, skip_alerting: bool) -> list[VerificationCommand]:
    python = sys.executable
    commands = [
        VerificationCommand("python syntax", [python, "-m", "scripts.validate_python_project"]),
        VerificationCommand("config validation", [python, "-m", "scripts.validate_config_files"]),
        VerificationCommand("docker artifact validation", [python, "-m", "scripts.validate_docker_artifacts"]),
        VerificationCommand("targeted retry tests", [python, "-m", "unittest", "tests.test_pipeline_retry"]),
        VerificationCommand("targeted orchestrator retry tests", [python, "-m", "unittest", "tests.test_v17_orchestrator_retry"]),
        VerificationCommand("targeted v18 quality tests", [python, "-m", "unittest", "tests.test_v18_quality_gates"]),
        VerificationCommand("targeted v19 docker tests", [python, "-m", "unittest", "tests.test_v19_docker_artifacts"]),
        VerificationCommand("targeted v20 api tests", [python, "-m", "unittest", "tests.test_v20_api_ingestion"]),
        VerificationCommand("targeted v21 database tests", [python, "-m", "unittest", "tests.test_v21_database_ingestion"]),
        VerificationCommand("targeted v22 dq catalog tests", [python, "-m", "unittest", "tests.test_v22_advanced_dq_rule_catalog"]),
        VerificationCommand("full test suite", [python, "-m", "unittest", "discover", "tests"]),
        VerificationCommand("dry-run orchestrator", [python, "-m", "scripts.pipeline_orchestrator", "--dry-run", "--run-date", "2026-06-23"]),
    ]

    if not skip_real_run:
        commands.append(
            VerificationCommand("real orchestrator", [python, "-m", "scripts.pipeline_orchestrator", "--run-date", "2026-06-23"])
        )

    if not skip_alerting:
        commands.append(VerificationCommand("independent alerting", [python, "-m", "scripts.pipeline_alerting"]))

    commands.append(VerificationCommand("runtime cleanliness", [python, "-m", "scripts.validate_runtime_cleanliness"]))
    return commands


def run_commands(commands: list[VerificationCommand]) -> int:
    for item in commands:
        print("=" * 70)
        print(f"Running: {item.name}")
        print(" ".join(item.command))
        result = subprocess.run(item.command, check=False)
        if result.returncode != 0:
            print(f"Release verification FAILED at gate: {item.name}")
            return result.returncode

    print("=" * 70)
    print("Release verification SUCCESS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run release verification gates.")
    parser.add_argument("--version", default="v22.0.0", help="Release version being verified.")
    parser.add_argument("--skip-real-run", action="store_true", help="Skip real orchestrator execution.")
    parser.add_argument("--skip-alerting", action="store_true", help="Skip independent alerting execution.")
    args = parser.parse_args()

    print(f"Version: {args.version}")
    commands = build_commands(
        skip_real_run=args.skip_real_run,
        skip_alerting=args.skip_alerting,
    )
    return run_commands(commands)


if __name__ == "__main__":
    sys.exit(main())
