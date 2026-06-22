"""
V13.0.0 - Data Observability + Pipeline Metrics Mart

This module collects production-style observability metrics from the
existing lakehouse pipeline outputs.

It summarizes:
- table row counts
- latest pipeline audit status
- DQ status and quarantined rows
- schema validation status
- watermark current/pending values
- SCD Type 2 history metrics
- JSON, JSONL, and CSV metrics outputs
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


METRICS_VERSION = "v13.0.0"

DEFAULT_OBSERVABILITY_OUTPUT_DIR = "output/observability"
DEFAULT_SUMMARY_FILE = "output/observability/pipeline_metrics_summary.json"
DEFAULT_HISTORY_JSONL_FILE = "output/observability/pipeline_metrics_history.jsonl"
DEFAULT_HISTORY_CSV_FILE = "output/observability/pipeline_metrics_history.csv"

HISTORY_CSV_COLUMNS = [
    "metrics_version",
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
    "current_watermark",
    "pending_watermark",
    "total_history_rows",
    "current_rows",
    "expired_rows",
    "changed_customer_count",
]


def current_utc_iso() -> str:
    """
    Return a stable UTC timestamp for observability output.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json_safely(file_path: str | Path) -> dict[str, Any]:
    """
    Read a JSON file safely.

    Missing file, empty file, or invalid JSON returns an empty dict.
    This is intentional because observability should not fail only
    because one runtime artifact is missing.
    """
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        return {}

    try:
        if path.stat().st_size == 0:
            return {}

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    except (json.JSONDecodeError, OSError):
        return {}


def read_latest_jsonl_record(file_path: str | Path) -> dict[str, Any]:
    """
    Read the latest valid JSON object from a JSONL file.

    The schema validation framework appends one JSON object per line,
    so the latest non-empty valid line represents the latest validation
    event.
    """
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        return {}

    try:
        with path.open("r", encoding="utf-8") as file:
            lines = [line.strip() for line in file if line.strip()]

        for line in reversed(lines):
            try:
                record = json.loads(line)
                if isinstance(record, dict):
                    return record
            except json.JSONDecodeError:
                continue

        return {}

    except OSError:
        return {}


def read_latest_csv_record(file_path: str | Path) -> dict[str, Any]:
    """
    Read the latest row from a CSV file safely.

    The pipeline audit file is append/update based and contains fields like:
    run_id, pipeline_name, environment, start_time, end_time, status,
    error_message.
    """
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        return {}

    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            rows = list(csv.DictReader(file))

        return rows[-1] if rows else {}

    except OSError:
        return {}


def write_json_safely(file_path: str | Path, data: dict[str, Any]) -> None:
    """
    Write JSON with parent directory creation.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, default=str)


def append_jsonl_safely(file_path: str | Path, data: dict[str, Any]) -> None:
    """
    Append one JSON object as one line.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(data, default=str) + "\n")


def calculate_scd2_metrics_from_rows(
    rows: list[dict[str, Any]],
    business_key_columns: list[str] | None = None,
) -> dict[str, int]:
    """
    Calculate SCD Type 2 metrics from normal Python dictionaries.

    This function is useful for unit tests because it does not need Spark.

    changed_customer_count means:
    number of distinct business keys that have at least one expired record.
    """
    business_key_columns = business_key_columns or ["customer_id"]

    total_history_rows = len(rows)
    current_rows = 0
    expired_rows = 0
    changed_keys: set[tuple[Any, ...]] = set()

    for row in rows:
        is_current = row.get("is_current")

        if is_current is True:
            current_rows += 1
            continue

        if is_current is False or row.get("effective_end_date") is not None:
            expired_rows += 1

            if all(key in row for key in business_key_columns):
                changed_keys.add(tuple(row.get(key) for key in business_key_columns))

    return {
        "total_history_rows": total_history_rows,
        "current_rows": current_rows,
        "expired_rows": expired_rows,
        "changed_customer_count": len(changed_keys),
    }


