"""
V13.0.0 - Data Observability + Pipeline Metrics Mart Runner

Run command:
    python -m scripts.pipeline_observability

This script collects observability metrics from the existing V12 lakehouse
pipeline outputs and writes:
- JSON summary
- JSONL historical metrics log
- CSV historical metrics log
"""

from __future__ import annotations

import sys
from typing import Any

from scripts.metrics_collector import MetricsCollector
from scripts.pipeline_config import load_pipeline_config
from scripts.spark_session import get_spark_session


def _print_metric_line(label: str, value: Any) -> None:
    """
    Print one clean metric line.
    """
    print(f"{label}: {value}")


def print_observability_summary(
    metrics: dict[str, Any],
    output_files: dict[str, str],
) -> None:
    """
    Print a readable terminal summary after metrics collection.
    """
    pipeline_health = metrics.get("pipeline_health", {})
    row_counts = metrics.get("row_counts", {})
    watermark = metrics.get("watermark", {})
    scd2 = metrics.get("scd2", {})

    print("\n" + "=" * 70)
    print("V13 Data Observability Metrics Summary")
    print("=" * 70)

    print("\nPipeline Health")
    _print_metric_line(
        "Latest pipeline status",
        pipeline_health.get("latest_pipeline_status"),
    )
    _print_metric_line(
        "Schema validation status",
        pipeline_health.get("schema_validation_status"),
    )
    _print_metric_line(
        "DQ status",
        pipeline_health.get("dq_status"),
    )

    print("\nRow Counts")
    _print_metric_line("Bronze rows", row_counts.get("bronze_rows"))
    _print_metric_line("Silver rows", row_counts.get("silver_rows"))
    _print_metric_line("Quarantine rows", row_counts.get("quarantine_rows"))
    _print_metric_line("Gold rows", row_counts.get("gold_rows"))
    _print_metric_line(
        "Customer history rows",
        row_counts.get("customer_history_rows"),
    )

    print("\nWatermark")
    _print_metric_line("Current watermark", watermark.get("current_watermark"))
    _print_metric_line("Pending watermark", watermark.get("pending_watermark"))

    print("\nSCD Type 2 Metrics")
    _print_metric_line("Total history rows", scd2.get("total_history_rows"))
    _print_metric_line("Current rows", scd2.get("current_rows"))
    _print_metric_line("Expired rows", scd2.get("expired_rows"))
    _print_metric_line(
        "Changed customer count",
        scd2.get("changed_customer_count"),
    )

    print("\nOutput Files")
    _print_metric_line("Summary JSON", output_files.get("summary_file"))
    _print_metric_line("History JSONL", output_files.get("history_jsonl_file"))
    _print_metric_line("History CSV", output_files.get("history_csv_file"))

    print("=" * 70)


def run_pipeline_observability() -> str:
    """
    Execute V13 metrics collection.

    Returns:
        SUCCESS if metrics are collected and written successfully.
        FAILED if an unexpected error occurs.
    """
    print("=" * 70)
    print("Starting V13 Data Observability Metrics Collection")
    print("=" * 70)

    config = load_pipeline_config()

    if not config.get("observability_enabled", True):
        print("Observability is disabled in pipeline config.")
        return "SKIPPED"

    spark = get_spark_session("V13DataObservabilityMetrics")

    try:
        collector = MetricsCollector(
            spark=spark,
            config=config,
        )

        metrics = collector.collect_all_metrics()
        output_files = collector.write_metrics_outputs(metrics)

        print_observability_summary(
            metrics=metrics,
            output_files=output_files,
        )

        print("\n" + "=" * 70)
        print("V13 observability collection completed successfully")
        print("=" * 70)

        return "SUCCESS"

    except Exception as error:
        print("\n" + "=" * 70)
        print("V13 observability collection failed")
        print(f"Error Type: {type(error).__name__}")
        print(f"Error Message: {error}")
        print("=" * 70)

        return "FAILED"

    finally:
        spark.stop()


if __name__ == "__main__":
    final_status = run_pipeline_observability()
    sys.exit(0 if final_status in {"SUCCESS", "SKIPPED"} else 1)