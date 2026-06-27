from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CONFIG_FILES = [
    "config/pipeline/local_config.json",
    "config/rules/customer_dq_rules.json",
    "config/rules/advanced_customer_dq_rule_catalog.json",
    "configs/schema_contracts/bronze_customers_schema.json",
    "configs/schema_contracts/silver_customers_schema.json",
    "config/jobs/customer_medallion_job.json",
    "config/alerts/customer_medallion_alerts.json",
    "config/retries/customer_medallion_retry_policy.json",
    "config/api/customer_api_ingestion_config.json",
    "config/database/customer_database_ingestion_config.json",
]


def validate_config_files(root: Path | str = Path(".")) -> list[str]:
    root_path = Path(root)
    issues: list[str] = []

    for relative_path in CONFIG_FILES:
        file_path = root_path / relative_path
        if not file_path.exists():
            issues.append(f"missing file: {relative_path}")
            continue

        result = subprocess.run(
            [sys.executable, "-m", "json.tool", str(file_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            issues.append(f"invalid json: {relative_path}: {result.stderr.strip()}")

    return issues


def main() -> int:
    issues = validate_config_files()
    if issues:
        print("Config validation FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Config validation SUCCESS")
    print(f"Validated files: {len(CONFIG_FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
