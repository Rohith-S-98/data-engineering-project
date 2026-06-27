from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_CATALOG_PATH = Path("config/rules/advanced_customer_dq_rule_catalog.json")
DEFAULT_INPUT_PATH = Path("data/raw/customer_data_dq_catalog_sample.csv")
DEFAULT_SUMMARY_PATH = Path("output/dq_reports/advanced_dq_catalog_summary.json")

SUPPORTED_RULE_TYPES = {"not_null", "regex", "allowed_values", "unique", "min_length"}
SUPPORTED_SEVERITIES = {"critical", "warning"}


@dataclass(frozen=True)
class RuleEvaluationResult:
    rule_id: str
    rule_name: str
    column: str
    rule_type: str
    severity: str
    failed_count: int
    passed_count: int


@dataclass(frozen=True)
class DqCatalogEvaluationSummary:
    catalog_name: str
    dataset_name: str
    total_records: int
    rules_evaluated: int
    total_failed_rules: int
    critical_failures: int
    warning_failures: int
    status: str
    output_summary_path: str


class DqRuleCatalogConfigError(ValueError):
    """Raised when the DQ rule catalog configuration is invalid."""


class DqRuleCatalogExecutionError(RuntimeError):
    """Raised when DQ rule catalog execution fails."""


def load_json(path: Path | str) -> dict[str, Any]:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_csv_records(input_path: Path | str) -> list[dict[str, str]]:
    file_path = Path(input_path)
    if not file_path.exists():
        raise DqRuleCatalogExecutionError(f"Input file not found: {file_path}")

    with file_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def validate_rule_catalog(catalog: dict[str, Any]) -> None:
    required_catalog_keys = {"catalog_name", "dataset_name", "rules"}
    missing_catalog_keys = sorted(required_catalog_keys - set(catalog))
    if missing_catalog_keys:
        raise DqRuleCatalogConfigError(f"Missing catalog keys: {missing_catalog_keys}")

    rules = catalog["rules"]
    if not isinstance(rules, list) or not rules:
        raise DqRuleCatalogConfigError("rules must be a non-empty list")

    for rule in rules:
        _validate_rule(rule)


def _validate_rule(rule: dict[str, Any]) -> None:
    required_rule_keys = {"rule_id", "rule_name", "column", "rule_type", "severity", "enabled"}
    missing_rule_keys = sorted(required_rule_keys - set(rule))
    if missing_rule_keys:
        raise DqRuleCatalogConfigError(f"Rule is missing required keys: {missing_rule_keys}")

    if rule["rule_type"] not in SUPPORTED_RULE_TYPES:
        raise DqRuleCatalogConfigError(f"Unsupported rule_type: {rule['rule_type']}")

    if rule["severity"] not in SUPPORTED_SEVERITIES:
        raise DqRuleCatalogConfigError(f"Unsupported severity: {rule['severity']}")

    if rule["rule_type"] == "regex" and not rule.get("pattern"):
        raise DqRuleCatalogConfigError("regex rule requires pattern")

    if rule["rule_type"] == "allowed_values" and not isinstance(rule.get("allowed_values"), list):
        raise DqRuleCatalogConfigError("allowed_values rule requires allowed_values list")

    if rule["rule_type"] == "min_length":
        min_length = rule.get("min_length")
        if not isinstance(min_length, int) or min_length <= 0:
            raise DqRuleCatalogConfigError("min_length rule requires positive integer min_length")


def load_rule_catalog(catalog_path: Path | str = DEFAULT_CATALOG_PATH) -> dict[str, Any]:
    catalog = load_json(catalog_path)
    validate_rule_catalog(catalog)
    return catalog


def evaluate_rule(records: list[dict[str, str]], rule: dict[str, Any]) -> RuleEvaluationResult:
    failed_count = 0
    column = rule["column"]
    rule_type = rule["rule_type"]

    if rule_type == "unique":
        values = [record.get(column, "") for record in records]
        duplicate_values = {value for value in values if value and values.count(value) > 1}
        failed_count = sum(1 for value in values if value in duplicate_values)
    else:
        for record in records:
            value = record.get(column, "")
            if _record_fails_rule(value, rule):
                failed_count += 1

    return RuleEvaluationResult(
        rule_id=rule["rule_id"],
        rule_name=rule["rule_name"],
        column=column,
        rule_type=rule_type,
        severity=rule["severity"],
        failed_count=failed_count,
        passed_count=len(records) - failed_count,
    )


