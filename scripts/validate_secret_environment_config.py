from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ENVIRONMENT_CONFIG_DIR = Path("config/environments")
ENV_EXAMPLE_PATH = Path(".env.example")
REQUIRED_ENVIRONMENTS = {"dev", "test", "prod"}
REQUIRED_CONFIG_KEYS = {
    "environment",
    "deployment_target",
    "pipeline_config_path",
    "workspace_profile",
    "catalog_name",
    "schema_name",
    "requires_approval",
    "credential_references",
    "runtime_roots",
}
REQUIRED_CREDENTIAL_REFS = {
    "source_api",
    "database",
    "databricks_workspace",
    "azure_storage",
}
PLACEHOLDER_VALUES = {"<set-locally>", "<placeholder>", "<redacted>"}
TEXT_SCAN_SUFFIXES = {".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".env", ".example"}
EXCLUDED_SCAN_PARTS = {".git", ".venv", "venv", "data", "output", "__pycache__"}
RISKY_KEYS = {"password", "secret", "token", "api_key", "apikey", "connection_string"}
ALLOWED_VALUE_PREFIXES = ("ENV:", "${", "<")
ALLOWED_LITERAL_VALUES = {"null", "none", "example", "placeholder", "redacted", "set-locally"}


class SecretEnvironmentValidationError(ValueError):
    """Raised when V26 secret/environment configuration is invalid."""


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SecretEnvironmentValidationError(f"missing required file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SecretEnvironmentValidationError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SecretEnvironmentValidationError(f"expected JSON object in {path}")
    return data


def is_env_reference(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if not value.startswith("ENV:"):
        return False
    name = value.split(":", 1)[1]
    return bool(re.fullmatch(r"[A-Z][A-Z0-9_]*", name))


def validate_environment_config(path: Path, expected_environment: str) -> list[str]:
    issues: list[str] = []
    data = load_json(path)

    missing_keys = REQUIRED_CONFIG_KEYS - set(data)
    for key in sorted(missing_keys):
        issues.append(f"{path}: missing key {key}")

    if data.get("environment") != expected_environment:
        issues.append(f"{path}: environment must be {expected_environment}")

    if not isinstance(data.get("requires_approval"), bool):
        issues.append(f"{path}: requires_approval must be boolean")

    if expected_environment == "prod" and data.get("requires_approval") is not True:
        issues.append(f"{path}: prod must require approval")

    credential_refs = data.get("credential_references", {})
    if not isinstance(credential_refs, dict):
        issues.append(f"{path}: credential_references must be an object")
    else:
        missing_refs = REQUIRED_CREDENTIAL_REFS - set(credential_refs)
        for ref_name in sorted(missing_refs):
            issues.append(f"{path}: missing credential reference {ref_name}")
        for ref_name, ref_value in credential_refs.items():
            if not is_env_reference(ref_value):
                issues.append(f"{path}: credential reference {ref_name} must use ENV:NAME format")

    runtime_roots = data.get("runtime_roots", {})
    if not isinstance(runtime_roots, dict):
        issues.append(f"{path}: runtime_roots must be an object")
    else:
        for key in ["data_root", "output_root"]:
            value = runtime_roots.get(key)
            if not isinstance(value, str) or not value.strip():
                issues.append(f"{path}: runtime_roots.{key} must be a non-empty string")

    return issues


def validate_all_environment_configs() -> list[str]:
    issues: list[str] = []
    for environment in sorted(REQUIRED_ENVIRONMENTS):
        path = ENVIRONMENT_CONFIG_DIR / f"{environment}.json"
        issues.extend(validate_environment_config(path, environment))
    return issues


def parse_env_example(path: Path = ENV_EXAMPLE_PATH) -> dict[str, str]:
    if not path.exists():
        raise SecretEnvironmentValidationError(f"missing required file: {path}")
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def validate_env_example() -> list[str]:
    issues: list[str] = []
    values = parse_env_example()
    required = {
        "APP_ENV",
        "PIPELINE_CONFIG_PATH",
        "ENVIRONMENT_CONFIG_PATH",
        "CUSTOMER_SOURCE_API_CREDENTIAL",
        "CUSTOMER_DATABASE_CREDENTIAL",
        "DATABRICKS_WORKSPACE_CREDENTIAL",
        "AZURE_STORAGE_CREDENTIAL",
    }
    missing = required - set(values)
    for key in sorted(missing):
        issues.append(f".env.example missing {key}")

    for key, value in values.items():
        if key.endswith("_CREDENTIAL") and value not in PLACEHOLDER_VALUES:
            issues.append(f".env.example {key} must use a placeholder value")

    return issues


def should_scan(path: Path) -> bool:
    if any(part in EXCLUDED_SCAN_PARTS for part in path.parts):
        return False
    if path.name == ".env.example":
        return True
    if path.suffix.lower() in TEXT_SCAN_SUFFIXES:
        return True
    return False


def is_allowed_literal(value: str) -> bool:
    cleaned = value.strip().strip('"\'').strip().rstrip(",")
    lowered = cleaned.lower()
    if not cleaned:
        return True
    if cleaned.startswith(ALLOWED_VALUE_PREFIXES):
        return True
    if lowered in ALLOWED_LITERAL_VALUES:
        return True
    if "example" in lowered or "placeholder" in lowered or "redacted" in lowered:
        return True
    return False


def find_potential_hardcoded_credentials(root: Path = Path(".")) -> list[str]:
    issues: list[str] = []
    assignment_pattern = re.compile(
        r"(?i)(password|secret|token|api[_-]?key|connection[_-]?string)\s*[:=]\s*([^\s,}\]]+)"
    )

    for path in root.rglob("*"):
        if not path.is_file() or not should_scan(path):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(content.splitlines(), start=1):
            for match in assignment_pattern.finditer(line):
                key = match.group(1).lower()
                value = match.group(2)
                if key in RISKY_KEYS and not is_allowed_literal(value):
                    issues.append(f"{path}:{line_number}: possible hardcoded credential literal")
    return issues


def validate_secret_environment_config() -> list[str]:
    issues: list[str] = []
    issues.extend(validate_all_environment_configs())
    issues.extend(validate_env_example())
    issues.extend(find_potential_hardcoded_credentials())
    return issues


def assert_valid_secret_environment_config() -> None:
    issues = validate_secret_environment_config()
    if issues:
        raise SecretEnvironmentValidationError("; ".join(issues))


def main() -> int:
    issues = validate_secret_environment_config()
    if issues:
        print("Secret/environment configuration validation FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Secret/environment configuration validation SUCCESS")
    print("Validated environments: dev, test, prod")
    print("Validated template: .env.example")
    return 0


if __name__ == "__main__":
    sys.exit(main())
