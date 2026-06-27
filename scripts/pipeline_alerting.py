from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_ALERT_CONFIG_PATH = "config/alerts/customer_medallion_alerts.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    text = str(value).strip()
    if not text:
        return None

    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _duration_seconds(start_time: str | None, end_time: str | None) -> float | None:
    start_dt = _parse_datetime(start_time)
    end_dt = _parse_datetime(end_time)

    if start_dt is None or end_dt is None:
        return None

    return max((end_dt - start_dt).total_seconds(), 0.0)


def _read_csv_rows(file_path: str) -> list[dict[str, str]]:
    path = Path(file_path)

    if not path.exists():
        return []

    with path.open(mode="r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _write_jsonl(file_path: str, records: list[dict[str, Any]]) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(mode="a", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, default=str) + "\n")


def _write_csv(file_path: str, records: list[dict[str, Any]]) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "alert_id",
        "alert_timestamp",
        "pipeline_name",
        "environment",
        "job_run_id",
        "step_name",
        "alert_type",
        "severity",
        "status",
        "message",
        "metric_name",
        "metric_value",
        "threshold_value",
    ]

    file_exists = path.exists()

    with path.open(mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for record in records:
            writer.writerow({field: record.get(field, "") for field in fieldnames})


def load_alert_config(alert_config_path: str = DEFAULT_ALERT_CONFIG_PATH) -> dict[str, Any]:
    path = Path(alert_config_path)

    if not path.exists():
        raise FileNotFoundError(f"Alert config not found: {alert_config_path}")

    with path.open(mode="r", encoding="utf-8") as file:
        config = json.load(file)

    required_keys = [
        "alerting_enabled",
        "pipeline_name",
        "environment",
        "severity_mapping",
        "sla_thresholds",
        "input_paths",
        "output_paths",
    ]

    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Missing required alert config keys: {missing_keys}")

    return config


def _latest_job_run(job_rows: list[dict[str, str]]) -> dict[str, str] | None:
    if not job_rows:
        return None

    return job_rows[-1]


def _build_alert(
    *,
    pipeline_name: str,
    environment: str,
    job_run_id: str,
    alert_type: str,
    severity: str,
    message: str,
    step_name: str = "",
    metric_name: str = "",
    metric_value: Any = "",
    threshold_value: Any = "",
) -> dict[str, Any]:
    return {
        "alert_id": f"{job_run_id}-{alert_type}-{step_name or 'pipeline'}-{int(datetime.now().timestamp() * 1000)}",
        "alert_timestamp": _utc_now(),
        "pipeline_name": pipeline_name,
        "environment": environment,
        "job_run_id": job_run_id,
        "step_name": step_name,
        "alert_type": alert_type,
        "severity": severity,
        "status": "OPEN",
        "message": message,
        "metric_name": metric_name,
        "metric_value": metric_value,
        "threshold_value": threshold_value,
    }


def _load_observability_summary(file_path: str) -> dict[str, Any]:
    path = Path(file_path)

    if not path.exists():
        return {}

    with path.open(mode="r", encoding="utf-8") as file:
        return json.load(file)


def collect_alert_events(
    alert_config: dict[str, Any],
    job_rows: list[dict[str, str]],
    step_rows: list[dict[str, str]],
    observability_summary: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not alert_config.get("alerting_enabled", True):
        return []

    observability_summary = observability_summary or {}

    pipeline_name = alert_config["pipeline_name"]
    environment = alert_config["environment"]
    severity_mapping = alert_config["severity_mapping"]
    sla_thresholds = alert_config["sla_thresholds"]

    latest_job = _latest_job_run(job_rows)
    if latest_job is None:
        return [
            _build_alert(
                pipeline_name=pipeline_name,
                environment=environment,
                job_run_id="UNKNOWN",
                alert_type="NO_JOB_RUN_DATA",
                severity="WARNING",
                message="No job run data was available for alert evaluation.",
            )
        ]

    job_run_id = latest_job.get("job_run_id", "")
    alerts: list[dict[str, Any]] = []

    job_status = latest_job.get("status", "")
    if job_status not in {"SUCCESS", "SUCCESS_WITH_WARNINGS"}:
        alerts.append(
            _build_alert(
                pipeline_name=pipeline_name,
                environment=environment,
                job_run_id=job_run_id,
                alert_type="PIPELINE_FAILURE",
                severity=severity_mapping.get("pipeline_failure", "CRITICAL"),
                message=(
                    f"Pipeline job_run_id={job_run_id} completed with status "
                    f"{job_status}."
                ),
                metric_name="job_status",
                metric_value=job_status,
                threshold_value="SUCCESS",
            )
        )

    max_pipeline_duration = sla_thresholds.get("max_pipeline_duration_seconds")
    pipeline_duration = _duration_seconds(
        latest_job.get("start_time"),
        latest_job.get("end_time"),
    )

    if (
        pipeline_duration is not None
        and max_pipeline_duration is not None
        and pipeline_duration > float(max_pipeline_duration)
    ):
        alerts.append(
            _build_alert(
                pipeline_name=pipeline_name,
                environment=environment,
                job_run_id=job_run_id,
                alert_type="PIPELINE_SLA_BREACH",
                severity=severity_mapping.get("pipeline_sla_breach", "WARNING"),
                message=(
                    f"Pipeline duration {pipeline_duration:.2f}s breached SLA "
                    f"threshold {max_pipeline_duration}s."
                ),
                metric_name="pipeline_duration_seconds",
                metric_value=round(pipeline_duration, 2),
                threshold_value=max_pipeline_duration,
            )
        )

    job_step_rows = [
        row for row in step_rows if row.get("job_run_id") == job_run_id
    ]

    max_step_duration = sla_thresholds.get("max_step_duration_seconds")

    for step in job_step_rows:
        step_name = step.get("step_name", "")
        step_status = step.get("status", "")
        is_critical = str(step.get("critical", "True")).lower() == "true"

        if step_status not in {"SUCCESS", "SKIPPED", "DRY_RUN"}:
            alert_type = (
                "CRITICAL_STEP_FAILURE"
                if is_critical
                else "OPTIONAL_STEP_FAILURE"
            )
            severity_key = (
                "critical_step_failure"
                if is_critical
                else "optional_step_failure"
            )

            alerts.append(
                _build_alert(
                    pipeline_name=pipeline_name,
                    environment=environment,
                    job_run_id=job_run_id,
                    step_name=step_name,
                    alert_type=alert_type,
                    severity=severity_mapping.get(severity_key, "WARNING"),
                    message=(
                        f"Step '{step_name}' completed with status "
                        f"{step_status}."
                    ),
                    metric_name="step_status",
                    metric_value=step_status,
                    threshold_value="SUCCESS",
                )
            )

        step_duration = _duration_seconds(
            step.get("start_time"),
            step.get("end_time"),
        )

        if (
            step_duration is not None
            and max_step_duration is not None
            and step_duration > float(max_step_duration)
        ):
            alerts.append(
                _build_alert(
                    pipeline_name=pipeline_name,
                    environment=environment,
                    job_run_id=job_run_id,
                    step_name=step_name,
                    alert_type="STEP_SLA_BREACH",
                    severity=severity_mapping.get("step_sla_breach", "WARNING"),
                    message=(
                        f"Step '{step_name}' duration {step_duration:.2f}s "
                        f"breached SLA threshold {max_step_duration}s."
                    ),
                    metric_name="step_duration_seconds",
                    metric_value=round(step_duration, 2),
                    threshold_value=max_step_duration,
                )
            )

    schema_status = str(
        observability_summary.get("schema_validation_status", "")
    ).upper()
    if schema_status and schema_status not in {"PASSED", "SUCCESS"}:
        alerts.append(
            _build_alert(
                pipeline_name=pipeline_name,
                environment=environment,
                job_run_id=job_run_id,
                alert_type="SCHEMA_FAILURE",
                severity=severity_mapping.get("schema_failure", "CRITICAL"),
                message=f"Schema validation status is {schema_status}.",
                metric_name="schema_validation_status",
                metric_value=schema_status,
                threshold_value="PASSED",
            )
        )

    dq_status = str(observability_summary.get("dq_status", "")).upper()
    if dq_status and dq_status != "SUCCESS":
        alerts.append(
            _build_alert(
                pipeline_name=pipeline_name,
                environment=environment,
                job_run_id=job_run_id,
                alert_type="DQ_FAILURE",
                severity=severity_mapping.get("dq_failure", "CRITICAL"),
                message=f"DQ status is {dq_status}.",
                metric_name="dq_status",
                metric_value=dq_status,
                threshold_value="SUCCESS",
            )
        )

    max_quarantine_rows = sla_thresholds.get("max_quarantine_rows")
    quarantine_rows = observability_summary.get("quarantine_rows")

    if (
        quarantine_rows is not None
        and max_quarantine_rows is not None
        and int(quarantine_rows) > int(max_quarantine_rows)
    ):
        alerts.append(
            _build_alert(
                pipeline_name=pipeline_name,
                environment=environment,
                job_run_id=job_run_id,
                alert_type="QUARANTINE_THRESHOLD_BREACH",
                severity=severity_mapping.get(
                    "quarantine_threshold_breach",
                    "WARNING",
                ),
                message=(
                    f"Quarantine rows {quarantine_rows} breached threshold "
                    f"{max_quarantine_rows}."
                ),
                metric_name="quarantine_rows",
                metric_value=quarantine_rows,
                threshold_value=max_quarantine_rows,
            )
        )

    return alerts


def _write_notification_summary(
    file_path: str,
    alerts: list[dict[str, Any]],
    pipeline_name: str,
    environment: str,
) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    critical_count = sum(1 for alert in alerts if alert["severity"] == "CRITICAL")
    warning_count = sum(1 for alert in alerts if alert["severity"] == "WARNING")

    lines = [
        "Pipeline Alert Notification Summary",
        "=" * 45,
        f"Generated At : {_utc_now()}",
        f"Pipeline     : {pipeline_name}",
        f"Environment  : {environment}",
        f"Alert Count  : {len(alerts)}",
        f"Critical     : {critical_count}",
        f"Warning      : {warning_count}",
        "",
    ]

    if not alerts:
        lines.append("No alerts generated for the latest pipeline run.")
    else:
        lines.append("Alerts:")
        for alert in alerts:
            lines.append(
                f"- [{alert['severity']}] {alert['alert_type']} "
                f"{alert.get('step_name') or 'pipeline'}: {alert['message']}"
            )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_pipeline_alerting(
    alert_config_path: str = DEFAULT_ALERT_CONFIG_PATH,
) -> str:
    print("=" * 70)
    print("Starting V16 Pipeline Alerting and SLA Monitoring")
    print("=" * 70)

    alert_config = load_alert_config(alert_config_path)

    input_paths = alert_config["input_paths"]
    output_paths = alert_config["output_paths"]

    job_rows = _read_csv_rows(input_paths["job_run_log_file"])
    step_rows = _read_csv_rows(input_paths["step_run_log_file"])
    observability_summary = _load_observability_summary(
        input_paths["observability_summary_file"]
    )

    alerts = collect_alert_events(
        alert_config=alert_config,
        job_rows=job_rows,
        step_rows=step_rows,
        observability_summary=observability_summary,
    )

    if alerts:
        _write_jsonl(output_paths["alert_events_jsonl"], alerts)
        _write_csv(output_paths["alert_events_csv"], alerts)

    _write_notification_summary(
        file_path=output_paths["notification_summary_file"],
        alerts=alerts,
        pipeline_name=alert_config["pipeline_name"],
        environment=alert_config["environment"],
    )

    print()
    print("V16 Alerting Summary")
    print(f"Alert count : {len(alerts)}")
    print(f"Critical    : {sum(1 for alert in alerts if alert['severity'] == 'CRITICAL')}")
    print(f"Warning     : {sum(1 for alert in alerts if alert['severity'] == 'WARNING')}")
    print(f"Summary file: {output_paths['notification_summary_file']}")

    if alerts:
        print("Alert events generated:")
        for alert in alerts:
            print(
                f"- [{alert['severity']}] {alert['alert_type']}: "
                f"{alert['message']}"
            )
    else:
        print("No alerts generated for the latest pipeline run.")

    print("=" * 70)
    print("V16 alerting completed successfully")
    print("=" * 70)

    return "SUCCESS"


if __name__ == "__main__":
    run_pipeline_alerting()
