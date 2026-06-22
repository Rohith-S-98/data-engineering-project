from scripts.lakehouse_io import assert_delta_table_exists, get_storage_format, read_lakehouse_table
from scripts.pipeline_config import load_pipeline_config
from scripts.scd_type2 import apply_scd_type2
from scripts.spark_session import get_spark_session


def run_customer_history_scd2() -> None:
    print("Starting Customer History SCD Type 2 processing...")

    config = load_pipeline_config()

    silver_input_path = config["silver_output_path"]
    customer_history_output_path = config["customer_history_output_path"]
    storage_format = get_storage_format(config)

    spark = get_spark_session("CustomerHistorySCD2")

    try:
        silver_df = read_lakehouse_table(
            spark=spark,
            input_path=silver_input_path,
            storage_format=storage_format,
        )

        print("SCD2 source silver records:")
        silver_df.show(truncate=False)

        scd2_result = apply_scd_type2(
            spark=spark,
            source_df=silver_df,
            target_path=customer_history_output_path,
            business_key_columns=config["scd2_business_keys"],
            tracked_columns=config["scd2_tracked_columns"],
            effective_start_column=config["scd2_effective_start_column"],
            storage_format=storage_format,
        )

        assert_delta_table_exists(
            table_path=customer_history_output_path,
            table_name="Customer history SCD2",
        )

        print("Customer History SCD2 result:")
        print(scd2_result)
        print(f"Customer history table written at: {customer_history_output_path}")

    finally:
        spark.stop()


if __name__ == "__main__":
    run_customer_history_scd2()
