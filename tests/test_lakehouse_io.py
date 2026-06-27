import tempfile
import unittest
from pathlib import Path

from scripts.lakehouse_io import (
    assert_delta_table_exists,
    build_merge_condition,
    get_lakehouse_write_strategy,
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

    def test_get_lakehouse_write_strategy_defaults_to_overwrite(self):
        config = {}

        result = get_lakehouse_write_strategy(config)

        self.assertEqual(result, "overwrite")

    def test_get_lakehouse_write_strategy_returns_lowercase_value(self):
        config = {"lakehouse_write_strategy": "MERGE"}

        result = get_lakehouse_write_strategy(config)

        self.assertEqual(result, "merge")

    def test_is_delta_table_path_returns_true_when_delta_log_has_commit_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            table_path = Path(temp_dir) / "customer_table"
            delta_log_path = table_path / "_delta_log"
            delta_log_path.mkdir(parents=True)
            (delta_log_path / "00000000000000000000.json").write_text(
                "{}\n",
                encoding="utf-8",
            )

            self.assertTrue(is_delta_table_path(str(table_path)))

    def test_is_delta_table_path_returns_false_when_delta_log_is_empty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            table_path = Path(temp_dir) / "customer_table"
            delta_log_path = table_path / "_delta_log"
            delta_log_path.mkdir(parents=True)

            self.assertFalse(is_delta_table_path(str(table_path)))

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
                "Expected a committed Delta transaction log JSON file",
                str(context.exception),
            )

    def test_build_merge_condition_for_single_key(self):
        result = build_merge_condition(["customer_id"])

        self.assertEqual(
            result,
            "target.customer_id = source.customer_id",
        )

    def test_build_merge_condition_for_multiple_keys(self):
        result = build_merge_condition(["source_system", "source_id"])

        self.assertEqual(
            result,
            "target.source_system = source.source_system "
            "AND target.source_id = source.source_id",
        )

    def test_build_merge_condition_fails_for_empty_keys(self):
        with self.assertRaises(ValueError) as context:
            build_merge_condition([])

        self.assertIn(
            "merge_keys must contain at least one column",
            str(context.exception),
        )

    def test_build_merge_condition_fails_for_invalid_key(self):
        with self.assertRaises(ValueError) as context:
            build_merge_condition(["customer_id", ""])

        self.assertIn(
            "Invalid merge keys",
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()