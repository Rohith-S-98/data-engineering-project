from __future__ import annotations

import json
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any

DEFAULT_RUNTIME_PARAMETER_CONFIG_PATH = "config/runtime/default_runtime_parameters.json"
DEFAULT_RUNTIME_PARAMETER_OUTPUT_DIR = "output/runtime_parameters"
ALLOWED_RUN_MODES = {"manual", "scheduled", "backfill"}


def _parse_iso_date(value: str | None, field_name: str) -> str | None:
    if value in {None, ""}:
        return None

    try:
        date.fromisoformat(str(value))
    except ValueError as error:
        raise ValueError(
            f"{field_name} must be in YYYY-MM-DD format. Received: {value}"
        ) from error

    return str(value)


def load_default_runtime_parameters(
    config_path: str = DEFAULT_RUNTIME_PARAMETER_CONFIG_PATH,
) -> dict[str, Any]:
    path = Path(config_path)

    if not path.exists():
        return {
            "run_mode": "manual",
            "run_date": None,
            "dry_run": False,
            "backfill_start_date": None,
            "backfill_end_date": None,
            "triggered_by": "local_cli",
            "allow_optional_step_failure": True,
        }

    with path.open(mode="r", encoding="utf-8") as file:
        parameters = json.load(file)

    return parameters


def merge_runtime_parameters(*parameter_sources: dict[str, Any] | None) -> dict[str, Any]:
    merged: dict[str, Any] = {}

    for source in parameter_sources:
        if source:
            merged.update(deepcopy(source))

    return merged


def validate_runtime_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
    validated = deepcopy(parameters)

    run_mode = str(validated.get("run_mode", "manual")).lower()
    if run_mode not in ALLOWED_RUN_MODES:
        raise ValueError(
            f"run_mode must be one of {sorted(ALLOWED_RUN_MODES)}. "
            f"Received: {run_mode}"
        )

    validated["run_mode"] = run_mode
    validated["run_date"] = _parse_iso_date(validated.get("run_date"), "run_date")
    validated["backfill_start_date"] = _parse_iso_date(
        validated.get("backfill_start_date"),
        "backfill_start_date",
    )
    validated["backfill_end_date"] = _parse_iso_date(
        validated.get("backfill_end_date"),
        "backfill_end_date",
    )
    validated["dry_run"] = bool(validated.get("dry_run", False))
    validated["allow_optional_step_failure"] = bool(
        validated.get("allow_optional_step_failure", True)
    )
    validated["triggered_by"] = str(validated.get("triggered_by", "local_cli"))

    if run_mode == "backfill":
        if not validated["backfill_start_date"] or not validated["backfill_end_date"]:
            raise ValueError(
                "backfill mode requires both backfill_start_date and backfill_end_date"
            )

        if validated["backfill_start_date"] > validated["backfill_end_date"]:
            raise ValueError(
                "backfill_start_date cannot be greater than backfill_end_date"
            )

    return validated


def save_runtime_parameters_snapshot(
    job_run_id: str,
    parameters: dict[str, Any],
    output_dir: str = DEFAULT_RUNTIME_PARAMETER_OUTPUT_DIR,
) -> str:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    output_file = path / f"runtime_parameters_{job_run_id}.json"
    output_file.write_text(
        json.dumps(parameters, indent=4, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return str(output_file)
