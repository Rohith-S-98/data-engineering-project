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
]


SUPPORTED_STORAGE_FORMATS = {"parquet", "delta"}
SUPPORTED_WRITE_STRATEGIES = {"overwrite", "merge"}


def _validate_merge_keys(config: dict) -> None:
    merge_key_configs = [
        "bronze_merge_keys",
        "silver_merge_keys",
        "quarantine_merge_keys",
        "gold_merge_keys",
    ]

    for key_config in merge_key_configs:
        merge_keys = config[key_config]

        if not isinstance(merge_keys, list) or not merge_keys:
            raise ValueError(
                f"{key_config} must be a non-empty list of column names"
            )

        invalid_keys = [
            key
            for key in merge_keys
            if not isinstance(key, str) or not key.strip()
        ]

        if invalid_keys:
            raise ValueError(
                f"{key_config} contains invalid merge keys: {invalid_keys}"
            )


def load_pipeline_config(
    config_path: str = "config/pipeline/local_config.json",
) -> dict:
    """
    Load centralized pipeline configuration from JSON file.

    Raises:
        ValueError: If the config file is missing, required keys are absent,
        unsupported storage/write strategy is configured, or merge keys are invalid.
    """

    config_file = Path(config_path)

    if not config_file.exists():
        raise ValueError(f"Pipeline config file not found: {config_path}")

    with config_file.open("r", encoding="utf-8") as file:
        config = json.load(file)

    missing_keys = [key for key in REQUIRED_KEYS if key not in config]

    if missing_keys:
        raise ValueError(
            f"Missing required pipeline config keys: {missing_keys}"
        )

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

    return config