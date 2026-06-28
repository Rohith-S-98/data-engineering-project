from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

MANIFEST_PATH = Path("release/capstone/v30_production_readiness_manifest.json")
REQUIRED_VERSION = "v30.0.0"
REQUIRED_BASELINE = "v29.0.0"
REQUIRED_CATEGORIES = {
    "ingestion",
    "data_quality_and_quarantine",
    "lakehouse_processing",
    "operations_and_recovery",
    "deployment_and_ci_cd",
    "observability_and_reporting",
    "security_and_environment_safety",
    "system_validation_and_storytelling",
}
REQUIRED_RELEASE_GATES = {
    "python syntax",
    "config validation",
    "docker artifact validation",
    "databricks bundle structure validation",
    "repository hygiene validation",
    "adf artifact validation",
    "power bi dashboard artifact validation",
    "secret environment config validation",
    "partition strategy validation",
    "storytelling pack validation",
    "capstone readiness validation",
    "e2e integration smoke",
    "full test suite",
    "dry-run orchestrator",
    "runtime cleanliness",
}
MIN_EVIDENCE_PER_CATEGORY = 3


class CapstoneReadinessValidationError(ValueError):
    """Raised when V30 capstone readiness metadata is invalid."""


def load_capstone_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    if not path.exists():
        raise CapstoneReadinessValidationError(f"capstone manifest not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CapstoneReadinessValidationError(f"invalid capstone manifest JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise CapstoneReadinessValidationError("capstone manifest must be a JSON object")
    return data


def validate_evidence_file(path_text: str, category: str) -> list[str]:
    issues: list[str] = []
    path = Path(path_text)
    if path.is_absolute():
        issues.append(f"{category}: evidence path must be relative: {path_text}")
    if ".." in path.parts:
        issues.append(f"{category}: evidence path must not traverse parent directories: {path_text}")
    if not path.exists():
        issues.append(f"{category}: evidence file missing: {path_text}")
    return issues


def validate_categories(manifest: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    categories = manifest.get("production_readiness_categories")

    if not isinstance(categories, list) or not categories:
        return ["production_readiness_categories must be a non-empty list"]

    found_categories: set[str] = set()
    for raw_category in categories:
        if not isinstance(raw_category, dict):
            issues.append("each production readiness category must be an object")
            continue

        name = raw_category.get("name")
        evidence = raw_category.get("evidence")

        if not isinstance(name, str) or not name.strip():
            issues.append("each category must have a non-empty name")
            continue

        if name in found_categories:
            issues.append(f"duplicate production readiness category: {name}")
        found_categories.add(name)

        if not isinstance(evidence, list) or len(evidence) < MIN_EVIDENCE_PER_CATEGORY:
            issues.append(f"{name}: must include at least {MIN_EVIDENCE_PER_CATEGORY} evidence files")
            continue

        for item in evidence:
            if not isinstance(item, str) or not item.strip():
                issues.append(f"{name}: evidence entries must be non-empty strings")
                continue
            issues.extend(validate_evidence_file(item, name))

    missing_categories = REQUIRED_CATEGORIES - found_categories
    for category in sorted(missing_categories):
        issues.append(f"missing production readiness category: {category}")

    extra_categories = found_categories - REQUIRED_CATEGORIES
    for category in sorted(extra_categories):
        issues.append(f"unexpected production readiness category: {category}")

    return issues


def validate_release_gates(manifest: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    gates = manifest.get("required_release_gates")
    if not isinstance(gates, list) or not gates:
        return ["required_release_gates must be a non-empty list"]

    gate_names = set()
    for gate in gates:
        if not isinstance(gate, str) or not gate.strip():
            issues.append("release gate names must be non-empty strings")
            continue
        gate_names.add(gate)

    missing_gates = REQUIRED_RELEASE_GATES - gate_names
    for gate in sorted(missing_gates):
        issues.append(f"missing required release gate: {gate}")

    return issues


def validate_capstone_readiness(path: Path = MANIFEST_PATH) -> list[str]:
    issues: list[str] = []
    manifest = load_capstone_manifest(path)

    if manifest.get("version") != REQUIRED_VERSION:
        issues.append(f"capstone manifest version must be {REQUIRED_VERSION}")

    if manifest.get("baseline_version") != REQUIRED_BASELINE:
        issues.append(f"capstone baseline version must be {REQUIRED_BASELINE}")

    if manifest.get("status") != "capstone-ready":
        issues.append("capstone status must be capstone-ready")

    if manifest.get("profile_update_status") != "deferred-until-v31-final-phase":
        issues.append("profile update status must remain deferred until V31 final phase")

    backlog = manifest.get("post_capstone_backlog")
    if not isinstance(backlog, list) or "v31.0.0 - Live Public API Integration Testing Framework" not in backlog:
        issues.append("post capstone backlog must include V31 live public API integration testing")

    completion_statement = manifest.get("completion_statement")
    if not isinstance(completion_statement, str) or "production-style Data Engineering capstone" not in completion_statement:
        issues.append("completion_statement must describe production-style Data Engineering capstone readiness")

    issues.extend(validate_categories(manifest))
    issues.extend(validate_release_gates(manifest))
    return issues


def assert_valid_capstone_readiness(path: Path = MANIFEST_PATH) -> None:
    issues = validate_capstone_readiness(path)
    if issues:
        raise CapstoneReadinessValidationError("; ".join(issues))


def main() -> int:
    issues = validate_capstone_readiness()
    if issues:
        print("Capstone readiness validation FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    manifest = load_capstone_manifest()
    print("Capstone readiness validation SUCCESS")
    print(f"Validated categories: {len(manifest['production_readiness_categories'])}")
    print(f"Validated release gates: {len(manifest['required_release_gates'])}")
    print(f"Validated manifest: {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
