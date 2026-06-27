from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.validate_repo_hygiene import (
    RepoHygieneValidationError,
    assert_valid_repo_hygiene,
    validate_required_tokens,
    validate_repo_hygiene,
    validate_tracked_files,
)


class TestV2301RepoHygiene(unittest.TestCase):
    def test_repository_hygiene_is_valid_for_current_repo(self):
        issues = validate_repo_hygiene()
        self.assertEqual(issues, [])

    def test_disallows_tracked_generated_runtime_files(self):
        tracked_files = [
            "data/raw/customer_data.csv",
            "output/runtime_parameters/runtime_parameters_test.json",
            "data/bronze/customer_bronze/part-0000.snappy.parquet",
        ]

        issues = validate_tracked_files(tracked_files)

        self.assertTrue(any("data/raw/customer_data.csv" in issue for issue in issues))
        self.assertTrue(any("output/runtime_parameters/runtime_parameters_test.json" in issue for issue in issues))
        self.assertTrue(any("part-0000.snappy.parquet" in issue for issue in issues))

    def test_allows_runtime_placeholder_files(self):
        tracked_files = [
            "output/runtime_parameters/.gitkeep",
            "output/dq_reports/.gitkeep",
            "data/bronze/.gitkeep",
        ]

        issues = validate_tracked_files(tracked_files)

        self.assertEqual(issues, [])

    def test_required_ignore_tokens_are_reported_when_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
            (root / ".dockerignore").write_text(".git\n", encoding="utf-8")

            issues = validate_required_tokens(root)

            self.assertTrue(any("missing .gitignore token" in issue for issue in issues))
            self.assertTrue(any("missing .dockerignore token" in issue for issue in issues))

    def test_assert_valid_repo_hygiene_raises_when_git_ls_files_fails(self):
        failed_process = subprocess.CompletedProcess(
            args=["git", "ls-files"],
            returncode=1,
            stdout="",
            stderr="not a git repository",
        )
        with patch("scripts.validate_repo_hygiene.subprocess.run", return_value=failed_process):
            with self.assertRaises(RepoHygieneValidationError):
                assert_valid_repo_hygiene()


if __name__ == "__main__":
    unittest.main()
