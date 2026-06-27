from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_SUMMARY_FILE = Path("output/observability/pipeline_metrics_summary.json")
DEFAULT_POWERBI_OUTPUT_DIR = Path("output/observability/powerbi")

KPI_COLUMNS = [
    "snapshot_generated_at",
    "metrics_generated_at",
    "environment",
    "dataset_name",
    "latest_pipeline_status",
    "schema_validation_status",
    "dq_status",
    "bronze_rows",
    "silver_rows",
    "quarantine_rows",
    "gold_rows",
    "customer_history_rows",
    "quarantine_rate_pct",
    "dq_failure_rate_pct",
    "current_watermark",
    "pending_watermark",
    "total_history_rows",
    "current_rows",
    "expired_rows",
    "changed_customer_count",
]

DQ_COLUMNS = [
    "snapshot_generated_at",
    "metrics_generated_at",
    "environment",
    "dataset_name",
    "dq_status",
    "total_input_rows",
    "valid_rows",
    "quarantined_rows",
    "total_rules",
    "failed_rule_count",
    "dq_pass_rate_pct",
    "dq_failure_rate_pct",
]

LAYER_ROW_COUNT_COLUMNS = [
    "snapshot_generated_at",
    "metrics_generated_at",
    "environment",
    "dataset_name",
    "layer_name",
    "row_count",
]


def current_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def safe_int(value: Any) -> int:
    try:
        if value is None or value == "":
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0


def pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def read_json(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"metrics summary file not found: {file_path}")
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("metrics summary must be a JSON object")
    return data


def write_csv(path: str | Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in columns})


def build_kpi_snapshot(metrics: dict[str, Any]) -> dict[str, Any]:
    generated_at = current_utc_iso()
    pipeline_health = metrics.get("pipeline_health", {})
    row_counts = metrics.get("row_counts", {})
    data_quality = metrics.get("data_quality", {})
    watermark = metrics.get("watermark", {})
    scd2 = metrics.get("scd2", {})

    total_input_rows = safe_int(data_quality.get("total_input_rows"))
    quarantined_rows = safe_int(data_quality.get("quarantined_rows"))
    failed_rule_count = safe_int(data_quality.get("failed_rule_count"))
    total_rules = safe_int(data_quality.get("total_rules"))

    return {
        "snapshot_generated_at": generated_at,
        "metrics_generated_at": metrics.get("metrics_generated_at"),
        "environment": metrics.get("environment"),
        "dataset_name": metrics.get("dataset_name"),
        "latest_pipeline_status": pipeline_health.get("latest_pipeline_status"),
        "schema_validation_status": pipeline_health.get("schema_validation_status"),
        "dq_status": pipeline_health.get("dq_status"),
        "bronze_rows": safe_int(row_counts.get("bronze_rows")),
        "silver_rows": safe_int(row_counts.get("silver_rows")),
        "quarantine_rows": safe_int(row_counts.get("quarantine_rows")),
        "gold_rows": safe_int(row_counts.get("gold_rows")),
        "customer_history_rows": safe_int(row_counts.get("customer_history_rows")),
        "quarantine_rate_pct": pct(quarantined_rows, total_input_rows),
        "dq_failure_rate_pct": pct(failed_rule_count, total_rules),
        "current_watermark": watermark.get("current_watermark"),
        "pending_watermark": watermark.get("pending_watermark"),
        "total_history_rows": safe_int(scd2.get("total_history_rows")),
        "current_rows": safe_int(scd2.get("current_rows")),
        "expired_rows": safe_int(scd2.get("expired_rows")),
        "changed_customer_count": safe_int(scd2.get("changed_customer_count")),
    }


def build_dq_snapshot(metrics: dict[str, Any]) -> dict[str, Any]:
    generated_at = current_utc_iso()
    data_quality = metrics.get("data_quality", {})
    total_input_rows = safe_int(data_quality.get("total_input_rows"))
    valid_rows = safe_int(data_quality.get("valid_rows"))
    quarantined_rows = safe_int(data_quality.get("quarantined_rows"))
    total_rules = safe_int(data_quality.get("total_rules"))
    failed_rule_count = safe_int(data_quality.get("failed_rule_count"))

    return {
        "snapshot_generated_at": generated_at,
        "metrics_generated_at": metrics.get("metrics_generated_at"),
        "environment": metrics.get("environment"),
        "dataset_name": metrics.get("dataset_name"),
        "dq_status": data_quality.get("dq_status"),
        "total_input_rows": total_input_rows,
        "valid_rows": valid_rows,
        "quarantined_rows": quarantined_rows,
        "total_rules": total_rules,
        "failed_rule_count": failed_rule_count,
        "dq_pass_rate_pct": pct(valid_rows, total_input_rows),
        "dq_failure_rate_pct": pct(failed_rule_count, total_rules),
    }


def build_layer_row_count_records(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    generated_at = current_utc_iso()
    row_counts = metrics.get("row_counts", {})
    common = {
        "snapshot_generated_at": generated_at,
        "metrics_generated_at": metrics.get("metrics_generated_at"),
        "environment": metrics.get("environment"),
        "dataset_name": metrics.get("dataset_name"),
    }
    layers = {
        "bronze": "bronze_rows",
        "silver": "silver_rows",
        "quarantine": "quarantine_rows",
        "gold": "gold_rows",
        "customer_history": "customer_history_rows",
    }
    return [
        {**common, "layer_name": layer_name, "row_count": safe_int(row_counts.get(source_column))}
        for layer_name, source_column in layers.items()
    ]


def export_powerbi_observability(
    summary_file: str | Path = DEFAULT_SUMMARY_FILE,
    output_dir: str | Path = DEFAULT_POWERBI_OUTPUT_DIR,
) -> dict[str, str]:
    metrics = read_json(summary_file)
    output_path = Path(output_dir)

    kpi_file = output_path / "dashboard_kpi_snapshot.csv"
    dq_file = output_path / "dashboard_data_quality_snapshot.csv"
    layer_file = output_path / "dashboard_layer_row_counts.csv"

    write_csv(kpi_file, KPI_COLUMNS, [build_kpi_snapshot(metrics)])
    write_csv(dq_file, DQ_COLUMNS, [build_dq_snapshot(metrics)])
    write_csv(layer_file, LAYER_ROW_COUNT_COLUMNS, build_layer_row_count_records(metrics))

    return {
        "dashboard_kpi_snapshot": str(kpi_file),
        "dashboard_data_quality_snapshot": str(dq_file),
        "dashboard_layer_row_counts": str(layer_file),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Power BI-ready observability CSV files.")
    parser.add_argument("--summary-file", default=str(DEFAULT_SUMMARY_FILE))
    parser.add_argument("--output-dir", default=str(DEFAULT_POWERBI_OUTPUT_DIR))
    args = parser.parse_args()

    try:
        output_files = export_powerbi_observability(args.summary_file, args.output_dir)
    except Exception as error:
        print("Power BI observability export FAILED")
        print(f"Error Type: {type(error).__name__}")
        print(f"Error Message: {error}")
        return 1

    print("Power BI observability export SUCCESS")
    for label, file_path in output_files.items():
        print(f"{label}: {file_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
