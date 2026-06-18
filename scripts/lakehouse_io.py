from pathlib import Path

from delta.tables import DeltaTable
from pyspark.sql import DataFrame, SparkSession


def get_storage_format(config: dict) -> str:
    """
    Return configured lakehouse storage format.

    Supported:
    - parquet
    - delta
    """

    return str(config.get("storage_format", "parquet")).lower()


def get_lakehouse_write_strategy(config: dict) -> str:
    """
    Return configured lakehouse write strategy.

    Supported:
    - overwrite
    - merge
    """

    return str(config.get("lakehouse_write_strategy", "overwrite")).lower()


def read_lakehouse_table(
    spark: SparkSession,
    input_path: str,
    storage_format: str,
) -> DataFrame:
    """
    Read a lakehouse table by path using the configured storage format.
    """

    return spark.read.format(storage_format).load(input_path)


def write_lakehouse_table(
    df: DataFrame,
    output_path: str,
    storage_format: str,
    mode: str = "overwrite",
) -> None:
    """
    Write a lakehouse table by path using the configured storage format.
    """

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    (
        df.write
        .format(storage_format)
        .mode(mode)
        .save(output_path)
    )


def is_delta_table_path(table_path: str) -> bool:
    """
    Check whether a path looks like a Delta table.
    """

    return (Path(table_path) / "_delta_log").exists()


def assert_delta_table_exists(
    table_path: str,
    table_name: str,
) -> None:
    """
    Validate that a table path contains Delta transaction logs.
    """

    if not is_delta_table_path(table_path):
        raise ValueError(
            f"{table_name} is not a valid Delta table path: {table_path}. "
            "Expected _delta_log folder was not found."
        )


def build_merge_condition(
    merge_keys: list[str],
    target_alias: str = "target",
    source_alias: str = "source",
) -> str:
    """
    Build Delta MERGE condition from configured merge keys.

    Example:
        ["source_system", "source_id"]

    Output:
        target.source_system = source.source_system
        AND target.source_id = source.source_id
    """

    if not merge_keys:
        raise ValueError("merge_keys must contain at least one column")

    invalid_keys = [
        key
        for key in merge_keys
        if not isinstance(key, str) or not key.strip()
    ]

    if invalid_keys:
        raise ValueError(f"Invalid merge keys: {invalid_keys}")

    return " AND ".join(
        f"{target_alias}.{key} = {source_alias}.{key}"
        for key in merge_keys
    )


def merge_lakehouse_table(
    spark: SparkSession,
    source_df: DataFrame,
    target_path: str,
    merge_keys: list[str],
    storage_format: str,
) -> str:
    """
    Upsert source DataFrame into a target Delta table.

    If the Delta table does not exist, it is created.
    If it exists, records are updated when matched and inserted when not matched.
    """

    if storage_format != "delta":
        write_lakehouse_table(
            df=source_df,
            output_path=target_path,
            storage_format=storage_format,
            mode="overwrite",
        )
        return "overwritten"

    if not is_delta_table_path(target_path):
        write_lakehouse_table(
            df=source_df,
            output_path=target_path,
            storage_format=storage_format,
            mode="overwrite",
        )
        return "created"

    merge_condition = build_merge_condition(merge_keys)

    (
        DeltaTable.forPath(spark, target_path)
        .alias("target")
        .merge(
            source_df.alias("source"),
            merge_condition,
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )

    return "merged"


def write_or_merge_lakehouse_table(
    spark: SparkSession,
    df: DataFrame,
    output_path: str,
    storage_format: str,
    write_strategy: str,
    merge_keys: list[str],
) -> str:
    """
    Write data using either overwrite or Delta MERGE strategy.
    """

    if write_strategy == "merge":
        return merge_lakehouse_table(
            spark=spark,
            source_df=df,
            target_path=output_path,
            merge_keys=merge_keys,
            storage_format=storage_format,
        )

    write_lakehouse_table(
        df=df,
        output_path=output_path,
        storage_format=storage_format,
        mode="overwrite",
    )

    return "overwritten"