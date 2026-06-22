from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from delta.tables import DeltaTable
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    concat_ws,
    coalesce,
    current_timestamp,
    lit,
    sha2,
    to_timestamp,
    trim,
)
from pyspark.sql.types import BooleanType, TimestampType


NULL_HASH_TOKEN = "__NULL__"
HASH_SEPARATOR = "||"


def normalize_hash_value(value: Any) -> str:
    """
    Normalize values before hash generation.

    This keeps hash generation stable across Python unit tests and Spark logic.
    """
    if value is None:
        return NULL_HASH_TOKEN

    normalized = str(value).strip()

    if normalized == "":
        return NULL_HASH_TOKEN

    return normalized


def generate_record_hash(
    record: dict[str, Any],
    tracked_columns: list[str],
) -> str:
    """
    Generate deterministic SHA-256 hash for selected tracked columns.
    """
    values = [
        normalize_hash_value(record.get(column))
        for column in tracked_columns
    ]

    hash_input = HASH_SEPARATOR.join(values)

    return sha256(hash_input.encode("utf-8")).hexdigest()


def is_current_record(record: dict[str, Any]) -> bool:
    """
    Return True when a history record is marked as current.
    """
    return bool(record.get("is_current") is True)


def has_record_changed(
    source_record: dict[str, Any],
    current_record: dict[str, Any],
    tracked_columns: list[str],
    hash_column: str = "record_hash",
) -> bool:
    """
    Compare source record against current history record using record hash.
    """
    source_hash = generate_record_hash(source_record, tracked_columns)
    current_hash = current_record.get(hash_column)

    if not current_hash:
        current_hash = generate_record_hash(current_record, tracked_columns)

    return source_hash != current_hash


def _current_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_current_history_record(
    record: dict[str, Any],
    tracked_columns: list[str],
    effective_start_date: Any,
) -> dict[str, Any]:
    """
    Build a new active SCD2 history record.
    """
    now = _current_utc_iso()
    history_record = dict(record)

    history_record["effective_start_date"] = effective_start_date
    history_record["effective_end_date"] = None
    history_record["is_current"] = True
    history_record["record_hash"] = generate_record_hash(record, tracked_columns)
    history_record["created_at"] = now
    history_record["updated_at"] = now

    return history_record


def build_expired_history_record(
    record: dict[str, Any],
    effective_end_date: Any,
) -> dict[str, Any]:
    """
    Expire an existing current SCD2 history record.
    """
    expired_record = dict(record)

    expired_record["effective_end_date"] = effective_end_date
    expired_record["is_current"] = False
    expired_record["updated_at"] = _current_utc_iso()

    return expired_record


def _validate_scd2_columns(
    source_df: DataFrame,
    business_key_columns: list[str],
    tracked_columns: list[str],
) -> None:
    source_columns = set(source_df.columns)
    required_columns = set(business_key_columns + tracked_columns)
    missing_columns = sorted(required_columns - source_columns)

    if missing_columns:
        raise ValueError(f"SCD2 source DataFrame missing columns: {missing_columns}")

    if not business_key_columns:
        raise ValueError("SCD2 business_key_columns must not be empty")

    if not tracked_columns:
        raise ValueError("SCD2 tracked_columns must not be empty")


def build_spark_record_hash(
    tracked_columns: list[str],
):
    """
    Build Spark SHA-256 hash expression for selected tracked columns.
    """
    normalized_columns = [
        coalesce(trim(col(column_name).cast("string")), lit(NULL_HASH_TOKEN))
        for column_name in tracked_columns
    ]

    return sha2(concat_ws(HASH_SEPARATOR, *normalized_columns), 256)


def prepare_scd2_source_dataframe(
    source_df: DataFrame,
    tracked_columns: list[str],
    effective_start_column: str,
) -> DataFrame:
    """
    Add SCD2 metadata columns to source records before history processing.
    """
    if effective_start_column in source_df.columns:
        effective_start_expr = to_timestamp(col(effective_start_column))
    else:
        effective_start_expr = current_timestamp()

    return (
        source_df
        .withColumn("record_hash", build_spark_record_hash(tracked_columns))
        .withColumn("effective_start_date", effective_start_expr.cast(TimestampType()))
        .withColumn("effective_end_date", lit(None).cast(TimestampType()))
        .withColumn("is_current", lit(True).cast(BooleanType()))
        .withColumn("created_at", current_timestamp())
        .withColumn("updated_at", current_timestamp())
    )


