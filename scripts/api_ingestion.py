from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATH = Path("config/api/customer_api_ingestion_config.json")


@dataclass(frozen=True)
class ApiIngestionSummary:
    source_name: str
    pages_read: int
    records_written: int
    target_csv_path: str


class ApiIngestionConfigError(ValueError):
    """Raised when API ingestion configuration is invalid."""


class ApiIngestionSourceError(FileNotFoundError):
    """Raised when mock API source payload is unavailable."""


REQUIRED_CONFIG_KEYS = {
    "source_name",
    "enabled",
    "base_url",
    "http_method",
    "auth_type",
    "pagination",
    "mock_response_path",
    "target_csv_path",
    "target_columns",
    "field_mapping",
    "default_values",
}


def load_json(path: Path | str) -> dict[str, Any]:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_api_config(config: dict[str, Any]) -> None:
    missing_keys = sorted(REQUIRED_CONFIG_KEYS - set(config))
    if missing_keys:
        raise ApiIngestionConfigError(f"Missing API config keys: {missing_keys}")

    if not isinstance(config["target_columns"], list) or not config["target_columns"]:
        raise ApiIngestionConfigError("target_columns must be a non-empty list")

    if not isinstance(config["field_mapping"], dict) or not config["field_mapping"]:
        raise ApiIngestionConfigError("field_mapping must be a non-empty object")

    pagination = config["pagination"]
    if not isinstance(pagination, dict):
        raise ApiIngestionConfigError("pagination must be an object")

    max_pages = pagination.get("max_pages")
    if not isinstance(max_pages, int) or max_pages <= 0:
        raise ApiIngestionConfigError("pagination.max_pages must be a positive integer")


def load_api_config(config_path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    config = load_json(config_path)
    validate_api_config(config)
    return config


def load_mock_api_pages(mock_response_path: Path | str) -> list[dict[str, Any]]:
    file_path = Path(mock_response_path)
    if not file_path.exists():
        raise ApiIngestionSourceError(f"Mock API response file not found: {file_path}")

    payload = load_json(file_path)
    pages = payload.get("pages")
    if not isinstance(pages, list):
        raise ApiIngestionSourceError("Mock API response must contain a pages array")

    return sorted(pages, key=lambda page: page.get("page_number", 0))


def map_api_record(record: dict[str, Any], config: dict[str, Any]) -> dict[str, str]:
    mapped: dict[str, str] = {}
    field_mapping = config["field_mapping"]
    default_values = config["default_values"]

    for target_column in config["target_columns"]:
        source_field = next(
            (source for source, target in field_mapping.items() if target == target_column),
            None,
        )
        value = record.get(source_field, default_values.get(target_column, "")) if source_field else default_values.get(target_column, "")
        mapped[target_column] = "" if value is None else str(value)

    return mapped


def extract_api_records(config: dict[str, Any]) -> tuple[int, list[dict[str, str]]]:
    if not config.get("enabled", False):
        return 0, []

    pages = load_mock_api_pages(config["mock_response_path"])
    max_pages = config["pagination"]["max_pages"]
    selected_pages = pages[:max_pages]

    records: list[dict[str, str]] = []
    for page in selected_pages:
        page_records = page.get("records", [])
        if not isinstance(page_records, list):
            raise ApiIngestionSourceError("Each API page must contain a records array")
        for record in page_records:
            records.append(map_api_record(record, config))

    return len(selected_pages), records


def write_records_to_csv(records: list[dict[str, str]], target_columns: list[str], target_path: Path | str) -> None:
    file_path = Path(target_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=target_columns)
        writer.writeheader()
        writer.writerows(records)


def run_api_ingestion(config_path: Path | str = DEFAULT_CONFIG_PATH) -> ApiIngestionSummary:
    config = load_api_config(config_path)
    pages_read, records = extract_api_records(config)
    write_records_to_csv(records, config["target_columns"], config["target_csv_path"])

    summary = ApiIngestionSummary(
        source_name=config["source_name"],
        pages_read=pages_read,
        records_written=len(records),
        target_csv_path=config["target_csv_path"],
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V20 API ingestion framework.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to API ingestion config JSON.")
    args = parser.parse_args()

    summary = run_api_ingestion(args.config)
    print("API ingestion SUCCESS")
    print(f"Source name    : {summary.source_name}")
    print(f"Pages read     : {summary.pages_read}")
    print(f"Records written: {summary.records_written}")
    print(f"Target CSV     : {summary.target_csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
