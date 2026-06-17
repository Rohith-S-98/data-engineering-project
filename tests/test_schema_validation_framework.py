import warnings

warnings.filterwarnings("ignore", category=ResourceWarning)

import tempfile
import unittest
from pathlib import Path

from pyspark.sql import functions as F

from scripts.schema_validation_framework import SchemaValidationException, validate_schema
from scripts.spark_session import get_spark_session


class TestSchemaValidationFramework(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = get_spark_session("TestSchemaValidationFramework")

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_schema_validation_passes_for_silver_customer_schema(self):
        sample_data = [
            ("CUST001", "Rohith", "S", "rohith@example.com", 9876543210, "Bengaluru", "Karnataka", "2026-06-16", "CSV"),
            ("CUST002", "Anil", "Kumar", "anil@example.com", 9876543211, "Kolar", "Karnataka", "2026-06-16", "API"),
        ]

        df = self.spark.createDataFrame(
            sample_data,
            [
                "customer_id",
                "first_name",
                "last_name",
                "email",
                "phone",
                "city",
                "state",
                "created_date",
                "source_system",
            ],
        ).withColumn("created_date", F.to_date(F.col("created_date")))

        with tempfile.TemporaryDirectory() as temp_dir:
            result = validate_schema(
                df=df,
                contract_path="configs/schema_contracts/silver_customers_schema.json",
                audit_path=str(Path(temp_dir) / "schema_validation_audit.jsonl"),
                raise_on_failure=True,
            )

        self.assertEqual(result.status, "PASSED")
        self.assertEqual(result.total_issues, 0)

    def test_schema_validation_fails_when_required_column_missing(self):
        df = self.spark.createDataFrame(
            [("CUST001", "Rohith")],
            ["customer_id", "first_name"],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(SchemaValidationException):
                validate_schema(
                    df=df,
                    contract_path="configs/schema_contracts/silver_customers_schema.json",
                    audit_path=str(Path(temp_dir) / "schema_validation_audit.jsonl"),
                    raise_on_failure=True,
                )


if __name__ == "__main__":
    unittest.main()
