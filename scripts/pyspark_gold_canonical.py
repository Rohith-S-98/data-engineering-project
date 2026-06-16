from pyspark.sql.functions import col, concat_ws, current_timestamp, lit

from scripts.spark_session import get_spark_session


SILVER_INPUT_PATH = "data/silver/customer_valid"
GOLD_OUTPUT_PATH = "data/gold/customer_canonical"
RELTIO_PAYLOAD_OUTPUT_PATH = "output/reltio_payloads/customer_payload_json"


def run_pyspark_gold_canonical() -> None:
    print("Starting PySpark gold canonical transformation...")

    spark = get_spark_session("PySparkGoldCanonical")

    silver_df = spark.read.parquet(SILVER_INPUT_PATH)

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

    gold_df.write.mode("overwrite").parquet(GOLD_OUTPUT_PATH)

    (
        gold_df
        .coalesce(1)
        .write
        .mode("overwrite")
        .json(RELTIO_PAYLOAD_OUTPUT_PATH)
    )

    print(f"Gold canonical data written at: {GOLD_OUTPUT_PATH}")
    print(f"Reltio-style JSON payload written at: {RELTIO_PAYLOAD_OUTPUT_PATH}")

    spark.stop()


if __name__ == "__main__":
    run_pyspark_gold_canonical()