from scripts.pyspark_bronze_ingestion import run_bronze_ingestion
from scripts.pyspark_silver_dq import run_pyspark_silver_dq
from scripts.pyspark_gold_canonical import run_pyspark_gold_canonical


def run_pyspark_pipeline() -> None:
    print("=" * 70)
    print("Starting PySpark Data Engineering Pipeline")
    print("=" * 70)

    print("\nStep 1: Running Bronze Ingestion")
    run_bronze_ingestion()

    print("\nStep 2: Running Silver DQ Validation")
    run_pyspark_silver_dq()

    print("\nStep 3: Running Gold Canonical Transformation")
    run_pyspark_gold_canonical()

    print("\n" + "=" * 70)
    print("PySpark Pipeline Completed Successfully")
    print("=" * 70)


if __name__ == "__main__":
    run_pyspark_pipeline()