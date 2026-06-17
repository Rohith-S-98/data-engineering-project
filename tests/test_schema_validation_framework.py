from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from scripts.schema_validation_framework import (
    validate_schema,
    print_schema_validation_result,
    SchemaValidationException,
)


def main():
    spark = (
        SparkSession.builder
        .appName("V8 Schema Validation Framework Test")
        .master("local[*]")
        .getOrCreate()
    )

    sample_data = [
        ("CUST001", "Rohith", "S", "rohith@example.com", 9876543210, "Bengaluru", "Karnataka", "2026-06-16", "CSV"),
        ("CUST002", "Anil", "Kumar", "anil@example.com", 9876543211, "Kolar", "Karnataka", "2026-06-16", "API"),
    ]

    df = spark.createDataFrame(
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
    )

    df = df.withColumn("created_date", F.to_date(F.col("created_date")))

    print("Input DataFrame schema:")
    df.printSchema()

    try:
        result = validate_schema(
            df=df,
            contract_path="configs/schema_contracts/silver_customers_schema.json",
            audit_path="data/audit/schema_validation_audit.jsonl",
            raise_on_failure=True,
        )

        print_schema_validation_result(result)

    except SchemaValidationException as error:
        print("Schema validation failed.")
        print(error.to_dict())
        raise

    finally:
        spark.stop()


if __name__ == "__main__":
    main()