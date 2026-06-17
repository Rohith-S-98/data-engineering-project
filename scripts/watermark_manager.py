import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

DEFAULT_WATERMARK_STORE_PATH = "data/audit/watermark_store.json"
DEFAULT_PENDING_WATERMARK_PATH = "data/audit/pending_watermark_updates.json"


def read_json_file(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        return {}

    with open(path, mode="r", encoding="utf-8") as file:
        return json.load(file)


def write_json_file(file_path: str, data: dict) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def get_last_watermark_value(
    dataset: str,
    watermark_store_path: str = DEFAULT_WATERMARK_STORE_PATH,
) -> Optional[str]:
    watermark_store = read_json_file(watermark_store_path)
    dataset_watermark = watermark_store.get(dataset)

    if not dataset_watermark:
        return None

    return dataset_watermark.get("last_watermark")


def filter_incremental_dataframe(
    df: DataFrame,
    watermark_column: str,
    last_watermark: Optional[str],
) -> DataFrame:
    if watermark_column not in df.columns:
        raise ValueError(f"Watermark column not found in DataFrame: {watermark_column}")

    if not last_watermark:
        print("No previous watermark found. Running full initial load.")
        return df

    print(f"Previous watermark found: {last_watermark}")
    print(f"Filtering records where {watermark_column} > {last_watermark}")

    return df.filter(F.col(watermark_column) > F.to_date(F.lit(last_watermark)))


def get_max_watermark_value(df: DataFrame, watermark_column: str) -> Optional[str]:
    if watermark_column not in df.columns:
        raise ValueError(f"Watermark column not found in DataFrame: {watermark_column}")

    result_row = df.agg(F.max(F.col(watermark_column)).alias("max_watermark")).collect()[0]
    max_watermark = result_row["max_watermark"]

    if max_watermark is None:
        return None

    if hasattr(max_watermark, "isoformat"):
        return max_watermark.isoformat()

    return str(max_watermark)


def stage_watermark_update(
    dataset: str,
    watermark_column: str,
    previous_watermark: Optional[str],
    new_watermark: Optional[str],
    pending_watermark_path: str = DEFAULT_PENDING_WATERMARK_PATH,
) -> None:
    if not new_watermark:
        print("No new watermark found. Skipping watermark staging.")
        return

    pending_updates = read_json_file(pending_watermark_path)
    pending_updates[dataset] = {
        "dataset": dataset,
        "watermark_column": watermark_column,
        "previous_watermark": previous_watermark,
        "new_watermark": new_watermark,
        "status": "PENDING",
        "staged_at": datetime.now(timezone.utc).isoformat(),
    }

    write_json_file(pending_watermark_path, pending_updates)
    print(f"Watermark staged for dataset={dataset}: {previous_watermark} -> {new_watermark}")


def commit_staged_watermark_update(
    dataset: str,
    watermark_store_path: str = DEFAULT_WATERMARK_STORE_PATH,
    pending_watermark_path: str = DEFAULT_PENDING_WATERMARK_PATH,
) -> None:
    pending_updates = read_json_file(pending_watermark_path)

    if dataset not in pending_updates:
        print(f"No pending watermark found for dataset={dataset}. Nothing to commit.")
        return

    pending_update = pending_updates[dataset]
    watermark_store = read_json_file(watermark_store_path)

    watermark_store[dataset] = {
        "dataset": dataset,
        "watermark_column": pending_update["watermark_column"],
        "last_watermark": pending_update["new_watermark"],
        "previous_watermark": pending_update["previous_watermark"],
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "status": "COMMITTED",
    }

    write_json_file(watermark_store_path, watermark_store)

    del pending_updates[dataset]
    write_json_file(pending_watermark_path, pending_updates)

    print(
        f"Watermark committed for dataset={dataset}: "
        f"{pending_update['previous_watermark']} -> {pending_update['new_watermark']}"
    )


def clear_pending_watermark_update(
    dataset: str,
    pending_watermark_path: str = DEFAULT_PENDING_WATERMARK_PATH,
) -> None:
    pending_updates = read_json_file(pending_watermark_path)

    if dataset in pending_updates:
        del pending_updates[dataset]
        write_json_file(pending_watermark_path, pending_updates)
        print(f"Pending watermark cleared for dataset={dataset}.")
