from scripts.create_sample_data import create_raw_customer_data
from scripts.config_driven_dq import run_config_driven_dq
from scripts.logger_config import setup_logger


logger = setup_logger()


def run_pipeline() -> None:
    logger.info("=" * 60)
    logger.info("Starting End-to-End Data Engineering Pipeline")
    logger.info("=" * 60)

    try:
        logger.info("Step 1: Creating raw sample data")
        create_raw_customer_data()

        logger.info("Step 2: Running config-driven data quality validation")
        run_config_driven_dq()

        logger.info("=" * 60)
        logger.info("Pipeline completed successfully")
        logger.info("=" * 60)

    except Exception as error:
        logger.exception(f"Pipeline failed due to error: {error}")
        raise


if __name__ == "__main__":
    run_pipeline()