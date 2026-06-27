from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

DASHBOARD_SCHEMA_PATH = Path("dashboards/powerbi/observability_dashboard_schema.json")
EXPORTER_SCRIPT_PATH = Path("scripts/powerbi_observability_exporter.py")
DOCUMENTATION_PATH = Path("docs/v25_powerbi_observability_dashboard.md")
README_PATH = Path("dashboards/powerbi/README.md")

REQUIRED_FACT_TABLES = {
    "dashboard_kpi_snapshot",
    "dashboard_data_quality_snapshot",
    "dashboard_layer_row_counts",
}

REQUIRED_VISUALS = {
    "Pipeline status card",
    "DQ status card",
    "Layer row count bar chart",
    "Quarantine rate KPI",
    "DQ failure rate KPI",
}


class PowerBiDashboardValidationError(ValueError):
    """Raised when Power BI dashboard artifacts are invalid."""


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise PowerBiDashboardValidationError(f"missing required dashboard artifact: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PowerBiDashboardValidationError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise PowerBiDashboardValidationError(f"dashboard artifact must be a JSON object: {path}")
    return data


def validate_schema(schema: dict[str, Any]) -> list[str]:
    issues: list[str] = []

    if schema.get("version") != "v25.0.0":
        issues.append("dashboard schema version must be v25.0.0")

    fact_tables = schema.get("fact_tables", [])
    if not isinstance(fact_tables, list) or not fact_tables:
        issues.append("dashboard schema must define fact_tables")
        return issues

    fact_table_names = {table.get("name") for table in fact_tables if isinstance(table, dict)}
    missing_tables = REQUIRED_FACT_TABLES - fact_table_names
    for table_name in sorted(missing_tables):
        issues.append(f"missing dashboard fact table: {table_name}")

    for table in fact_tables:
        if not isinstance(table, dict):
            issues.append("fact table entries must be JSON objects")
            continue
        table_name = table.get("name")
        path = table.get("path")
        grain = table.get("grain")
        measures = table.get("primary_measures", [])
        if not table_name:
            issues.append("fact table missing name")
        if not path or not str(path).endswith(".csv"):
            issues.append(f"fact table must point to a CSV path: {table_name}")
        if not grain:
            issues.append(f"fact table missing grain: {table_name}")
        if not isinstance(measures, list) or not measures:
            issues.append(f"fact table missing primary measures: {table_name}")

    visuals = set(schema.get("recommended_visuals", []))
    missing_visuals = REQUIRED_VISUALS - visuals
    for visual in sorted(missing_visuals):
        issues.append(f"missing recommended visual: {visual}")

    if "refresh_guidance" not in schema:
        issues.append("dashboard schema must include refresh guidance")

    return issues


def validate_required_files() -> list[str]:
    issues: list[str] = []
    for path in [EXPORTER_SCRIPT_PATH, DASHBOARD_SCHEMA_PATH, DOCUMENTATION_PATH, README_PATH]:
        if not path.exists():
            issues.append(f"missing required file: {path}")
    return issues


def validate_powerbi_dashboard_artifacts() -> list[str]:
    issues = validate_required_files()
    if DASHBOARD_SCHEMA_PATH.exists():
        issues.extend(validate_schema(load_json(DASHBOARD_SCHEMA_PATH)))
    return issues


def assert_valid_powerbi_dashboard_artifacts() -> None:
    issues = validate_powerbi_dashboard_artifacts()
    if issues:
        raise PowerBiDashboardValidationError("; ".join(issues))


def main() -> int:
    issues = validate_powerbi_dashboard_artifacts()
    if issues:
        print("Power BI dashboard artifact validation FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Power BI dashboard artifact validation SUCCESS")
    print("Validated fact tables: 3")
    print("Validated dashboard schema: dashboards/powerbi/observability_dashboard_schema.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
