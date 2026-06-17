from pathlib import Path

from pyspark.sql import DataFrame, SparkSession


def get_storage_format(config: dict) -> str:
    """
    Return configured lakehouse storage format.

    Supported:
    - parquet
    - delta
    """

    return str(config.get("storage_format", "parquet")).lower()


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