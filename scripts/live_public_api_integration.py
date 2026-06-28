from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY_PATH = Path("config/api/live_public_api_sources.json")
REQUIRED_SOURCE_KEYS = {
    "source_name",
    "enabled",
    "live_enabled",
    "endpoint_reference",
    "http_method",
    "auth_type",
    "timeout_seconds",
    "expected_status_code",
    "response_type",
    "mock_response_path",
    "raw_landing_path",
    "normalized_csv_path",
    "schema_contract_path",
    "required_fields",
    "field_mapping",
}


@dataclass(frozen=True)
class PublicApiSourceSummary:
    source_name: str
    ingestion_mode: str
    raw_records: int
    normalized_records: int
    raw_landing_path: str
    normalized_csv_path: str


class PublicApiRegistryError(ValueError):
    """Raised when the V31 public API registry is invalid."""


class PublicApiResponseError(ValueError):
    """Raised when a public API response does not match required expectations."""


def load_json(path: Path | str) -> Any:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path | str, payload: Any) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_registry(path: Path | str = DEFAULT_REGISTRY_PATH) -> dict[str, Any]:
    registry = load_json(path)
    validate_registry(registry)
    return registry


def validate_registry(registry: dict[str, Any]) -> None:
    if registry.get("version") != "v31.0.0":
        raise PublicApiRegistryError("registry version must be v31.0.0")

    if registry.get("ci_safe_mode") is not True:
        raise PublicApiRegistryError("ci_safe_mode must be true")

    if registry.get("manual_execution_only") is not True:
        raise PublicApiRegistryError("manual_execution_only must be true")

    sources = registry.get("sources")
    if not isinstance(sources, list) or not sources:
        raise PublicApiRegistryError("sources must be a non-empty list")

    seen_names: set[str] = set()
    for source in sources:
        validate_source(source)
        source_name = source["source_name"]
        if source_name in seen_names:
            raise PublicApiRegistryError(f"duplicate source_name: {source_name}")
        seen_names.add(source_name)


def validate_source(source: dict[str, Any]) -> None:
    missing_keys = sorted(REQUIRED_SOURCE_KEYS - set(source))
    if missing_keys:
        raise PublicApiRegistryError(f"missing source keys: {missing_keys}")

    if source["http_method"] != "GET":
        raise PublicApiRegistryError("only GET sources are supported in V31")

    if source["auth_type"] != "none":
        raise PublicApiRegistryError("V31 public API registry only supports auth_type none")

    if source["response_type"] != "json":
        raise PublicApiRegistryError("V31 public API registry only supports JSON responses")

    if not isinstance(source["timeout_seconds"], int) or source["timeout_seconds"] <= 0:
        raise PublicApiRegistryError("timeout_seconds must be a positive integer")

    if not isinstance(source["expected_status_code"], int):
        raise PublicApiRegistryError("expected_status_code must be an integer")

    if not isinstance(source["required_fields"], list) or not source["required_fields"]:
        raise PublicApiRegistryError("required_fields must be a non-empty list")

    if not isinstance(source["field_mapping"], dict) or not source["field_mapping"]:
        raise PublicApiRegistryError("field_mapping must be a non-empty object")

    endpoint_reference = source["endpoint_reference"]
    if not isinstance(endpoint_reference, str) or not endpoint_reference.startswith("ENV:"):
        raise PublicApiRegistryError("endpoint_reference must use ENV:VARIABLE format")

    for path_key in ["mock_response_path", "raw_landing_path", "normalized_csv_path", "schema_contract_path"]:
        if not isinstance(source[path_key], str) or not source[path_key].strip():
            raise PublicApiRegistryError(f"{path_key} must be a non-empty string")

    if not Path(source["mock_response_path"]).exists():
        raise PublicApiRegistryError(f"mock response path does not exist: {source['mock_response_path']}")

    if not Path(source["schema_contract_path"]).exists():
        raise PublicApiRegistryError(f"schema contract path does not exist: {source['schema_contract_path']}")


