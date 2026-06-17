from pathlib import Path

from scripts.create_sample_data import create_raw_customer_data
from scripts.pipeline_config import load_pipeline_config
from scripts.spark_session import get_spark_session
from scripts.schema_validation_framework import (
    validate_schema,
    print_schema_validation_result,
)

def run_bronze_ingestion() -> None:
    print("Starting PySpark bronze ingestion...")

    config = load_pipeline_config()

    raw_data_file = Path(config["raw_data_file"])
    bronze_output_path = config["bronze_output_path"]

    if not raw_data_file.exists():
        print("Raw data file not found. Creating sample data...")
        create_raw_customer_data()

    spark = get_spark_session("PySparkBronzeIngestion")

    raw_df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(raw_data_file))
    )

    print("Raw DataFrame schema:")
    raw_df.printSchema()

    bronze_schema_result = validate_schema(
        df=raw_df,
        contract_path="configs/schema_contracts/bronze_customers_schema.json",
        audit_path="data/audit/schema_validation_audit.jsonl",
        raise_on_failure=True,
    )

    print_schema_validation_result(bronze_schema_result)

    print("Raw DataFrame preview:")
    raw_df.show(truncate=False)

    (
        raw_df.write
        .mode("overwrite")
        .parquet(bronze_output_path)
    )

    print(f"Bronze data written successfully at: {bronze_output_path}")

    spark.stop()


if __name__ == "__main__":
    run_bronze_ingestion()