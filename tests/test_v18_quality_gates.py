from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.validate_config_files import validate_config_files
from scripts.validate_python_project import iter_python_files, validate_python_files
from scripts.validate_release_tag import read_current_version
from scripts.validate_runtime_cleanliness import validate_runtime_cleanliness


class TestV18QualityGates(unittest.TestCase):
    def test_python_validator_detects_syntax_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bad_file = Path(temp_dir) / "bad.py"
            bad_file.write_text("def broken(:\n", encoding="utf-8")

            errors = validate_python_files((str(bad_file),))

            self.assertEqual(len(errors), 1)
            self.assertIn("bad.py", errors[0])

    def test_python_file_discovery_finds_python_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            script_dir = root / "scripts"
            script_dir.mkdir()
            file_path = script_dir / "sample.py"
            file_path.write_text("print('ok')\n", encoding="utf-8")

            files = iter_python_files((str(script_dir),))

            self.assertEqual(files, [file_path])

    def test_config_validator_reports_missing_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            issues = validate_config_files(temp_dir)

            self.assertTrue(issues)
            self.assertIn("missing file", issues[0])

    def test_read_current_version_from_readme(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            readme = Path(temp_dir) / "README.md"
            readme.write_text("# Demo\n\nCurrent Version: v18.0.0\n", encoding="utf-8")

            self.assertEqual(read_current_version(readme), "v18.0.0")

    def test_runtime_cleanliness_returns_git_issues(self):
        with patch(
            "scripts.validate_runtime_cleanliness.find_tracked_runtime_files",
            return_value=["output/alerts/alert_events.csv"],
        ), patch(
            "scripts.validate_runtime_cleanliness.find_dirty_runtime_paths",
            return_value=[],
        ):
            issues = validate_runtime_cleanliness()

            self.assertEqual(len(issues), 1)
            self.assertIn("tracked runtime file", issues[0])


if __name__ == "__main__":
    unittest.main()