def flatten_metrics_for_csv(metrics: dict[str, Any]) -> dict[str, Any]:
    """
    Convert nested metrics into one flat CSV row.
    """
    pipeline_health = metrics.get("pipeline_health", {})
    row_counts = metrics.get("row_counts", {})
    watermark = metrics.get("watermark", {})
    scd2 = metrics.get("scd2", {})

    return {
        "metrics_version": metrics.get("metrics_version"),
        "metrics_generated_at": metrics.get("metrics_generated_at"),
        "environment": metrics.get("environment"),
        "dataset_name": metrics.get("dataset_name"),
        "latest_pipeline_status": pipeline_health.get("latest_pipeline_status"),
        "schema_validation_status": pipeline_health.get("schema_validation_status"),
        "dq_status": pipeline_health.get("dq_status"),
        "bronze_rows": row_counts.get("bronze_rows"),
        "silver_rows": row_counts.get("silver_rows"),
        "quarantine_rows": row_counts.get("quarantine_rows"),
        "gold_rows": row_counts.get("gold_rows"),
        "customer_history_rows": row_counts.get("customer_history_rows"),
        "current_watermark": watermark.get("current_watermark"),
        "pending_watermark": watermark.get("pending_watermark"),
        "total_history_rows": scd2.get("total_history_rows"),
        "current_rows": scd2.get("current_rows"),
        "expired_rows": scd2.get("expired_rows"),
        "changed_customer_count": scd2.get("changed_customer_count"),
    }


