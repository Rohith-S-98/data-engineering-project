from pathlib import Path

from scripts.create_sample_data import create_raw_customer_data
from scripts.pipeline_config import load_pipeline_config
from scripts.schema_validation_framework import (
    print_schema_validation_result,
    validate_schema,
)
from scripts.spark_session import get_spark_session
from scripts.watermark_manager import (
    filter_incremental_dataframe,
    get_last_watermark_value,
    get_max_watermark_value,
    stage_watermark_update,
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

    try:
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

        watermark_column = "created_date"
        dataset_name = "customers"

        last_watermark = get_last_watermark_value(dataset=dataset_name)

        incremental_df = filter_incremental_dataframe(
            df=raw_df,
            watermark_column=watermark_column,
            last_watermark=last_watermark,
        )

        raw_row_count = raw_df.count()
        incremental_row_count = incremental_df.count()

        print(f"Raw input row count: {raw_row_count}")
        print(f"Incremental row count: {incremental_row_count}")

        new_watermark = get_max_watermark_value(
            df=incremental_df,
            watermark_column=watermark_column,
        )

        stage_watermark_update(
            dataset=dataset_name,
            watermark_column=watermark_column,
            previous_watermark=last_watermark,
            new_watermark=new_watermark,
        )

        print("Incremental Bronze DataFrame preview:")
        incremental_df.show(truncate=False)

        incremental_df.write.mode("overwrite").parquet(bronze_output_path)

        print(f"Bronze data written successfully at: {bronze_output_path}")

    finally:
        spark.stop()


if __name__ == "__main__":
    run_bronze_ingestion()