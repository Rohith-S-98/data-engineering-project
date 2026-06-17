import contextlib
import os
import sys
from pathlib import Path

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession


# Must be set before SparkSession creation.
os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)


@contextlib.contextmanager
def suppress_spark_startup_noise():
    """
    Suppresses JVM/Spark startup stderr noise during SparkSession creation.

    This hides common local Spark messages like:
    - Using incubator modules
    - NativeCodeLoader warning
    - default log4j profile warning

    Real Python exceptions will still be raised.
    """

    devnull = open(os.devnull, "w")
    old_stderr_fd = os.dup(2)

    try:
        os.dup2(devnull.fileno(), 2)
        yield
    finally:
        os.dup2(old_stderr_fd, 2)
        os.close(old_stderr_fd)
        devnull.close()


def get_spark_session(
    app_name: str = "DataEngineeringPipeline",
    enable_delta: bool = True,
) -> SparkSession:
    """
    Create a local SparkSession.

    V10 enables Delta Lake support by default so Bronze, Silver, Gold,
    and quarantine lakehouse outputs can be written as Delta tables.
    """

    Path("config").mkdir(parents=True, exist_ok=True)

    builder = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.sql.shuffle.partitions", "4")
        .config(
            "spark.driver.extraJavaOptions",
            "-Dlog4j.configurationFile=config/log4j2.properties",
        )
        .config(
            "spark.executor.extraJavaOptions",
            "-Dlog4j.configurationFile=config/log4j2.properties",
        )
    )

    if enable_delta:
        builder = (
            configure_spark_with_delta_pip(builder)
            .config(
                "spark.sql.extensions",
                "io.delta.sql.DeltaSparkSessionExtension",
            )
            .config(
                "spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog",
            )
        )

    with suppress_spark_startup_noise():
        spark = builder.getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    return spark