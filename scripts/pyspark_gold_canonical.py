from pyspark.sql.functions import col, concat_ws, current_timestamp, lit

from scripts.lakehouse_io import (
    assert_delta_table_exists,
    get_storage_format,
    read_lakehouse_table,
    write_lakehouse_table,
)
from scripts.pipeline_config import load_pipeline_config
from scripts.spark_session import get_spark_session
from scripts.lakehouse_io import (
    assert_delta_table_exists,
    get_lakehouse_write_strategy,
    get_storage_format,
    read_lakehouse_table,
    write_or_merge_lakehouse_table,
)

def run_pyspark_gold_canonical() -> None:
    print("Starting PySpark gold canonical transformation...")

    config = load_pipeline_config()

    silver_input_path = config["silver_output_path"]
    gold_output_path = config["gold_output_path"]
    reltio_payload_output_path = config["reltio_payload_output_path"]
    storage_format = get_storage_format(config)
    write_strategy = get_lakehouse_write_strategy(config)
    spark = get_spark_session("PySparkGoldCanonical")

    try:
        silver_df = read_lakehouse_table(
            spark=spark,
            input_path=silver_input_path,
            storage_format=storage_format,
        )

        print("Silver valid records:")
        silver_df.show(truncate=False)

        gold_df = (
            silver_df
            .withColumn("source_id", col("customer_id"))
            .withColumn("full_name", concat_ws(" ", col("first_name"), col("last_name")))
            .withColumn("record_type", lit("Customer"))
            .withColumn("record_status", lit("ACTIVE"))
            .withColumn("processed_at", current_timestamp())
            .select(
                col("source_system"),
                col("source_id"),
                col("record_type"),
                col("record_status"),
                col("full_name"),
                col("email").alias("contact_email"),
                col("phone").cast("string").alias("contact_phone"),
                col("city").alias("address_city"),
                col("state").alias("address_state"),
                col("created_date"),
                col("processed_at"),
            )
        )

        print("Gold canonical records:")
        gold_df.show(truncate=False)

        gold_write_status = write_or_merge_lakehouse_table(
            spark=spark,
            df=gold_df,
            output_path=gold_output_path,
            storage_format=storage_format,
            write_strategy=write_strategy,
            merge_keys=config["gold_merge_keys"],
        )

        if storage_format == "delta":
            assert_delta_table_exists(
                table_path=gold_output_path,
                table_name="Gold customers",
            )

        # Reltio payload intentionally stays JSON.
        gold_df.coalesce(1).write.mode("overwrite").json(reltio_payload_output_path)

        print(
            f"Gold canonical data {gold_write_status} at: "
            f"{gold_output_path} using format={storage_format}, "
            f"strategy={write_strategy}"
        )
        print(f"Reltio-style JSON payload written at: {reltio_payload_output_path}")

    finally:
        spark.stop()


if __name__ == "__main__":
    run_pyspark_gold_canonical()