def _record_fails_rule(value: str, rule: dict[str, Any]) -> bool:
    rule_type = rule["rule_type"]

    if rule_type == "not_null":
        return value is None or str(value).strip() == ""

    if rule_type == "regex":
        return re.fullmatch(rule["pattern"], str(value or "")) is None

    if rule_type == "allowed_values":
        return str(value or "") not in set(str(item) for item in rule["allowed_values"])

    if rule_type == "min_length":
        return len(str(value or "")) < int(rule["min_length"])

    raise DqRuleCatalogConfigError(f"Unsupported rule_type: {rule_type}")


def evaluate_rule_catalog(records: list[dict[str, str]], catalog: dict[str, Any]) -> tuple[DqCatalogEvaluationSummary, list[RuleEvaluationResult]]:
    enabled_rules = [rule for rule in catalog["rules"] if rule.get("enabled", False)]
    results = [evaluate_rule(records, rule) for rule in enabled_rules]

    critical_failures = sum(result.failed_count for result in results if result.severity == "critical")
    warning_failures = sum(result.failed_count for result in results if result.severity == "warning")
    total_failed_rules = sum(1 for result in results if result.failed_count > 0)
    status = "FAILED" if critical_failures > 0 else "SUCCESS_WITH_WARNINGS" if warning_failures > 0 else "SUCCESS"

    summary = DqCatalogEvaluationSummary(
        catalog_name=catalog["catalog_name"],
        dataset_name=catalog["dataset_name"],
        total_records=len(records),
        rules_evaluated=len(results),
        total_failed_rules=total_failed_rules,
        critical_failures=critical_failures,
        warning_failures=warning_failures,
        status=status,
        output_summary_path=str(DEFAULT_SUMMARY_PATH),
    )
    return summary, results


def write_summary(summary: DqCatalogEvaluationSummary, results: list[RuleEvaluationResult], output_path: Path | str) -> None:
    file_path = Path(output_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": asdict(summary) | {"output_summary_path": str(file_path)},
        "rules": [asdict(result) for result in results],
    }
    file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_advanced_dq_rule_catalog(
    catalog_path: Path | str = DEFAULT_CATALOG_PATH,
    input_path: Path | str = DEFAULT_INPUT_PATH,
    output_path: Path | str = DEFAULT_SUMMARY_PATH,
) -> DqCatalogEvaluationSummary:
    catalog = load_rule_catalog(catalog_path)
    records = read_csv_records(input_path)
    summary, results = evaluate_rule_catalog(records, catalog)
    final_summary = DqCatalogEvaluationSummary(
        catalog_name=summary.catalog_name,
        dataset_name=summary.dataset_name,
        total_records=summary.total_records,
        rules_evaluated=summary.rules_evaluated,
        total_failed_rules=summary.total_failed_rules,
        critical_failures=summary.critical_failures,
        warning_failures=summary.warning_failures,
        status=summary.status,
        output_summary_path=str(output_path),
    )
    write_summary(final_summary, results, output_path)
    return final_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V22 advanced data quality rule catalog.")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG_PATH), help="Path to advanced DQ rule catalog JSON.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT_PATH), help="Path to input customer CSV.")
    parser.add_argument("--output", default=str(DEFAULT_SUMMARY_PATH), help="Path to output DQ summary JSON.")
    args = parser.parse_args()

    summary = run_advanced_dq_rule_catalog(args.catalog, args.input, args.output)
    print("Advanced DQ rule catalog evaluation SUCCESS")
    print(f"Catalog name     : {summary.catalog_name}")
    print(f"Dataset name     : {summary.dataset_name}")
    print(f"Total records    : {summary.total_records}")
    print(f"Rules evaluated  : {summary.rules_evaluated}")
    print(f"Critical failures: {summary.critical_failures}")
    print(f"Warning failures : {summary.warning_failures}")
    print(f"Final status     : {summary.status}")
    print(f"Summary file     : {summary.output_summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
