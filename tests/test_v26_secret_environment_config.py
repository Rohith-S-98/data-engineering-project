from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_secret_environment_config import (
    find_potential_hardcoded_credentials,
    is_allowed_literal,
    is_env_reference,
    validate_environment_config,
    validate_secret_environment_config,
)


class TestV26SecretEnvironmentConfig(unittest.TestCase):
    def test_current_secret_environment_config_is_valid(self):
        self.assertEqual(validate_secret_environment_config(), [])

    def test_env_reference_format_validation(self):
        self.assertTrue(is_env_reference("ENV:CUSTOMER_DATABASE_CREDENTIAL"))
        self.assertFalse(is_env_reference("CUSTOMER_DATABASE_CREDENTIAL"))
        self.assertFalse(is_env_reference("ENV:lowercase_value"))

    def test_allowed_placeholder_literals(self):
        self.assertTrue(is_allowed_literal("<set-locally>"))
        self.assertTrue(is_allowed_literal("ENV:CUSTOMER_SOURCE_API_CREDENTIAL"))
        self.assertTrue(is_allowed_literal("placeholder"))
        self.assertFalse(is_allowed_literal("plain-real-value"))

    def test_prod_environment_requires_approval(self):
        config = {
            "environment": "prod",
            "deployment_target": "azure-prod",
            "pipeline_config_path": "config/pipeline/local_config.json",
            "workspace_profile": "prod",
            "catalog_name": "customer_prod",
            "schema_name": "pipeline",
            "requires_approval": False,
            "credential_references": {
                "source_api": "ENV:CUSTOMER_SOURCE_API_CREDENTIAL",
                "database": "ENV:CUSTOMER_DATABASE_CREDENTIAL",
                "databricks_workspace": "ENV:DATABRICKS_WORKSPACE_CREDENTIAL",
                "azure_storage": "ENV:AZURE_STORAGE_CREDENTIAL"
            },
            "runtime_roots": {"data_root": "data", "output_root": "output"}
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "prod.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            issues = validate_environment_config(path, "prod")

        self.assertTrue(any("prod must require approval" in issue for issue in issues))

    def test_invalid_credential_reference_is_rejected(self):
        config = {
            "environment": "dev",
            "deployment_target": "local-dev",
            "pipeline_config_path": "config/pipeline/local_config.json",
            "workspace_profile": "dev",
            "catalog_name": "customer_dev",
            "schema_name": "pipeline",
            "requires_approval": False,
            "credential_references": {
                "source_api": "literal-value",
                "database": "ENV:CUSTOMER_DATABASE_CREDENTIAL",
                "databricks_workspace": "ENV:DATABRICKS_WORKSPACE_CREDENTIAL",
                "azure_storage": "ENV:AZURE_STORAGE_CREDENTIAL"
            },
            "runtime_roots": {"data_root": "data", "output_root": "output"}
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "dev.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            issues = validate_environment_config(path, "dev")

        self.assertTrue(any("source_api" in issue for issue in issues))

    def test_hardcoded_credential_literal_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "config.json"
            path.write_text('{"password": "plain-real-value"}', encoding="utf-8")
            issues = find_potential_hardcoded_credentials(Path(tmp_dir))

        self.assertEqual(len(issues), 1)

    def test_placeholder_credential_literal_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "config.json"
            path.write_text('{"password": "<placeholder>"}', encoding="utf-8")
            issues = find_potential_hardcoded_credentials(Path(tmp_dir))

        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