def append_csv_safely(file_path: str | Path, row: dict[str, Any]) -> None:
    """
    Append one flattened metrics row to CSV.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = path.exists() and path.stat().st_size > 0

    with path.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=HISTORY_CSV_COLUMNS)

        if not file_exists:
            writer.writeheader()

        writer.writerow({column: row.get(column) for column in HISTORY_CSV_COLUMNS})


class MetricsCollector:
    """
    Reusable observability metrics collector.

    This class reads pipeline outputs only. It does not mutate Bronze,
    Silver, Gold, Quarantine, Watermark, Audit, or History tables.
    """

    def __init__(
        self,
        spark: SparkSession | None,
        config: dict[str, Any],
    ) -> None:
        self.spark = spark
        self.config = config

        self.environment = config.get("environment", "unknown")
        self.dataset_name = config.get("dataset_name", "unknown_dataset")
        self.storage_format = str(config.get("storage_format", "parquet")).lower()

    def _path_exists(self, table_path: str | Path | None) -> bool:
        if not table_path:
            return False

        path = Path(table_path)
        return path.exists()

    def _detect_read_format(self, table_path: str | Path) -> str:
        """
        Prefer Delta when _delta_log exists.
        Fall back to parquet for local compatibility.

        This protects V13 from failing if an older layer was written as
        parquet while config says storage_format='delta'.
        """
        path = Path(table_path)

        if (path / "_delta_log").exists():
            return "delta"

        if self.storage_format == "delta":
            return "parquet"

        return self.storage_format

    def _read_table_safely(self, table_path: str | Path | None) -> DataFrame | None:
        """
        Read a table path safely.

        Missing path or Spark read failure returns None.
        """
        if self.spark is None or not table_path:
            return None

        path = Path(table_path)

        if not path.exists():
            return None

        try:
            read_format = self._detect_read_format(path)

            if read_format == "delta":
                return self.spark.read.format("delta").load(str(path))

            if read_format == "parquet":
                return self.spark.read.parquet(str(path))

            return self.spark.read.format(read_format).load(str(path))

        except Exception:
            return None

    def count_table_rows(self, table_path: str | Path | None) -> int:
        """
        Count rows safely from a lakehouse table path.

        Missing table or read failure returns 0.
        """
        df = self._read_table_safely(table_path)

        if df is None:
            return 0

        try:
            return int(df.count())
        except Exception:
            return 0

    def collect_table_row_counts(self) -> dict[str, int]:
        """
        Capture row counts from all major V12 lakehouse layers.
        """
        return {
            "bronze_rows": self.count_table_rows(self.config.get("bronze_output_path")),
            "silver_rows": self.count_table_rows(self.config.get("silver_output_path")),
            "quarantine_rows": self.count_table_rows(self.config.get("quarantine_output_path")),
            "gold_rows": self.count_table_rows(self.config.get("gold_output_path")),
            "customer_history_rows": self.count_table_rows(
                self.config.get("customer_history_output_path")
            ),
        }

    def collect_latest_pipeline_audit_metrics(self) -> dict[str, Any]:
        """
        Capture the latest pipeline audit row/status.
        """
        audit_file = self.config.get("audit_log_file")
        latest_audit_row = read_latest_csv_record(audit_file) if audit_file else {}

        if not latest_audit_row:
            return {
                "audit_log_file": audit_file,
                "latest_pipeline_status": "MISSING",
                "latest_run_id": None,
                "latest_pipeline_name": None,
                "latest_start_time": None,
                "latest_end_time": None,
                "latest_error_message": None,
            }

        return {
            "audit_log_file": audit_file,
            "latest_pipeline_status": latest_audit_row.get("status", "UNKNOWN"),
            "latest_run_id": latest_audit_row.get("run_id"),
            "latest_pipeline_name": latest_audit_row.get("pipeline_name"),
            "latest_start_time": latest_audit_row.get("start_time"),
            "latest_end_time": latest_audit_row.get("end_time"),
            "latest_error_message": latest_audit_row.get("error_message"),
        }

    def collect_dq_metrics(self) -> dict[str, Any]:
        """
        Capture DQ status and quarantined row count.

        Primary source:
        - DQ report JSON

        Fallback:
        - quarantine table row count
        """
        dq_report_file = self.config.get("dq_report_file")
        dq_report = read_json_safely(dq_report_file) if dq_report_file else {}

        quarantine_count_from_table = self.count_table_rows(
            self.config.get("quarantine_output_path")
        )

        if not dq_report:
            return {
                "dq_report_file": dq_report_file,
                "dq_status": "MISSING",
                "total_input_rows": 0,
                "valid_rows": 0,
                "quarantined_rows": quarantine_count_from_table,
                "total_rules": 0,
                "failed_rule_count": 0,
            }

        return {
            "dq_report_file": dq_report_file,
            "dq_status": dq_report.get("dq_status", "UNKNOWN"),
            "total_input_rows": int(dq_report.get("total_input_rows", 0) or 0),
            "valid_rows": int(dq_report.get("valid_rows", 0) or 0),
            "quarantined_rows": int(
                dq_report.get("quarantined_rows", quarantine_count_from_table) or 0
            ),
            "total_rules": int(dq_report.get("total_rules", 0) or 0),
            "failed_rule_count": int(dq_report.get("failed_rule_count", 0) or 0),
        }

    def collect_schema_validation_metrics(self) -> dict[str, Any]:
        """
        Capture latest schema validation result from JSONL audit.
        """
        audit_file = self.config.get("schema_validation_audit_file")
        latest_schema_record = read_latest_jsonl_record(audit_file) if audit_file else {}

        if not latest_schema_record:
            return {
                "audit_file": audit_file,
                "status": "MISSING",
                "schema_name": None,
                "layer": None,
                "dataset": None,
                "total_issues": 0,
                "validated_at": None,
            }

        return {
            "audit_file": audit_file,
            "status": latest_schema_record.get("status", "UNKNOWN"),
            "schema_name": latest_schema_record.get("schema_name"),
            "layer": latest_schema_record.get("layer"),
            "dataset": latest_schema_record.get("dataset"),
            "total_issues": int(latest_schema_record.get("total_issues", 0) or 0),
            "validated_at": latest_schema_record.get("validated_at"),
        }

    def collect_watermark_metrics(self) -> dict[str, Any]:
        """
        Capture committed and pending watermark movement.
        """
        watermark_store_file = self.config.get("watermark_store_file")
        pending_watermark_file = self.config.get("pending_watermark_file")

        watermark_store = (
            read_json_safely(watermark_store_file) if watermark_store_file else {}
        )
        pending_store = (
            read_json_safely(pending_watermark_file) if pending_watermark_file else {}
        )

        current_record = watermark_store.get(self.dataset_name, {})
        pending_record = pending_store.get(self.dataset_name, {})

        return {
            "watermark_store_file": watermark_store_file,
            "pending_watermark_file": pending_watermark_file,
            "dataset": self.dataset_name,
            "watermark_column": current_record.get(
                "watermark_column",
                self.config.get("watermark_column"),
            ),
            "current_watermark": current_record.get("last_watermark"),
            "previous_watermark": current_record.get("previous_watermark"),
            "current_status": current_record.get(
                "status",
                "MISSING" if not current_record else "UNKNOWN",
            ),
            "current_updated_at": current_record.get("updated_at"),
            "pending_watermark": pending_record.get("new_watermark"),
            "pending_previous_watermark": pending_record.get("previous_watermark"),
            "pending_status": pending_record.get(
                "status",
                "MISSING" if not pending_record else "UNKNOWN",
            ),
            "pending_staged_at": pending_record.get("staged_at"),
        }

    def collect_scd2_metrics(self) -> dict[str, Any]:
        """
        Capture SCD Type 2 historical dimension metrics.

        Metrics:
        - total history rows
        - current rows
        - expired rows
        - changed customer count
        """
        history_path = self.config.get("customer_history_output_path")
        business_key_columns = self.config.get("scd2_business_keys", ["customer_id"])

        df = self._read_table_safely(history_path)

        if df is None:
            return {
                "history_path": history_path,
                "status": "MISSING",
                "total_history_rows": 0,
                "current_rows": 0,
                "expired_rows": 0,
                "changed_customer_count": 0,
            }

        try:
            total_history_rows = int(df.count())

            if "is_current" in df.columns:
                current_df = df.filter(F.col("is_current").cast("boolean") == F.lit(True))
                expired_df = df.filter(F.col("is_current").cast("boolean") == F.lit(False))

                current_rows = int(current_df.count())
                expired_rows = int(expired_df.count())

            elif "effective_end_date" in df.columns:
                expired_df = df.filter(F.col("effective_end_date").isNotNull())
                expired_rows = int(expired_df.count())
                current_rows = total_history_rows - expired_rows

            else:
                expired_df = None
                current_rows = 0
                expired_rows = 0

            changed_customer_count = 0

            if expired_rows > 0 and expired_df is not None:
                available_keys = [
                    key for key in business_key_columns
                    if key in expired_df.columns
                ]

                if available_keys:
                    changed_customer_count = int(
                        expired_df.select(*available_keys).distinct().count()
                    )

            return {
                "history_path": history_path,
                "status": "AVAILABLE",
                "total_history_rows": total_history_rows,
                "current_rows": current_rows,
                "expired_rows": expired_rows,
                "changed_customer_count": changed_customer_count,
            }

        except Exception:
            return {
                "history_path": history_path,
                "status": "ERROR",
                "total_history_rows": 0,
                "current_rows": 0,
                "expired_rows": 0,
                "changed_customer_count": 0,
            }

    def collect_all_metrics(self) -> dict[str, Any]:
        """
        Build the complete V13 metrics summary.
        """
        row_counts = self.collect_table_row_counts()
        pipeline_audit = self.collect_latest_pipeline_audit_metrics()
        dq_metrics = self.collect_dq_metrics()
        schema_metrics = self.collect_schema_validation_metrics()
        watermark_metrics = self.collect_watermark_metrics()
        scd2_metrics = self.collect_scd2_metrics()

        return {
            "metrics_version": METRICS_VERSION,
            "metrics_generated_at": current_utc_iso(),
            "environment": self.environment,
            "dataset_name": self.dataset_name,
            "pipeline_health": {
                "latest_pipeline_status": pipeline_audit.get("latest_pipeline_status"),
                "schema_validation_status": schema_metrics.get("status"),
                "dq_status": dq_metrics.get("dq_status"),
            },
            "row_counts": row_counts,
            "pipeline_audit": pipeline_audit,
            "data_quality": dq_metrics,
            "schema_validation": schema_metrics,
            "watermark": watermark_metrics,
            "scd2": scd2_metrics,
        }

    def write_metrics_outputs(self, metrics: dict[str, Any]) -> dict[str, str]:
        """
        Write V13 observability metrics to:
        - JSON summary
        - JSONL historical log
        - CSV historical log
        """
        summary_file = self.config.get(
            "observability_summary_file",
            DEFAULT_SUMMARY_FILE,
        )
        history_jsonl_file = self.config.get(
            "observability_history_jsonl_file",
            DEFAULT_HISTORY_JSONL_FILE,
        )
        history_csv_file = self.config.get(
            "observability_history_csv_file",
            DEFAULT_HISTORY_CSV_FILE,
        )

        write_json_safely(summary_file, metrics)
        append_jsonl_safely(history_jsonl_file, metrics)

        flat_row = flatten_metrics_for_csv(metrics)
        append_csv_safely(history_csv_file, flat_row)

        return {
            "summary_file": summary_file,
            "history_jsonl_file": history_jsonl_file,
            "history_csv_file": history_csv_file,
        }