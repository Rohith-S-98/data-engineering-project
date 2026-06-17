import json
from pathlib import Path

from scripts.exceptions import PipelineConfigError


DEFAULT_CONFIG_FILE = Path("config/pipeline/local_config.json")

REQUIRED_KEYS = [
    "environment",
    "dataset_name",
    "watermark_column",
    "raw_data_file",
    "clean_raw_data_file",
    "dirty_raw_data_file",
    "dq_rules_file",
    "bronze_output_path",
    "silver_output_path",
    "gold_output_path",
    "quarantine_output_path",
    "dq_report_file",
    "reltio_payload_output_path",
    "audit_log_file",
    "bronze_schema_contract",
    "silver_schema_contract",
    "schema_validation_audit_file",
    "watermark_store_file",
    "pending_watermark_file",
]


def load_pipeline_config(config_file: str | Path = DEFAULT_CONFIG_FILE) -> dict:
    config_path = Path(config_file)

    if not config_path.exists():
        raise PipelineConfigError(f"Pipeline config file not found: {config_path}")

    with open(config_path, mode="r", encoding="utf-8") as file:
        config = json.load(file)

    missing_keys = [key for key in REQUIRED_KEYS if key not in config]

    if missing_keys:
        raise PipelineConfigError(f"Missing required config keys: {missing_keys}")

    return config
