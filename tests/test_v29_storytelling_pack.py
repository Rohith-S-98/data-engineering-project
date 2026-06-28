from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.validate_storytelling_pack import (
    REQUIRED_FILES,
    STORYTELLING_DIR,
    validate_storytelling_file,
    validate_storytelling_pack,
)


class TestV29StorytellingPack(unittest.TestCase):
    def test_current_storytelling_pack_is_valid(self):
        self.assertEqual(validate_storytelling_pack(), [])

    def test_required_storytelling_files_are_registered(self):
        self.assertIn("project_overview_2_minute.md", REQUIRED_FILES)
        self.assertIn("deep_dive_walkthrough.md", REQUIRED_FILES)
        self.assertIn("resume_bullets.md", REQUIRED_FILES)
        self.assertIn("apexon_iqvia_mapping.md", REQUIRED_FILES)
        self.assertIn("mock_interview_questions.md", REQUIRED_FILES)

    def test_storytelling_directory_exists(self):
        self.assertTrue(STORYTELLING_DIR.exists())
        self.assertTrue(STORYTELLING_DIR.is_dir())

    def test_missing_required_term_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            story_dir = Path(tmp_dir)
            path = story_dir / "sample.md"
            path.write_text("This is a long valid storytelling file. " * 30, encoding="utf-8")

            with patch("scripts.validate_storytelling_pack.STORYTELLING_DIR", story_dir):
                issues = validate_storytelling_file("sample.md", ["missing required phrase"])

        self.assertTrue(any("missing required term" in issue for issue in issues))

    def test_short_content_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            story_dir = Path(tmp_dir)
            path = story_dir / "sample.md"
            path.write_text("short content", encoding="utf-8")

            with patch("scripts.validate_storytelling_pack.STORYTELLING_DIR", story_dir):
                issues = validate_storytelling_file("sample.md", ["short"])

        self.assertTrue(any("content is too short" in issue for issue in issues))

    def test_forbidden_phrase_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            story_dir = Path(tmp_dir)
            path = story_dir / "sample.md"
            content = "This is a long file. " * 30 + " guaranteed job "
            path.write_text(content, encoding="utf-8")

            with patch("scripts.validate_storytelling_pack.STORYTELLING_DIR", story_dir):
                issues = validate_storytelling_file("sample.md", ["long file"])

        self.assertTrue(any("forbidden phrase" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
