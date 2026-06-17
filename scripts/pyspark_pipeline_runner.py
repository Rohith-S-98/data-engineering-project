import sys

from scripts.exceptions import DQValidationError, PipelineExecutionError
from scripts.pipeline_config import load_pipeline_config
from scripts.pyspark_bronze_ingestion import run_bronze_ingestion
from scripts.pyspark_gold_canonical import run_pyspark_gold_canonical
from scripts.pyspark_silver_dq import run_pyspark_silver_dq
from scripts.run_metadata import create_pipeline_run, update_pipeline_run
from scripts.watermark_manager import commit_staged_watermark_update


def run_pyspark_pipeline(raise_on_failure: bool = True) -> str:
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
            raise DQValidationError("Pipeline stopped because HIGH severity DQ rules failed.")

        print("\nStep 3: Running Gold Canonical Transformation")
        run_pyspark_gold_canonical()

        commit_staged_watermark_update(
            dataset=config["dataset_name"],
            watermark_store_path=config["watermark_store_file"],
            pending_watermark_path=config["pending_watermark_file"],
        )

        update_pipeline_run(
            run_id=run_id,
            audit_log_file=config["audit_log_file"],
            status="SUCCESS",
        )

        print("\n" + "=" * 70)
        print("PySpark Pipeline Completed Successfully")
        print("=" * 70)
        return "SUCCESS"

    except Exception as error:
        update_pipeline_run(
            run_id=run_id,
            audit_log_file=config["audit_log_file"],
            status="FAILED",
            error_message=str(error),
        )

        print("\n" + "=" * 70)
        print("PySpark Pipeline Failed")
        print(f"Error Type: {type(error).__name__}")
        print(f"Error Message: {error}")
        print("=" * 70)

        if raise_on_failure:
            raise PipelineExecutionError(f"Pipeline execution failed: {error}") from None

        return "FAILED"


if __name__ == "__main__":
    final_status = run_pyspark_pipeline(raise_on_failure=False)
    sys.exit(0 if final_status == "SUCCESS" else 1)
