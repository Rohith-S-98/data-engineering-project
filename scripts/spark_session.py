from pyspark.sql import SparkSession


def get_spark_session(app_name: str = "DataEngineeringPipelineV2") -> SparkSession:
    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")
    return spark