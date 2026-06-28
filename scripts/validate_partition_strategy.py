from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_STRATEGY_PATH = Path("config/partitioning/customer_partition_strategy.json")
REQUIRED_DATASETS = {
    "bronze_customers",
    "silver_customers",
    "customer_history",
    "gold_customer_canonical",
    "pipeline_observability_metrics",
}
REQUIRED_TABLE_KEYS = {
    "dataset",
    "layer",
    "expected_volume",
    "partition_columns",
    "clustering_columns",
    "target_file_size_mb",
    "retention_days",
    "maintenance_actions",
}
SUPPORTED_LAYERS = {"bronze", "silver", "history", "gold", "observability"}
SUPPORTED_VOLUME_LEVELS = {"small", "medium", "large"}
MIN_TARGET_FILE_SIZE_MB = 32
MAX_TARGET_FILE_SIZE_MB = 1024
MIN_RETENTION_DAYS = 7
MAX_PARTITION_COLUMNS = 3


class PartitionStrategyValidationError(ValueError):
    """Raised when V28 partition strategy metadata is invalid."""


def load_partition_strategy(path: Path = DEFAULT_STRATEGY_PATH) -> dict[str, Any]:
    if not path.exists():
        raise PartitionStrategyValidationError(f"partition strategy file not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PartitionStrategyValidationError(f"invalid JSON in partition strategy file: {exc}") from exc

    if not isinstance(data, dict):
        raise PartitionStrategyValidationError("partition strategy must be a JSON object")
    return data


def validate_string_list(value: Any, field_name: str, dataset: str) -> list[str]:
    issues: list[str] = []
    if not isinstance(value, list) or not value:
        issues.append(f"{dataset}: {field_name} must be a non-empty list")
        return issues

    for item in value:
        if not isinstance(item, str) or not item.strip():
            issues.append(f"{dataset}: {field_name} must contain only non-empty strings")
    return issues


def validate_table_strategy(table: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    dataset = str(table.get("dataset", "<missing-dataset>"))

    missing_keys = REQUIRED_TABLE_KEYS - set(table)
    for key in sorted(missing_keys):
        issues.append(f"{dataset}: missing required key {key}")

    layer = table.get("layer")
    if layer not in SUPPORTED_LAYERS:
        issues.append(f"{dataset}: unsupported layer {layer}")

    expected_volume = table.get("expected_volume")
    if expected_volume not in SUPPORTED_VOLUME_LEVELS:
        issues.append(f"{dataset}: unsupported expected_volume {expected_volume}")

    partition_columns = table.get("partition_columns")
    issues.extend(validate_string_list(partition_columns, "partition_columns", dataset))
    if isinstance(partition_columns, list) and len(partition_columns) > MAX_PARTITION_COLUMNS:
        issues.append(f"{dataset}: partition_columns must not exceed {MAX_PARTITION_COLUMNS}")

    clustering_columns = table.get("clustering_columns")
    issues.extend(validate_string_list(clustering_columns, "clustering_columns", dataset))

    target_file_size_mb = table.get("target_file_size_mb")
    if not isinstance(target_file_size_mb, int):
        issues.append(f"{dataset}: target_file_size_mb must be an integer")
    elif not MIN_TARGET_FILE_SIZE_MB <= target_file_size_mb <= MAX_TARGET_FILE_SIZE_MB:
        issues.append(
            f"{dataset}: target_file_size_mb must be between "
            f"{MIN_TARGET_FILE_SIZE_MB} and {MAX_TARGET_FILE_SIZE_MB}"
        )

    retention_days = table.get("retention_days")
    if not isinstance(retention_days, int):
        issues.append(f"{dataset}: retention_days must be an integer")
    elif retention_days < MIN_RETENTION_DAYS:
        issues.append(f"{dataset}: retention_days must be at least {MIN_RETENTION_DAYS}")

    maintenance_actions = table.get("maintenance_actions")
    issues.extend(validate_string_list(maintenance_actions, "maintenance_actions", dataset))

    if dataset == "customer_history" and "effective_year" not in (partition_columns or []):
        issues.append("customer_history: must partition by effective_year")

    if dataset == "pipeline_observability_metrics" and target_file_size_mb and target_file_size_mb > 128:
        issues.append("pipeline_observability_metrics: target_file_size_mb should stay small for dashboard refresh")

    return issues


def validate_partition_strategy(path: Path = DEFAULT_STRATEGY_PATH) -> list[str]:
    issues: list[str] = []
    strategy = load_partition_strategy(path)

    if strategy.get("version") != "v28.0.0":
        issues.append("partition strategy version must be v28.0.0")

    tables = strategy.get("tables")
    if not isinstance(tables, list) or not tables:
        issues.append("partition strategy must define a non-empty tables list")
        return issues

    datasets = set()
    for table in tables:
        if not isinstance(table, dict):
            issues.append("each partition strategy table entry must be an object")
            continue
        dataset = table.get("dataset")
        if isinstance(dataset, str):
            if dataset in datasets:
                issues.append(f"duplicate dataset in partition strategy: {dataset}")
            datasets.add(dataset)
        issues.extend(validate_table_strategy(table))

    missing_datasets = REQUIRED_DATASETS - datasets
    for dataset in sorted(missing_datasets):
        issues.append(f"missing required dataset strategy: {dataset}")

    return issues


def assert_valid_partition_strategy(path: Path = DEFAULT_STRATEGY_PATH) -> None:
    issues = validate_partition_strategy(path)
    if issues:
        raise PartitionStrategyValidationError("; ".join(issues))


def main() -> int:
    issues = validate_partition_strategy()
    if issues:
        print("Partition strategy validation FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    strategy = load_partition_strategy()
    print("Partition strategy validation SUCCESS")
    print(f"Validated table strategies: {len(strategy['tables'])}")
    print(f"Validated strategy file: {DEFAULT_STRATEGY_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
