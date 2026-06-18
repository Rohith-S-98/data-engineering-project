from pathlib import Path

from scripts.create_sample_data import create_raw_customer_data
from scripts.lakehouse_io import (
    assert_delta_table_exists,
    get_lakehouse_write_strategy,
    get_storage_format,
    write_or_merge_lakehouse_table,
)
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

    dataset_name = config["dataset_name"]
    watermark_column = config["watermark_column"]
    storage_format = get_storage_format(config)
    write_strategy = get_lakehouse_write_strategy(config)

    if not raw_data_file.exists():
        print("Raw data file not found. Creating sample data...")
        try:
            create_raw_customer_data(use_dirty_data=False)
        except TypeError:
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
            contract_path=config["bronze_schema_contract"],
            audit_path=config["schema_validation_audit_file"],
            raise_on_failure=True,
        )

        print_schema_validation_result(bronze_schema_result)

        last_watermark = get_last_watermark_value(
            dataset=dataset_name,
            watermark_store_path=config["watermark_store_file"],
        )

        incremental_df = filter_incremental_dataframe(
            df=raw_df,
            watermark_column=watermark_column,
            last_watermark=last_watermark,
        )

        raw_row_count = raw_df.count()
        incremental_row_count = incremental_df.count()

        print(f"Raw input row count: {raw_row_count}")
        print(f"Incremental row count: {incremental_row_count}")

        print("Incremental Bronze DataFrame preview:")
        incremental_df.show(truncate=False)

        bronze_write_status = write_or_merge_lakehouse_table(
            spark=spark,
            df=incremental_df,
            output_path=bronze_output_path,
            storage_format=storage_format,
            write_strategy=write_strategy,
            merge_keys=config["bronze_merge_keys"],
        )

        if storage_format == "delta":
            assert_delta_table_exists(
                table_path=bronze_output_path,
                table_name="Bronze customers",
            )

        print(
            f"Bronze data {bronze_write_status} successfully at: "
            f"{bronze_output_path} using format={storage_format}, "
            f"strategy={write_strategy}"
        )

        new_watermark = get_max_watermark_value(
            df=incremental_df,
            watermark_column=watermark_column,
        )

        if new_watermark is not None:
            stage_watermark_update(
                dataset=dataset_name,
                watermark_column=watermark_column,
                previous_watermark=last_watermark,
                new_watermark=new_watermark,
                pending_watermark_path=config["pending_watermark_file"],
            )
        else:
            print("No new watermark staged because no incremental records were found.")

    finally:
        spark.stop()


if __name__ == "__main__":
    run_bronze_ingestion()