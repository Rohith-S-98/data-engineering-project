import tempfile
import unittest
from pathlib import Path

from scripts.lakehouse_io import (
    assert_delta_table_exists,
    get_storage_format,
    is_delta_table_path,
)


class TestLakehouseIO(unittest.TestCase):

    def test_get_storage_format_defaults_to_parquet(self):
        config = {}

        result = get_storage_format(config)

        self.assertEqual(result, "parquet")

    def test_get_storage_format_returns_lowercase_value(self):
        config = {"storage_format": "DELTA"}

        result = get_storage_format(config)

        self.assertEqual(result, "delta")

    def test_is_delta_table_path_returns_true_when_delta_log_exists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            table_path = Path(temp_dir) / "customer_table"
            delta_log_path = table_path / "_delta_log"
            delta_log_path.mkdir(parents=True)

            self.assertTrue(is_delta_table_path(str(table_path)))

    def test_is_delta_table_path_returns_false_when_delta_log_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            table_path = Path(temp_dir) / "customer_table"
            table_path.mkdir(parents=True)

            self.assertFalse(is_delta_table_path(str(table_path)))

    def test_assert_delta_table_exists_raises_for_non_delta_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            table_path = Path(temp_dir) / "customer_table"
            table_path.mkdir(parents=True)

            with self.assertRaises(ValueError) as context:
                assert_delta_table_exists(
                    table_path=str(table_path),
                    table_name="customers",
                )

            self.assertIn(
                "Expected _delta_log folder was not found",
                str(context.exception),
            )


if __name__ == "__main__":
    unittest.main()