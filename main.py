from scripts.create_sample_data import create_raw_customer_data
from scripts.config_driven_dq import run_config_driven_dq


def run_pipeline() -> None:
    print("=" * 60)
    print("Starting End-to-End Data Engineering Pipeline")
    print("=" * 60)

    print("\nStep 1: Creating raw sample data...")
    create_raw_customer_data()

    print("\nStep 2: Running config-driven data quality validation...")
    run_config_driven_dq()

    print("\n" + "=" * 60)
    print("Pipeline completed successfully")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()