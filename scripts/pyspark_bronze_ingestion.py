from pathlib import Path

from scripts.create_sample_data import create_raw_customer_data
from scripts.spark_session import get_spark_session


RAW_DATA_FILE = Path("data/raw/customer_data.csv")
BRONZE_OUTPUT_PATH = "data/bronze/customer_bronze"


def run_bronze_ingestion() -> None:
    print("Starting PySpark bronze ingestion...")

    if not RAW_DATA_FILE.exists():
        print("Raw data file not found. Creating sample data...")
        create_raw_customer_data()

    spark = get_spark_session("PySparkBronzeIngestion")

    raw_df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(RAW_DATA_FILE))
    )

    print("Raw DataFrame schema:")
    raw_df.printSchema()

    print("Raw DataFrame preview:")
    raw_df.show(truncate=False)

    (
        raw_df.write
        .mode("overwrite")
        .parquet(BRONZE_OUTPUT_PATH)
    )

    print(f"Bronze data written successfully at: {BRONZE_OUTPUT_PATH}")

    spark.stop()


if __name__ == "__main__":
    run_bronze_ingestion()