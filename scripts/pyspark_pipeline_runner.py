from scripts.pipeline_config import load_pipeline_config
from scripts.pyspark_bronze_ingestion import run_bronze_ingestion
from scripts.pyspark_silver_dq import run_pyspark_silver_dq
from scripts.pyspark_gold_canonical import run_pyspark_gold_canonical
from scripts.run_metadata import create_pipeline_run, update_pipeline_run


def run_pyspark_pipeline() -> None:
    config = load_pipeline_config()

    run_id = create_pipeline_run(
        pipeline_name="pyspark_customer_medallion_pipeline",
        environment=config["environment"],
        audit_log_file=config["audit_log_file"],
    )

    print("=" * 70)
    print("Starting PySpark Data Engineering Pipeline")
    print(f"Pipeline Run ID: {run_id}")
    print("=" * 70)

    try:
        print("\nStep 1: Running Bronze Ingestion")
        run_bronze_ingestion()

        print("\nStep 2: Running Silver DQ Validation")
        dq_status = run_pyspark_silver_dq()
        if dq_status == "FAILED":
            raise Exception("Pipeline stopped because HIGH severity DQ rules failed.")

        print("\nStep 3: Running Gold Canonical Transformation")
        run_pyspark_gold_canonical()

        update_pipeline_run(
            run_id=run_id,
            audit_log_file=config["audit_log_file"],
            status="SUCCESS",
        )

        print("\n" + "=" * 70)
        print("PySpark Pipeline Completed Successfully")
        print("=" * 70)

    except Exception as error:
        update_pipeline_run(
            run_id=run_id,
            audit_log_file=config["audit_log_file"],
            status="FAILED",
            error_message=str(error),
        )

        print("\n" + "=" * 70)
        print("PySpark Pipeline Failed")
        print(f"Error: {error}")
        print("=" * 70)

        raise


if __name__ == "__main__":
    run_pyspark_pipeline()