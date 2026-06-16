import json
from pathlib import Path


DEFAULT_CONFIG_FILE = Path("config/pipeline/local_config.json")


def load_pipeline_config(config_file: str | Path = DEFAULT_CONFIG_FILE) -> dict:
    config_path = Path(config_file)

    if not config_path.exists():
        raise FileNotFoundError(f"Pipeline config file not found: {config_path}")

    with open(config_path, mode="r", encoding="utf-8") as file:
        config = json.load(file)

    required_keys = [
        "environment",
        "raw_data_file",
        "dq_rules_file",
        "bronze_output_path",
        "silver_output_path",
        "gold_output_path",
        "quarantine_output_path",
        "dq_report_file",
        "reltio_payload_output_path",
    ]

    missing_keys = [
        key for key in required_keys
        if key not in config
    ]

    if missing_keys:
        raise ValueError(f"Missing required config keys: {missing_keys}")

    return config