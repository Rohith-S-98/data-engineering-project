from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

DEFAULT_MANIFEST_PATH = Path("tests/integration/customer_pipeline_e2e_manifest.json")
SUPPORTED_MODES = {"smoke", "full"}


@dataclass(frozen=True)
class IntegrationGate:
    name: str
    command: list[str]
    mode: str


@dataclass(frozen=True)
class IntegrationResult:
    name: str
    command: list[str]
    returncode: int

    @property
    def success(self) -> bool:
        return self.returncode == 0


def load_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> dict:
    if not path.exists():
        raise ValueError(f"E2E integration manifest not found: {path}")

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid E2E integration manifest JSON: {path}: {exc}") from exc

    if not isinstance(manifest, dict):
        raise ValueError("E2E integration manifest must be a JSON object")

    gates = manifest.get("gates")
    if not isinstance(gates, list) or not gates:
        raise ValueError("E2E integration manifest must define at least one gate")

    return manifest


def parse_gate(raw_gate: dict) -> IntegrationGate:
    if not isinstance(raw_gate, dict):
        raise ValueError("Each E2E gate must be a JSON object")

    name = raw_gate.get("name")
    command = raw_gate.get("command")
    mode = raw_gate.get("mode", "smoke")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Each E2E gate must have a non-empty name")

    if not isinstance(command, list) or not command:
        raise ValueError(f"E2E gate {name} must define a non-empty command list")

    if any(not isinstance(part, str) or not part.strip() for part in command):
        raise ValueError(f"E2E gate {name} command must contain only non-empty strings")

    if mode not in SUPPORTED_MODES:
        raise ValueError(f"E2E gate {name} has unsupported mode: {mode}")

    return IntegrationGate(name=name, command=command, mode=mode)


def select_gates(manifest: dict, mode: str) -> list[IntegrationGate]:
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"Unsupported E2E mode: {mode}")

    gates = [parse_gate(raw_gate) for raw_gate in manifest["gates"]]
    if mode == "full":
        return gates
    return [gate for gate in gates if gate.mode == "smoke"]


def render_command(command: Sequence[str], run_date: str) -> list[str]:
    return [
        part.replace("{python}", sys.executable).replace("{run_date}", run_date)
        for part in command
    ]


def run_gate(
    gate: IntegrationGate,
    run_date: str,
    command_runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> IntegrationResult:
    command = render_command(gate.command, run_date=run_date)
    print("=" * 70)
    print(f"Running E2E gate: {gate.name}")
    print(" ".join(command))
    completed = command_runner(command, check=False)
    return IntegrationResult(name=gate.name, command=command, returncode=completed.returncode)


def run_e2e_manifest(
    manifest: dict,
    mode: str,
    run_date: str,
    command_runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> list[IntegrationResult]:
    results: list[IntegrationResult] = []
    for gate in select_gates(manifest, mode):
        result = run_gate(gate, run_date=run_date, command_runner=command_runner)
        results.append(result)
        if not result.success:
            break
    return results


def print_summary(results: list[IntegrationResult]) -> None:
    print("=" * 70)
    print("V27 E2E Integration Summary")
    for result in results:
        status = "SUCCESS" if result.success else "FAILED"
        print(f"{result.name}: {status}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run manifest-driven E2E integration checks.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST_PATH), help="E2E integration manifest path.")
    parser.add_argument("--mode", choices=sorted(SUPPORTED_MODES), default="smoke", help="Integration gate mode to run.")
    parser.add_argument("--run-date", default=None, help="Run date passed to orchestration gates.")
    parser.add_argument("--list-gates", action="store_true", help="List selected gates without executing them.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = load_manifest(manifest_path)
    run_date = args.run_date or manifest.get("default_run_date") or "2026-06-23"
    selected_gates = select_gates(manifest, args.mode)

    print(f"Manifest: {manifest_path}")
    print(f"Mode: {args.mode}")
    print(f"Run date: {run_date}")

    if args.list_gates:
        for gate in selected_gates:
            print(f"- {gate.name}")
        return 0

    results = run_e2e_manifest(manifest, mode=args.mode, run_date=run_date)
    print_summary(results)

    if not results or any(not result.success for result in results):
        print("V27 E2E integration FAILED")
        return 1

    print("V27 E2E integration SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
