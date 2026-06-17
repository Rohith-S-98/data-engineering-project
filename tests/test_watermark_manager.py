from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from scripts.watermark_manager import (
    get_last_watermark_value,
    filter_incremental_dataframe,
    get_max_watermark_value,
    stage_watermark_update,
    commit_staged_watermark_update,
)


def main():
    test_watermark_store = "data/audit/test_watermark_store.json"
    test_pending_watermark = "data/audit/test_pending_watermark_updates.json"

    Path(test_watermark_store).unlink(missing_ok=True)
    Path(test_pending_watermark).unlink(missing_ok=True)

    spark = (
        SparkSession.builder
        .appName("V9 Watermark Manager Test")
        .master("local[*]")
        .getOrCreate()
    )

    sample_data = [
        ("CUST001", "2026-06-15"),
        ("CUST002", "2026-06-16"),
        ("CUST003", "2026-06-17"),
    ]

    df = spark.createDataFrame(
        sample_data,
        ["customer_id", "created_date"],
    )

    df = df.withColumn("created_date", F.to_date(F.col("created_date")))

    print("Initial DataFrame:")
    df.show()

    last_watermark = get_last_watermark_value(
        dataset="customers",
        watermark_store_path=test_watermark_store,
    )

    initial_incremental_df = filter_incremental_dataframe(
        df=df,
        watermark_column="created_date",
        last_watermark=last_watermark,
    )

    print("Initial load count:", initial_incremental_df.count())

    max_watermark = get_max_watermark_value(
        df=initial_incremental_df,
        watermark_column="created_date",
    )

    stage_watermark_update(
        dataset="customers",
        watermark_column="created_date",
        previous_watermark=last_watermark,
        new_watermark=max_watermark,
        pending_watermark_path=test_pending_watermark,
    )

    commit_staged_watermark_update(
        dataset="customers",
        watermark_store_path=test_watermark_store,
        pending_watermark_path=test_pending_watermark,
    )

    committed_watermark = get_last_watermark_value(
        dataset="customers",
        watermark_store_path=test_watermark_store,
    )

    print("Committed watermark:", committed_watermark)

    second_incremental_df = filter_incremental_dataframe(
        df=df,
        watermark_column="created_date",
        last_watermark=committed_watermark,
    )

    print("Second incremental load count:", second_incremental_df.count())

    assert initial_incremental_df.count() == 3
    assert committed_watermark == "2026-06-17"
    assert second_incremental_df.count() == 0

    print("V9 watermark manager test passed.")

    spark.stop()


if __name__ == "__main__":
    main()