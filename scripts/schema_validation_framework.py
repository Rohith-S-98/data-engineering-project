import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SchemaValidationException(Exception):
    """Custom exception for schema validation failures."""

    def __init__(
        self,
        message: str,
        dataset: Optional[str] = None,
        layer: Optional[str] = None,
        issues: Optional[List[Dict]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.dataset = dataset
        self.layer = layer
        self.issues = issues or []

    def to_dict(self) -> Dict:
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "dataset": self.dataset,
            "layer": self.layer,
            "issues": self.issues,
            "timestamp": utc_now_iso(),
        }


@dataclass
class SchemaIssue:
    issue_type: str
    column_name: Optional[str]
    expected: Optional[str]
    actual: Optional[str]
    severity: str
    message: str


@dataclass
class SchemaValidationResult:
    schema_name: str
    layer: str
    dataset: str
    status: str
    total_issues: int
    issues: List[Dict]
    validated_at: str


def load_schema_contract(contract_path: str) -> Dict:
    if not os.path.exists(contract_path):
        raise FileNotFoundError(f"Schema contract not found: {contract_path}")

    with open(contract_path, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_data_type(data_type: Optional[str]) -> str:
    if data_type is None:
        return ""

    normalized = data_type.lower().strip()

    aliases = {
        "integer": "int",
        "long": "bigint",
        "boolean": "boolean",
        "bool": "boolean",
        "str": "string",
        "varchar": "string",
        "char": "string",
        "timestamp_ntz": "timestamp",
    }

    return aliases.get(normalized, normalized)


def data_types_match(expected: str, actual: str) -> bool:
    expected_norm = normalize_data_type(expected)
    actual_norm = normalize_data_type(actual)

    if expected_norm == actual_norm:
        return True

    if expected_norm.startswith("decimal") and actual_norm.startswith("decimal"):
        return True

    return False


def get_dataframe_schema_map(df: DataFrame) -> Dict[str, str]:
    return {field.name: field.dataType.simpleString() for field in df.schema.fields}


def find_duplicate_columns(df: DataFrame) -> List[str]:
    seen = set()
    duplicates = []

    for column in df.columns:
        if column in seen:
            duplicates.append(column)
        seen.add(column)

    return duplicates


def build_schema_issue(
    issue_type: str,
    column_name: Optional[str],
    expected: Optional[str],
    actual: Optional[str],
    severity: str,
    message: str,
) -> SchemaIssue:
    return SchemaIssue(
        issue_type=issue_type,
        column_name=column_name,
        expected=expected,
        actual=actual,
        severity=severity,
        message=message,
    )


def write_schema_validation_audit(
    result: SchemaValidationResult,
    audit_path: str = "data/audit/schema_validation_audit.jsonl",
) -> None:
    os.makedirs(os.path.dirname(audit_path), exist_ok=True)

    with open(audit_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(asdict(result)) + "\n")


def validate_schema(
    df: DataFrame,
    contract_path: str,
    audit_path: str = "data/audit/schema_validation_audit.jsonl",
    raise_on_failure: bool = True,
) -> SchemaValidationResult:
    contract = load_schema_contract(contract_path)

    schema_name = contract.get("schema_name", "unknown_schema")
    layer = contract.get("layer", "unknown_layer")
    dataset = contract.get("dataset", "unknown_dataset")
    allow_unexpected_columns = contract.get("allow_unexpected_columns", False)
    enforce_data_types = contract.get("enforce_data_types", True)
    check_nullable_data = contract.get("check_nullable_data", False)

    expected_columns = contract.get("columns", [])
    expected_column_map = {column["name"]: column for column in expected_columns}

    actual_columns = df.columns
    actual_column_set = set(actual_columns)
    expected_column_set = set(expected_column_map.keys())
    actual_schema_map = get_dataframe_schema_map(df)

    issues: List[SchemaIssue] = []

    duplicate_columns = find_duplicate_columns(df)
    for column_name in duplicate_columns:
        issues.append(
            build_schema_issue(
                issue_type="DUPLICATE_COLUMN",
                column_name=column_name,
                expected="unique column name",
                actual="duplicate column found",
                severity="ERROR",
                message=f"Duplicate column found: {column_name}",
            )
        )

    for column_name, column_config in expected_column_map.items():
        required = column_config.get("required", False)

        if required and column_name not in actual_column_set:
            issues.append(
                build_schema_issue(
                    issue_type="MISSING_REQUIRED_COLUMN",
                    column_name=column_name,
                    expected="column should exist",
                    actual="column missing",
                    severity="ERROR",
                    message=f"Required column missing: {column_name}",
                )
            )

    unexpected_columns = actual_column_set - expected_column_set

    if unexpected_columns and not allow_unexpected_columns:
        for column_name in sorted(unexpected_columns):
            issues.append(
                build_schema_issue(
                    issue_type="UNEXPECTED_COLUMN",
                    column_name=column_name,
                    expected="not present in schema contract",
                    actual="present in dataframe",
                    severity="ERROR",
                    message=f"Unexpected column found: {column_name}",
                )
            )
    elif unexpected_columns and allow_unexpected_columns:
        for column_name in sorted(unexpected_columns):
            issues.append(
                build_schema_issue(
                    issue_type="UNEXPECTED_COLUMN",
                    column_name=column_name,
                    expected="not present in schema contract",
                    actual="present in dataframe",
                    severity="WARN",
                    message=f"Unexpected column found but allowed: {column_name}",
                )
            )

    if enforce_data_types:
        for column_name, column_config in expected_column_map.items():
            if column_name not in actual_column_set:
                continue

            expected_type = column_config.get("data_type")
            actual_type = actual_schema_map.get(column_name)

            if not data_types_match(expected_type, actual_type):
                issues.append(
                    build_schema_issue(
                        issue_type="DATA_TYPE_MISMATCH",
                        column_name=column_name,
                        expected=expected_type,
                        actual=actual_type,
                        severity="ERROR",
                        message=(
                            f"Data type mismatch for column {column_name}: "
                            f"expected {expected_type}, actual {actual_type}"
                        ),
                    )
                )

    if check_nullable_data:
        for column_name, column_config in expected_column_map.items():
            if column_name not in actual_column_set:
                continue

            nullable = column_config.get("nullable", True)

            if nullable is False:
                null_exists = df.filter(F.col(column_name).isNull()).limit(1).count() > 0

                if null_exists:
                    issues.append(
                        build_schema_issue(
                            issue_type="NULLABILITY_VIOLATION",
                            column_name=column_name,
                            expected="non-null values",
                            actual="null value found",
                            severity="ERROR",
                            message=f"Non-nullable column contains null values: {column_name}",
                        )
                    )

    issue_dicts = [asdict(issue) for issue in issues]
    error_issues = [issue for issue in issues if issue.severity == "ERROR"]
    status = "FAILED" if error_issues else "PASSED"

    result = SchemaValidationResult(
        schema_name=schema_name,
        layer=layer,
        dataset=dataset,
        status=status,
        total_issues=len(issues),
        issues=issue_dicts,
        validated_at=utc_now_iso(),
    )

    write_schema_validation_audit(result, audit_path)

    if status == "FAILED" and raise_on_failure:
        raise SchemaValidationException(
            message=f"Schema validation failed for {layer}.{dataset}",
            dataset=dataset,
            layer=layer,
            issues=issue_dicts,
        )

    return result


def print_schema_validation_result(result: SchemaValidationResult) -> None:
    print("=" * 70)
    print("Schema Validation Result")
    print("=" * 70)
    print(f"Schema Name  : {result.schema_name}")
    print(f"Layer        : {result.layer}")
    print(f"Dataset      : {result.dataset}")
    print(f"Status       : {result.status}")
    print(f"Total Issues : {result.total_issues}")
    print(f"Validated At : {result.validated_at}")

    if result.issues:
        print("-" * 70)
        print("Issues:")
        for issue in result.issues:
            print(
                f"[{issue['severity']}] {issue['issue_type']} | "
                f"Column: {issue['column_name']} | "
                f"Expected: {issue['expected']} | "
                f"Actual: {issue['actual']} | "
                f"{issue['message']}"
            )

    print("=" * 70)
