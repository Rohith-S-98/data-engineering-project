import warnings

warnings.filterwarnings("ignore", category=ResourceWarning)

import tempfile
import unittest
from pathlib import Path

from pyspark.sql import functions as F

from scripts.spark_session import get_spark_session
from scripts.watermark_manager import (
    commit_staged_watermark_update,
    filter_incremental_dataframe,
    get_last_watermark_value,
    get_max_watermark_value,
    stage_watermark_update,
)


class TestWatermarkManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = get_spark_session("TestWatermarkManager")

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_initial_load_stage_commit_and_second_incremental_load(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            watermark_store = str(Path(temp_dir) / "watermark_store.json")
            pending_watermark = str(Path(temp_dir) / "pending_watermark_updates.json")

            df = self.spark.createDataFrame(
                [
                    ("CUST001", "2026-06-15"),
                    ("CUST002", "2026-06-16"),
                    ("CUST003", "2026-06-17"),
                ],
                ["customer_id", "created_date"],
            ).withColumn("created_date", F.to_date(F.col("created_date")))

            last_watermark = get_last_watermark_value("customers", watermark_store)
            initial_incremental_df = filter_incremental_dataframe(df, "created_date", last_watermark)
            max_watermark = get_max_watermark_value(initial_incremental_df, "created_date")

            stage_watermark_update(
                dataset="customers",
                watermark_column="created_date",
                previous_watermark=last_watermark,
                new_watermark=max_watermark,
                pending_watermark_path=pending_watermark,
            )
            commit_staged_watermark_update(
                dataset="customers",
                watermark_store_path=watermark_store,
                pending_watermark_path=pending_watermark,
            )

            committed_watermark = get_last_watermark_value("customers", watermark_store)
            second_incremental_df = filter_incremental_dataframe(df, "created_date", committed_watermark)

            self.assertEqual(initial_incremental_df.count(), 3)
            self.assertEqual(committed_watermark, "2026-06-17")
            self.assertEqual(second_incremental_df.count(), 0)


if __name__ == "__main__":
    unittest.main()