def _build_scd2_merge_condition(
    business_key_columns: list[str],
) -> str:
    key_conditions = [
        f"target.{key} = source.{key}"
        for key in business_key_columns
    ]

    key_conditions.append("target.is_current = true")

    return " AND ".join(key_conditions)


def apply_scd_type2(
    spark: SparkSession,
    source_df: DataFrame,
    target_path: str,
    business_key_columns: list[str],
    tracked_columns: list[str],
    effective_start_column: str = "created_date",
    storage_format: str = "delta",
) -> dict[str, int | str]:
    """
    Apply SCD Type 2 logic into a Delta history table.

    Behavior:
    - If the target history table does not exist, create it with all records as current.
    - If a source business key is new, insert it as current.
    - If a source business key exists but tracked hash changed:
        1. expire previous current record
        2. insert new current version
    - If no hash change, do nothing.
    """
    if storage_format != "delta":
        raise ValueError("SCD Type 2 history tracking requires storage_format='delta'")

    _validate_scd2_columns(
        source_df=source_df,
        business_key_columns=business_key_columns,
        tracked_columns=tracked_columns,
    )

    Path(target_path).parent.mkdir(parents=True, exist_ok=True)

    prepared_source_df = prepare_scd2_source_dataframe(
        source_df=source_df,
        tracked_columns=tracked_columns,
        effective_start_column=effective_start_column,
    )

    source_count = prepared_source_df.count()

    if not (Path(target_path) / "_delta_log").exists():
        (
            prepared_source_df.write
            .format("delta")
            .mode("overwrite")
            .save(target_path)
        )

        return {
            "status": "created",
            "source_records": source_count,
            "new_records": source_count,
            "changed_records": 0,
            "inserted_records": source_count,
            "expired_records": 0,
        }

    target_delta = DeltaTable.forPath(spark, target_path)

    current_target_df = (
        target_delta.toDF()
        .filter(col("is_current") == lit(True))
        .select(
            *business_key_columns,
            col("record_hash").alias("_target_record_hash"),
        )
    )

    comparison_df = (
        prepared_source_df.alias("source")
        .join(
            current_target_df.alias("target"),
            on=business_key_columns,
            how="left",
        )
    )

    new_records_df = (
        comparison_df
        .filter(col("_target_record_hash").isNull())
        .select("source.*")
    )

    changed_records_df = (
        comparison_df
        .filter(
            col("_target_record_hash").isNotNull()
            & (col("source.record_hash") != col("_target_record_hash"))
        )
        .select("source.*")
    )

    records_to_insert_df = (
        new_records_df
        .unionByName(changed_records_df)
        .cache()
    )

    changed_keys_df = (
        changed_records_df
        .select(
            *business_key_columns,
            col("effective_start_date").alias("_new_effective_start_date"),
        )
        .cache()
    )

    new_count = new_records_df.count()
    changed_count = changed_keys_df.count()
    insert_count = records_to_insert_df.count()

    if changed_count > 0:
        merge_condition = _build_scd2_merge_condition(business_key_columns)

        (
            target_delta.alias("target")
            .merge(
                changed_keys_df.alias("source"),
                merge_condition,
            )
            .whenMatchedUpdate(
                set={
                    "effective_end_date": "source._new_effective_start_date",
                    "is_current": "false",
                    "updated_at": "current_timestamp()",
                }
            )
            .execute()
        )

    if insert_count > 0:
        (
            records_to_insert_df.write
            .format("delta")
            .mode("append")
            .save(target_path)
        )

    records_to_insert_df.unpersist()
    changed_keys_df.unpersist()

    return {
        "status": "merged",
        "source_records": source_count,
        "new_records": new_count,
        "changed_records": changed_count,
        "inserted_records": insert_count,
        "expired_records": changed_count,
    }
