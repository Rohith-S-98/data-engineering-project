from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_databricks_bundle_structure import (
    DatabricksBundleValidationError,
    assert_valid_databricks_bundle_structure,
    validate_databricks_bundle_structure,
)


class TestV23DatabricksBundleStructure(unittest.TestCase):
    def test_repository_databricks_bundle_structure_is_valid(self):
        issues = validate_databricks_bundle_structure()
        self.assertEqual(issues, [])

    def test_valid_temp_bundle_structure_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_valid_bundle_structure(root)

            issues = validate_databricks_bundle_structure(root)

            self.assertEqual(issues, [])

    def test_missing_databricks_yml_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "resources").mkdir(parents=True)
            (root / "deployment/databricks").mkdir(parents=True)
            (root / "resources/customer_medallion_job.yml").write_text(_valid_job_resource(), encoding="utf-8")
            (root / "deployment/databricks/README.md").write_text("deployment notes", encoding="utf-8")

            issues = validate_databricks_bundle_structure(root)

            self.assertIn("missing file: databricks.yml", issues)

    def test_missing_required_root_token_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_valid_bundle_structure(root)
            (root / "databricks.yml").write_text("bundle:\n  name: wrong-name\n", encoding="utf-8")

            issues = validate_databricks_bundle_structure(root)

            self.assertTrue(any("name: data-engineering-project" in issue for issue in issues))

    def test_assert_valid_bundle_raises_for_invalid_structure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            with self.assertRaises(DatabricksBundleValidationError):
                assert_valid_databricks_bundle_structure(root)

    def test_missing_job_task_token_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_valid_bundle_structure(root)
            (root / "resources/customer_medallion_job.yml").write_text(
                "resources:\n  jobs:\n    customer_medallion_pipeline_job:\n      tasks: []\n",
                encoding="utf-8",
            )

            issues = validate_databricks_bundle_structure(root)

            self.assertTrue(any("validate_python_project" in issue for issue in issues))


def _write_valid_bundle_structure(root: Path) -> None:
    (root / "resources").mkdir(parents=True, exist_ok=True)
    (root / "deployment/databricks").mkdir(parents=True, exist_ok=True)
    (root / "databricks.yml").write_text(_valid_root_bundle(), encoding="utf-8")
    (root / "resources/customer_medallion_job.yml").write_text(_valid_job_resource(), encoding="utf-8")
    (root / "deployment/databricks/README.md").write_text("deployment notes", encoding="utf-8")


def _valid_root_bundle() -> str:
    return """bundle:
  name: data-engineering-project
include:
  - resources/*.yml
targets:
  dev:
    mode: development
  prod:
    mode: production
"""


def _valid_job_resource() -> str:
    return """resources:
  jobs:
    customer_medallion_pipeline_job:
      tasks:
        - task_key: validate_python_project
        - task_key: validate_config_files
        - task_key: run_pipeline_dry_run
        - task_key: run_runtime_cleanliness
"""


if __name__ == "__main__":
    unittest.main()
