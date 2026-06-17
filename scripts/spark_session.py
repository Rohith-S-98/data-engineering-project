import contextlib
import os
import sys
from pathlib import Path

# Must be set before SparkSession creation.
os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)

os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--conf spark.ui.showConsoleProgress=false "
    "--conf spark.driver.extraJavaOptions='-Dlog4j.configurationFile=config/log4j2.properties' "
    "--conf spark.executor.extraJavaOptions='-Dlog4j.configurationFile=config/log4j2.properties' "
    "pyspark-shell"
)

from pyspark.sql import SparkSession


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


def get_spark_session(app_name: str = "DataEngineeringPipeline") -> SparkSession:
    Path("config").mkdir(parents=True, exist_ok=True)

    with suppress_spark_startup_noise():
        spark = (
            SparkSession.builder
            .appName(app_name)
            .master("local[*]")
            .config("spark.ui.showConsoleProgress", "false")
            .config("spark.sql.shuffle.partitions", "4")
            .config("spark.driver.extraJavaOptions", "-Dlog4j.configurationFile=config/log4j2.properties")
            .config("spark.executor.extraJavaOptions", "-Dlog4j.configurationFile=config/log4j2.properties")
            .getOrCreate()
        )

    spark.sparkContext.setLogLevel("ERROR")

    return spark