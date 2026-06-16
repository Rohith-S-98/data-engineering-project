import csv
import json
from datetime import datetime
from pathlib import Path


RAW_DATA_FILE = Path("data/raw/customer_data.csv")
DQ_RULES_FILE = Path("config/rules/customer_dq_rules.json")

# OUTPUT_DIR = Path("output")
# DQ_REPORT_DIR = OUTPUT_DIR / "dq_reports"
# QUARANTINE_DIR = OUTPUT_DIR / "quarantine"

# DQ_REPORT_FILE = DQ_REPORT_DIR / "config_driven_customer_dq_report.json"
# QUARANTINE_FILE = QUARANTINE_DIR / "customer_quarantine.csv"

OUTPUT_DIR = Path("output")
DQ_REPORT_DIR = OUTPUT_DIR / "dq_reports"
QUARANTINE_DIR = OUTPUT_DIR / "quarantine"
PROCESSED_DATA_DIR = Path("data/processed")

DQ_REPORT_FILE = DQ_REPORT_DIR / "config_driven_customer_dq_report.json"
QUARANTINE_FILE = QUARANTINE_DIR / "customer_quarantine.csv"
VALID_RECORDS_FILE = PROCESSED_DATA_DIR / "customer_valid.csv"

def read_csv(file_path: Path) -> list[dict]:
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(file_path, mode="r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def read_json(file_path: Path) -> dict:
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")

    with open(file_path, mode="r", encoding="utf-8") as file:
        return json.load(file)


def check_not_null(row: dict, column: str) -> bool:
    return bool(row.get(column))


def check_allowed_values(row: dict, column: str, allowed_values: list[str]) -> bool:
    return row.get(column) in allowed_values


def get_duplicate_keys(rows: list[dict], column: str) -> set:
    seen = set()
    duplicates = set()

    for row in rows:
        value = row.get(column)

        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)

    return duplicates


def apply_dq_rules(rows: list[dict], rules_config: dict) -> tuple[list[dict], list[dict], list[dict]]:
    rules = rules_config["rules"]

    valid_rows = []
    quarantine_rows = []
    rule_results = []

    unique_rules = [rule for rule in rules if rule["rule_type"] == "unique"]
    duplicate_lookup = {}

    for rule in unique_rules:
        column = rule["column"]
        duplicate_lookup[column] = get_duplicate_keys(rows, column)

    for row in rows:
        row_errors = []

        for rule in rules:
            rule_name = rule["rule_name"]
            rule_type = rule["rule_type"]
            column = rule["column"]
            severity = rule["severity"]

            passed = True

            if rule_type == "not_null":
                passed = check_not_null(row, column)

            elif rule_type == "allowed_values":
                passed = check_allowed_values(row, column, rule["allowed_values"])

            elif rule_type == "unique":
                passed = row.get(column) not in duplicate_lookup[column]

            else:
                raise ValueError(f"Unsupported rule type: {rule_type}")

            rule_results.append(
                {
                    "rule_name": rule_name,
                    "column": column,
                    "rule_type": rule_type,
                    "severity": severity,
                    "passed": passed,
                    "customer_id": row.get("customer_id"),
                }
            )

            if not passed:
                row_errors.append(
                    {
                        "rule_name": rule_name,
                        "column": column,
                        "rule_type": rule_type,
                        "severity": severity,
                    }
                )

        if row_errors:
            quarantined_row = row.copy()
            quarantined_row["dq_errors"] = json.dumps(row_errors)
            quarantine_rows.append(quarantined_row)
        else:
            valid_rows.append(row)

    return valid_rows, quarantine_rows, rule_results


def write_csv(rows: list[dict], output_file: Path) -> None:
    if not rows:
        return

    output_file.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(rows[0].keys())

    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(data: dict, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def generate_summary_report(
    rows: list[dict],
    valid_rows: list[dict],
    quarantine_rows: list[dict],
    rule_results: list[dict],
    rules_config: dict,
) -> dict:
    failed_rules = [result for result in rule_results if not result["passed"]]

    return {
        "table_name": rules_config["table_name"],
        "primary_key": rules_config["primary_key"],
        "report_generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_file": str(RAW_DATA_FILE),
        "total_input_rows": len(rows),
        "valid_rows": len(valid_rows),
        "quarantined_rows": len(quarantine_rows),
        "total_rules_executed": len(rule_results),
        "failed_rule_count": len(failed_rules),
        "dq_status": "PASSED" if not failed_rules else "FAILED",
        "failed_rules": failed_rules,
    }


def run_config_driven_dq() -> None:
    print("Starting config-driven DQ validation...")

    rows = read_csv(RAW_DATA_FILE)
    rules_config = read_json(DQ_RULES_FILE)

    valid_rows, quarantine_rows, rule_results = apply_dq_rules(rows, rules_config)

    report = generate_summary_report(
        rows=rows,
        valid_rows=valid_rows,
        quarantine_rows=quarantine_rows,
        rule_results=rule_results,
        rules_config=rules_config,
    )

    write_csv(valid_rows, VALID_RECORDS_FILE)
    write_csv(quarantine_rows, QUARANTINE_FILE)
    write_json(report, DQ_REPORT_FILE)

    print(f"Total input rows: {len(rows)}")
    print(f"Valid rows: {len(valid_rows)}")
    print(f"Quarantined rows: {len(quarantine_rows)}")
    print(f"Valid records file created at: {VALID_RECORDS_FILE}")
    print(f"DQ report created at: {DQ_REPORT_FILE}")
    print(f"Quarantine file created at: {QUARANTINE_FILE}")


if __name__ == "__main__":
    run_config_driven_dq()