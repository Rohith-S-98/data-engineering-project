import json
import tempfile
import unittest
from pathlib import Path

from scripts.pipeline_config import load_pipeline_config
from scripts.exceptions import PipelineConfigError

class TestPipelineConfig(unittest.TestCase):

    def test_load_pipeline_config_successfully(self):
        config = load_pipeline_config()

        self.assertEqual(config["environment"], "local")
        self.assertIn("raw_data_file", config)
        self.assertIn("dq_rules_file", config)
        self.assertIn("bronze_output_path", config)
        self.assertIn("silver_output_path", config)
        self.assertIn("gold_output_path", config)
        self.assertIn("quarantine_output_path", config)
        self.assertIn("dq_report_file", config)
        self.assertIn("reltio_payload_output_path", config)

    def test_load_pipeline_config_fails_when_file_missing(self):
        with self.assertRaises(PipelineConfigError):
            load_pipeline_config("config/pipeline/missing_config.json")

    def test_load_pipeline_config_fails_when_required_key_missing(self):
        incomplete_config = {
            "environment": "local",
            "raw_data_file": "data/raw/customer_data.csv"
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_config_file = Path(temp_dir) / "bad_config.json"

            with open(temp_config_file, mode="w", encoding="utf-8") as file:
                json.dump(incomplete_config, file)

            with self.assertRaises(PipelineConfigError):
                load_pipeline_config(temp_config_file)


if __name__ == "__main__":
    unittest.main()