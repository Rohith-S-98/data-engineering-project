import json
from pathlib import Path


REQUIRED_KEYS = [
    "environment",
    "dataset_name",

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
]


def load_pipeline_config(
    config_path: str = "config/pipeline/local_config.json",
) -> dict:
    """
    Load centralized pipeline configuration from JSON file.

    Raises:
        ValueError: If the config file is missing or required keys are absent.
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

    return config