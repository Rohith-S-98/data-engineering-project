from __future__ import annotations

import json
import sys
from pathlib import Path

ADF_PIPELINE_PATH = Path("azure/adf/pipelines/customer_medallion_adf_pipeline.json")
ADF_LINKED_SERVICE_PATH = Path("azure/adf/linked_services/ls_databricks_customer_pipeline.json")
ADF_DATASET_PATH = Path("azure/adf/datasets/customer_landing_metadata.json")

REQUIRED_ACTIVITY_SEQUENCE = [
    "Validate_Runtime_Parameters",
    "Run_API_Ingestion",
    "Run_Database_Ingestion",
    "Run_Advanced_DQ_Catalog",
    "Run_Medallion_Orchestrator",
    "Validate_Runtime_Cleanliness",
]

REQUIRED_PIPELINE_PARAMETERS = ["run_date", "environment", "trigger_mode"]
REQUIRED_DATASET_COLUMNS = ["customer_id", "first_name", "last_name", "country", "created_date"]


class AdfArtifactValidationError(ValueError):
    """Raised when ADF-style artifact validation fails."""


def load_json(path: Path) -> dict:
    if not path.exists():
        raise AdfArtifactValidationError(f"missing required ADF artifact: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AdfArtifactValidationError(f"invalid JSON in {path}: {exc}") from exc


def validate_pipeline(pipeline: dict) -> list[str]:
    issues: list[str] = []

    if pipeline.get("name") != "customer_medallion_adf_pipeline":
        issues.append("pipeline name must be customer_medallion_adf_pipeline")

    properties = pipeline.get("properties", {})
    parameters = properties.get("parameters", {})
    for parameter in REQUIRED_PIPELINE_PARAMETERS:
        if parameter not in parameters:
            issues.append(f"missing pipeline parameter: {parameter}")

    activities = properties.get("activities", [])
    activity_names = [activity.get("name") for activity in activities]
    for activity_name in REQUIRED_ACTIVITY_SEQUENCE:
        if activity_name not in activity_names:
            issues.append(f"missing pipeline activity: {activity_name}")

    if len(activity_names) != len(set(activity_names)):
        issues.append("pipeline activity names must be unique")

    linked_service_references = [
        activity.get("linkedServiceName", {}).get("referenceName")
        for activity in activities
    ]
    if any(reference != "ls_databricks_customer_pipeline" for reference in linked_service_references):
        issues.append("all activities must reference ls_databricks_customer_pipeline")

    dependency_map = {
        activity.get("name"): [item.get("activity") for item in activity.get("dependsOn", [])]
        for activity in activities
    }
    expected_dependencies = {
        "Validate_Runtime_Parameters": [],
        "Run_API_Ingestion": ["Validate_Runtime_Parameters"],
        "Run_Database_Ingestion": ["Validate_Runtime_Parameters"],
        "Run_Advanced_DQ_Catalog": ["Run_API_Ingestion", "Run_Database_Ingestion"],
        "Run_Medallion_Orchestrator": ["Run_Advanced_DQ_Catalog"],
        "Validate_Runtime_Cleanliness": ["Run_Medallion_Orchestrator"],
    }
    for activity_name, expected in expected_dependencies.items():
        actual = dependency_map.get(activity_name, [])
        if sorted(actual) != sorted(expected):
            issues.append(f"invalid dependency chain for activity: {activity_name}")

    return issues


def validate_linked_service(linked_service: dict) -> list[str]:
    issues: list[str] = []

    if linked_service.get("name") != "ls_databricks_customer_pipeline":
        issues.append("linked service name must be ls_databricks_customer_pipeline")

    properties = linked_service.get("properties", {})
    if properties.get("type") != "AzureDatabricks":
        issues.append("linked service type must be AzureDatabricks")

    serialized = json.dumps(linked_service).lower()
    disallowed_tokens = ["access_token", "pat", "secret=", "password"]
    for token in disallowed_tokens:
        if token in serialized:
            issues.append(f"linked service must not contain secret-like token: {token}")

    type_properties = properties.get("typeProperties", {})
    if "workspaceUrl" not in type_properties:
        issues.append("linked service must include workspaceUrl placeholder")

    return issues


def validate_dataset(dataset: dict) -> list[str]:
    issues: list[str] = []

    if dataset.get("name") != "customer_landing_metadata":
        issues.append("dataset metadata name must be customer_landing_metadata")

    if dataset.get("format") != "csv":
        issues.append("dataset metadata format must be csv")

    columns = dataset.get("columns", [])
    for column in REQUIRED_DATASET_COLUMNS:
        if column not in columns:
            issues.append(f"dataset metadata missing column: {column}")

    if dataset.get("version") != "v24.0.0":
        issues.append("dataset metadata version must be v24.0.0")

    return issues


def validate_adf_artifacts() -> list[str]:
    pipeline = load_json(ADF_PIPELINE_PATH)
    linked_service = load_json(ADF_LINKED_SERVICE_PATH)
    dataset = load_json(ADF_DATASET_PATH)

    issues: list[str] = []
    issues.extend(validate_pipeline(pipeline))
    issues.extend(validate_linked_service(linked_service))
    issues.extend(validate_dataset(dataset))
    return issues


def assert_valid_adf_artifacts() -> None:
    issues = validate_adf_artifacts()
    if issues:
        raise AdfArtifactValidationError("; ".join(issues))


def main() -> int:
    issues = validate_adf_artifacts()
    if issues:
        print("ADF artifact validation FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("ADF artifact validation SUCCESS")
    print("Validated files: 3")
    print(f"Validated activities: {len(REQUIRED_ACTIVITY_SEQUENCE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
