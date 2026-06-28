from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.live_public_api_integration import (
    PublicApiRegistryError,
    PublicApiResponseError,
    get_nested_value,
    load_registry,
    normalize_records,
    run_public_api_integration,
    validate_registry,
)


class TestV31PublicApiIntegration(unittest.TestCase):
    def test_current_registry_is_valid(self):
        registry = load_registry()

        self.assertEqual(registry["version"], "v31.0.0")
        self.assertTrue(registry["ci_safe_mode"])
        self.assertEqual(len(registry["sources"]), 2)

    def test_mock_integration_writes_raw_and_normalized_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry = _build_temp_registry(root)
            registry_path = root / "registry.json"
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            summaries = run_public_api_integration(registry_path)

            self.assertEqual(len(summaries), 1)
            self.assertEqual(summaries[0].ingestion_mode, "mock")
            self.assertEqual(summaries[0].normalized_records, 1)
            self.assertTrue((root / "raw.json").exists())
            self.assertTrue((root / "normalized.csv").exists())

            with (root / "normalized.csv").open("r", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(rows[0]["source_name"], "unit_test_reference_api")
            self.assertEqual(rows[0]["country_code"], "IN")
            self.assertEqual(rows[0]["ingestion_mode"], "mock")

    def test_nested_value_reader_supports_dot_paths(self):
        record = {"name": {"common": "India"}, "region": "Asia"}

        self.assertEqual(get_nested_value(record, "name.common"), "India")
        self.assertEqual(get_nested_value(record, "region"), "Asia")
        self.assertIsNone(get_nested_value(record, "missing.field"))

    def test_normalize_records_adds_metadata_columns(self):
        source = {
            "source_name": "unit_test_reference_api",
            "field_mapping": {"name.common": "country_name", "cca2": "country_code"},
        }
        records = [{"name": {"common": "India"}, "cca2": "IN"}]

        normalized = normalize_records(source, records, "mock")

        self.assertEqual(normalized[0]["source_name"], "unit_test_reference_api")
        self.assertEqual(normalized[0]["ingestion_mode"], "mock")
        self.assertEqual(normalized[0]["record_index"], "1")
        self.assertEqual(normalized[0]["country_name"], "India")

    def test_registry_rejects_live_enabled_ci_unsafe_mode(self):
        registry = _build_minimal_registry()
        registry["ci_safe_mode"] = False

        with self.assertRaises(PublicApiRegistryError):
            validate_registry(registry)

    def test_registry_rejects_non_env_endpoint_reference(self):
        registry = _build_minimal_registry()
        registry["sources"][0]["endpoint_reference"] = "plain-url"

        with self.assertRaises(PublicApiRegistryError):
            validate_registry(registry)

    def test_missing_required_response_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry = _build_temp_registry(root)
            mock_path = root / "mock.json"
            mock_path.write_text(json.dumps([{"name": {"common": "India"}}]), encoding="utf-8")
            registry_path = root / "registry.json"
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            with self.assertRaises(PublicApiResponseError):
                run_public_api_integration(registry_path)

    def test_live_mode_requires_endpoint_environment_variable(self):
        registry = _build_minimal_registry()
        registry["sources"][0]["live_enabled"] = True

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            mock_path = root / "mock.json"
            schema_path = root / "schema.json"
            mock_path.write_text(json.dumps([{"cca2": "IN"}]), encoding="utf-8")
            schema_path.write_text(json.dumps({"version": "v31.0.0"}), encoding="utf-8")
            registry["sources"][0]["mock_response_path"] = str(mock_path)
            registry["sources"][0]["schema_contract_path"] = str(schema_path)
            registry["sources"][0]["raw_landing_path"] = str(root / "raw.json")
            registry["sources"][0]["normalized_csv_path"] = str(root / "normalized.csv")
            registry_path = root / "registry.json"
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            with patch.dict("os.environ", {}, clear=True):
                with self.assertRaises(PublicApiRegistryError):
                    run_public_api_integration(registry_path, allow_live=True)


def _build_temp_registry(root: Path) -> dict:
    mock_path = root / "mock.json"
    schema_path = root / "schema.json"
    mock_path.write_text(
        json.dumps([
            {
                "name": {"common": "India"},
                "cca2": "IN",
                "region": "Asia",
                "population": 1400000000,
            }
        ]),
        encoding="utf-8",
    )
    schema_path.write_text(json.dumps({"version": "v31.0.0"}), encoding="utf-8")

    registry = _build_minimal_registry()
    registry["sources"][0]["mock_response_path"] = str(mock_path)
    registry["sources"][0]["schema_contract_path"] = str(schema_path)
    registry["sources"][0]["raw_landing_path"] = str(root / "raw.json")
    registry["sources"][0]["normalized_csv_path"] = str(root / "normalized.csv")
    return registry


def _build_minimal_registry() -> dict:
    return {
        "version": "v31.0.0",
        "registry_name": "unit_test_registry",
        "ci_safe_mode": True,
        "manual_execution_only": True,
        "sources": [
            {
                "source_name": "unit_test_reference_api",
                "enabled": True,
                "live_enabled": False,
                "endpoint_reference": "ENV:UNIT_TEST_PUBLIC_API_URL",
                "http_method": "GET",
                "auth_type": "none",
                "timeout_seconds": 10,
                "expected_status_code": 200,
                "response_type": "json",
                "mock_response_path": "data/api/mock_live_countries_response.json",
                "raw_landing_path": "output/live_api/raw/unit_test_reference_api.json",
                "normalized_csv_path": "output/live_api/normalized/unit_test_reference_api.csv",
                "schema_contract_path": "configs/schema_contracts/live_public_api_schema.json",
                "required_fields": ["cca2"],
                "field_mapping": {"cca2": "country_code"},
            }
        ],
    }


if __name__ == "__main__":
    unittest.main()
