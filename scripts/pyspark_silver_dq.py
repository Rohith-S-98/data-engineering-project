import json
from datetime import datetime
from pathlib import Path

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, concat_ws, lit, trim, when
from pyspark.sql.window import Window
from pyspark.sql.functions import count

from scripts.spark_session import get_spark_session


BRONZE_INPUT_PATH = "data/bronze/customer_bronze"
DQ_RULES_FILE = Path("config/rules/customer_dq_rules.json")

SILVER_OUTPUT_PATH = "data/silver/customer_valid"
QUARANTINE_OUTPUT_PATH = "output/quarantine/pyspark_customer_quarantine"

DQ_REPORT_DIR = Path("output/dq_reports")
DQ_REPORT_FILE = DQ_REPORT_DIR / "pyspark_customer_dq_report.json"


def read_json(file_path: Path) -> dict:
    if not file_path.exists():
        raise FileNotFoundError(f"DQ rules file not found: {file_path}")

    with open(file_path, mode="r", encoding="utf-8") as file:
        return json.load(file)


def apply_pyspark_dq_rules(df: DataFrame, rules_config: dict) -> tuple[DataFrame, DataFrame, list[dict]]:
    rules = rules_config["rules"]
    validated_df = df
    rule_summary = []

    for rule in rules:
        rule_name = rule["rule_name"]
        rule_type = rule["rule_type"]
        column_name = rule["column"]
        severity = rule["severity"]
        error_column = f"{rule_name}_failed"

        if rule_type == "not_null":
            failed_condition = (
                col(column_name).isNull() |
                (trim(col(column_name).cast("string")) == "")
            )

        elif rule_type == "allowed_values":
            allowed_values = rule["allowed_values"]
            failed_condition = ~col(column_name).isin(allowed_values)

        elif rule_type == "unique":
            window_spec = Window.partitionBy(column_name)
            validated_df = validated_df.withColumn(
                f"{column_name}_count",
                count(column_name).over(window_spec)
            )
            failed_condition = col(f"{column_name}_count") > 1

        else:
            raise ValueError(f"Unsupported rule type: {rule_type}")

        validated_df = validated_df.withColumn(
            error_column,
            when(failed_condition, lit(rule_name)).otherwise(lit(None))
        )

        failed_count = validated_df.filter(col(error_column).isNotNull()).count()

        rule_summary.append(
            {
                "rule_name": rule_name,
                "rule_type": rule_type,
                "column": column_name,
                "severity": severity,
                "failed_count": failed_count,
            }
        )

    error_columns = [
        f"{rule['rule_name']}_failed"
        for rule in rules
    ]

    validated_df = validated_df.withColumn(
        "dq_errors",
        concat_ws(", ", *[col(error_col) for error_col in error_columns])
    )

    quarantine_df = validated_df.filter(col("dq_errors") != "")
    valid_df = validated_df.filter(col("dq_errors") == "")

    technical_columns = error_columns + [
        f"{rule['column']}_count"
        for rule in rules
        if rule["rule_type"] == "unique"
    ]

    valid_df = valid_df.drop(*technical_columns, "dq_errors")

    return valid_df, quarantine_df, rule_summary


def write_dq_report(
    total_input_rows: int,
    valid_rows: int,
    quarantined_rows: int,
    rule_summary: list[dict],
    rules_config: dict,
) -> None:
    failed_rules = [
        rule for rule in rule_summary
        if rule["failed_count"] > 0
    ]

    report = {
        "table_name": rules_config["table_name"],
        "primary_key": rules_config["primary_key"],
        "report_generated_at": datetime.now().isoformat(timespec="seconds"),
        "input_layer": BRONZE_INPUT_PATH,
        "silver_output_path": SILVER_OUTPUT_PATH,
        "quarantine_output_path": QUARANTINE_OUTPUT_PATH,
        "total_input_rows": total_input_rows,
        "valid_rows": valid_rows,
        "quarantined_rows": quarantined_rows,
        "total_rules": len(rule_summary),
        "failed_rule_count": len(failed_rules),
        "dq_status": "PASSED" if not failed_rules else "FAILED",
        "rule_summary": rule_summary,
    }

    DQ_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with open(DQ_REPORT_FILE, mode="w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)


def run_pyspark_silver_dq() -> None:
    print("Starting PySpark silver DQ validation...")

    spark = get_spark_session("PySparkSilverDQ")

    rules_config = read_json(DQ_RULES_FILE)

    bronze_df = spark.read.parquet(BRONZE_INPUT_PATH)

    print("Bronze DataFrame:")
    bronze_df.show(truncate=False)

    valid_df, quarantine_df, rule_summary = apply_pyspark_dq_rules(
        bronze_df,
        rules_config,
    )

    total_input_rows = bronze_df.count()
    valid_rows = valid_df.count()
    quarantined_rows = quarantine_df.count()

    valid_df.write.mode("overwrite").parquet(SILVER_OUTPUT_PATH)
    quarantine_df.write.mode("overwrite").parquet(QUARANTINE_OUTPUT_PATH)

    write_dq_report(
        total_input_rows=total_input_rows,
        valid_rows=valid_rows,
        quarantined_rows=quarantined_rows,
        rule_summary=rule_summary,
        rules_config=rules_config,
    )

    print(f"Total input rows: {total_input_rows}")
    print(f"Valid rows: {valid_rows}")
    print(f"Quarantined rows: {quarantined_rows}")
    print(f"Silver valid records written at: {SILVER_OUTPUT_PATH}")
    print(f"Quarantine records written at: {QUARANTINE_OUTPUT_PATH}")
    print(f"DQ report written at: {DQ_REPORT_FILE}")

    spark.stop()


if __name__ == "__main__":
    run_pyspark_silver_dq()