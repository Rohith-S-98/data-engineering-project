import json
from pathlib import Path


REQUIRED_KEYS = [
    "environment",
    "dataset_name",
    "storage_format",
    "lakehouse_write_strategy",
    "raw_data_file",
    "dq_rules_file",
    "bronze_schema_contract",
    "silver_schema_contract",
    "schema_validation_audit_file",
    "bronze_output_path",
    "silver_output_path",
    "gold_output_path",
    "quarantine_output_path",
    "dq_report_file",
    "reltio_payload_output_path",
    "audit_log_file",
    "watermark_column",
    "watermark_store_file",
    "pending_watermark_file",
    "bronze_merge_keys",
    "silver_merge_keys",
    "quarantine_merge_keys",
    "gold_merge_keys",
    "customer_history_output_path",
    "scd2_business_keys",
    "scd2_tracked_columns",
    "scd2_effective_start_column",
    "observability_enabled",
"observability_output_dir",
"observability_summary_file",
"observability_history_jsonl_file",
"observability_history_csv_file",
]

SUPPORTED_STORAGE_FORMATS = {"parquet", "delta"}
SUPPORTED_WRITE_STRATEGIES = {"overwrite", "merge"}


def _validate_non_empty_string_list(config: dict, key_name: str) -> None:
    values = config[key_name]

    if not isinstance(values, list) or not values:
        raise ValueError(f"{key_name} must be a non-empty list of column names")

    invalid_values = [
        value for value in values
        if not isinstance(value, str) or not value.strip()
    ]

    if invalid_values:
        raise ValueError(f"{key_name} contains invalid values: {invalid_values}")


def _validate_merge_keys(config: dict) -> None:
    merge_key_configs = [
        "bronze_merge_keys",
        "silver_merge_keys",
        "quarantine_merge_keys",
        "gold_merge_keys",
    ]

    for key_config in merge_key_configs:
        _validate_non_empty_string_list(config, key_config)


def _validate_scd2_config(config: dict) -> None:
    _validate_non_empty_string_list(config, "scd2_business_keys")
    _validate_non_empty_string_list(config, "scd2_tracked_columns")

    effective_start_column = config["scd2_effective_start_column"]
    if not isinstance(effective_start_column, str) or not effective_start_column.strip():
        raise ValueError("scd2_effective_start_column must be a non-empty string")

    history_path = config["customer_history_output_path"]
    if not isinstance(history_path, str) or not history_path.strip():
        raise ValueError("customer_history_output_path must be a non-empty string")


def load_pipeline_config(
    config_path: str = "config/pipeline/local_config.json",
) -> dict:
    """
    Load centralized pipeline configuration from JSON file.

    Raises:
        ValueError: If the config file is missing, required keys are absent,
        unsupported storage/write strategy is configured, merge keys are invalid,
        or SCD2 config is invalid.
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise ValueError(f"Pipeline config file not found: {config_path}")

    with config_file.open("r", encoding="utf-8") as file:
        config = json.load(file)

    missing_keys = [key for key in REQUIRED_KEYS if key not in config]

    if missing_keys:
        raise ValueError(f"Missing required pipeline config keys: {missing_keys}")

    storage_format = str(config["storage_format"]).lower()
    write_strategy = str(config["lakehouse_write_strategy"]).lower()

    if storage_format not in SUPPORTED_STORAGE_FORMATS:
        raise ValueError(
            f"Unsupported storage_format: {storage_format}. "
            f"Supported values: {sorted(SUPPORTED_STORAGE_FORMATS)}"
        )

    if write_strategy not in SUPPORTED_WRITE_STRATEGIES:
        raise ValueError(
            f"Unsupported lakehouse_write_strategy: {write_strategy}. "
            f"Supported values: {sorted(SUPPORTED_WRITE_STRATEGIES)}"
        )

    if write_strategy == "merge" and storage_format != "delta":
        raise ValueError(
            "lakehouse_write_strategy='merge' is supported only when "
            "storage_format='delta'"
        )

    config["storage_format"] = storage_format
    config["lakehouse_write_strategy"] = write_strategy

    _validate_merge_keys(config)
    _validate_scd2_config(config)

    return config