def resolve_env_endpoint(endpoint_reference: str) -> str:
    env_name = endpoint_reference.replace("ENV:", "", 1)
    value = os.environ.get(env_name)
    if not value:
        raise PublicApiRegistryError(f"missing endpoint environment variable: {env_name}")
    return value


def fetch_source_payload(source: dict[str, Any], allow_live: bool) -> tuple[str, Any]:
    if not source.get("enabled", False):
        return "disabled", []

    if allow_live and source.get("live_enabled") is True:
        endpoint = resolve_env_endpoint(source["endpoint_reference"])
        request = urllib.request.Request(endpoint, method="GET")
        with urllib.request.urlopen(request, timeout=source["timeout_seconds"]) as response:
            status_code = getattr(response, "status", None)
            if status_code != source["expected_status_code"]:
                raise PublicApiResponseError(
                    f"{source['source_name']}: expected status {source['expected_status_code']} but got {status_code}"
                )
            payload = json.loads(response.read().decode("utf-8"))
        return "manual-live", payload

    return "mock", load_json(source["mock_response_path"])


def get_nested_value(record: dict[str, Any], field_path: str) -> Any:
    value: Any = record
    for part in field_path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def payload_to_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list) and all(isinstance(item, dict) for item in payload):
        return payload
    raise PublicApiResponseError("payload must be an object or an array of objects")


def validate_required_fields(source: dict[str, Any], records: list[dict[str, Any]]) -> None:
    missing: list[str] = []
    for index, record in enumerate(records):
        for field in source["required_fields"]:
            if get_nested_value(record, field) is None:
                missing.append(f"record {index}: {field}")

    if missing:
        raise PublicApiResponseError(f"{source['source_name']}: missing required fields: {missing}")


def normalize_records(source: dict[str, Any], records: list[dict[str, Any]], ingestion_mode: str) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for index, record in enumerate(records, start=1):
        row: dict[str, str] = {
            "source_name": source["source_name"],
            "ingestion_mode": ingestion_mode,
            "record_index": str(index),
        }
        for source_field, target_field in source["field_mapping"].items():
            value = get_nested_value(record, source_field)
            row[target_field] = "" if value is None else str(value)
        normalized.append(row)
    return normalized


def write_normalized_csv(path: Path | str, records: list[dict[str, str]]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        file_path.write_text("", encoding="utf-8")
        return

    fieldnames = list(records[0])
    with file_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def run_source(source: dict[str, Any], allow_live: bool = False) -> PublicApiSourceSummary:
    ingestion_mode, payload = fetch_source_payload(source, allow_live=allow_live)
    records = payload_to_records(payload)
    validate_required_fields(source, records)
    normalized = normalize_records(source, records, ingestion_mode)

    write_json(source["raw_landing_path"], payload)
    write_normalized_csv(source["normalized_csv_path"], normalized)

    return PublicApiSourceSummary(
        source_name=source["source_name"],
        ingestion_mode=ingestion_mode,
        raw_records=len(records),
        normalized_records=len(normalized),
        raw_landing_path=source["raw_landing_path"],
        normalized_csv_path=source["normalized_csv_path"],
    )


def run_public_api_integration(
    registry_path: Path | str = DEFAULT_REGISTRY_PATH,
    allow_live: bool = False,
) -> list[PublicApiSourceSummary]:
    registry = load_registry(registry_path)
    return [run_source(source, allow_live=allow_live) for source in registry["sources"]]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V31 public API integration framework.")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY_PATH), help="Path to public API registry JSON.")
    parser.add_argument("--allow-live", action="store_true", help="Allow manual live endpoint execution when source live_enabled is true.")
    args = parser.parse_args()

    summaries = run_public_api_integration(args.registry, allow_live=args.allow_live)
    print("Public API integration SUCCESS")
    for summary in summaries:
        print(
            f"{summary.source_name}: mode={summary.ingestion_mode}, "
            f"raw={summary.raw_records}, normalized={summary.normalized_records}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
