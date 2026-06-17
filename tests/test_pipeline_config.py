import json
import tempfile
import unittest
from pathlib import Path

from scripts.pipeline_config import REQUIRED_KEYS, load_pipeline_config


class TestPipelineConfig(unittest.TestCase):

    def test_load_pipeline_config_successfully(self):
        config = load_pipeline_config("config/pipeline/local_config.json")

        self.assertIsInstance(config, dict)

        for key in REQUIRED_KEYS:
            self.assertIn(key, config)

    def test_load_pipeline_config_fails_when_file_missing(self):
        with self.assertRaises(ValueError) as context:
            load_pipeline_config("config/pipeline/missing_config.json")

        self.assertIn(
            "Pipeline config file not found",
            str(context.exception),
        )

    def test_load_pipeline_config_fails_when_required_key_missing(self):
        incomplete_config = {
            "environment": "local",
            "raw_data_file": "data/raw/customer_data.csv",
        }

        temp_config_file = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False,
                encoding="utf-8",
            ) as temp_file:
                json.dump(incomplete_config, temp_file)
                temp_config_file = temp_file.name

            with self.assertRaises(ValueError) as context:
                load_pipeline_config(temp_config_file)

            self.assertIn(
                "Missing required pipeline config keys",
                str(context.exception),
            )

        finally:
            if temp_config_file:
                Path(temp_config_file).unlink(missing_ok=True)

    def test_load_pipeline_config_fails_for_unsupported_storage_format(self):
        config = {
            key: "dummy_value"
            for key in REQUIRED_KEYS
        }
        config["storage_format"] = "orc"

        temp_config_file = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False,
                encoding="utf-8",
            ) as temp_file:
                json.dump(config, temp_file)
                temp_config_file = temp_file.name

            with self.assertRaises(ValueError) as context:
                load_pipeline_config(temp_config_file)

            self.assertIn(
                "Unsupported storage_format",
                str(context.exception),
            )

        finally:
            if temp_config_file:
                Path(temp_config_file).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()