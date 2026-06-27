from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.validate_adf_artifacts import (
    AdfArtifactValidationError,
    assert_valid_adf_artifacts,
    load_json,
    validate_adf_artifacts,
    validate_dataset,
    validate_linked_service,
    validate_pipeline,
)


class TestV24AdfArtifacts(unittest.TestCase):
    def test_current_adf_artifacts_are_valid(self):
        self.assertEqual(validate_adf_artifacts(), [])

    def test_pipeline_requires_expected_parameters_and_activities(self):
        pipeline = {
            "name": "customer_medallion_adf_pipeline",
            "properties": {
                "parameters": {"run_date": {}, "environment": {}, "trigger_mode": {}},
                "activities": [
                    {"name": "Validate_Runtime_Parameters", "linkedServiceName": {"referenceName": "ls_databricks_customer_pipeline"}, "dependsOn": []},
                    {"name": "Run_API_Ingestion", "linkedServiceName": {"referenceName": "ls_databricks_customer_pipeline"}, "dependsOn": [{"activity": "Validate_Runtime_Parameters"}]},
                    {"name": "Run_Database_Ingestion", "linkedServiceName": {"referenceName": "ls_databricks_customer_pipeline"}, "dependsOn": [{"activity": "Validate_Runtime_Parameters"}]},
                    {"name": "Run_Advanced_DQ_Catalog", "linkedServiceName": {"referenceName": "ls_databricks_customer_pipeline"}, "dependsOn": [{"activity": "Run_API_Ingestion"}, {"activity": "Run_Database_Ingestion"}]},
                    {"name": "Run_Medallion_Orchestrator", "linkedServiceName": {"referenceName": "ls_databricks_customer_pipeline"}, "dependsOn": [{"activity": "Run_Advanced_DQ_Catalog"}]},
                    {"name": "Validate_Runtime_Cleanliness", "linkedServiceName": {"referenceName": "ls_databricks_customer_pipeline"}, "dependsOn": [{"activity": "Run_Medallion_Orchestrator"}]},
                ],
            },
        }

        self.assertEqual(validate_pipeline(pipeline), [])

    def test_pipeline_rejects_broken_dependency_chain(self):
        pipeline = {
            "name": "customer_medallion_adf_pipeline",
            "properties": {
                "parameters": {"run_date": {}, "environment": {}, "trigger_mode": {}},
                "activities": [
                    {"name": "Validate_Runtime_Parameters", "linkedServiceName": {"referenceName": "ls_databricks_customer_pipeline"}, "dependsOn": []},
                    {"name": "Run_API_Ingestion", "linkedServiceName": {"referenceName": "ls_databricks_customer_pipeline"}, "dependsOn": []},
                ],
            },
        }

        issues = validate_pipeline(pipeline)

        self.assertTrue(any("missing pipeline activity" in issue for issue in issues))
        self.assertTrue(any("invalid dependency chain" in issue for issue in issues))

    def test_linked_service_rejects_unsafe_auth_field(self):
        linked_service = {
            "name": "ls_databricks_customer_pipeline",
            "properties": {
                "type": "AzureDatabricks",
                "typeProperties": {
                    "workspaceUrl": "https://example-dev.azuredatabricks.net",
                    "unsafe_password_field": "not_allowed",
                },
            },
        }

        issues = validate_linked_service(linked_service)

        self.assertTrue(any("secret-like token" in issue for issue in issues))

    def test_dataset_requires_core_customer_columns(self):
        dataset = {
            "name": "customer_landing_metadata",
            "format": "csv",
            "columns": ["customer_id"],
            "version": "v24.0.0",
        }

        issues = validate_dataset(dataset)

        self.assertTrue(any("dataset metadata missing column" in issue for issue in issues))

    def test_load_json_raises_for_missing_file(self):
        with self.assertRaises(AdfArtifactValidationError):
            load_json(Path("missing-adf-artifact.json"))

    def test_assert_valid_raises_when_validation_fails(self):
        with patch("scripts.validate_adf_artifacts.validate_adf_artifacts", return_value=["broken"]):
            with self.assertRaises(AdfArtifactValidationError):
                assert_valid_adf_artifacts()


if __name__ == "__main__":
    unittest.main()
