import tempfile
import unittest
from pathlib import Path

from scripts.validate_docker_artifacts import validate_docker_artifacts


class TestV19DockerArtifacts(unittest.TestCase):

    def test_current_repo_docker_artifacts_are_valid(self):
        issues = validate_docker_artifacts()

        self.assertEqual(issues, [])

    def test_validation_reports_missing_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            issues = validate_docker_artifacts(Path(temp_dir))

        self.assertIn("missing file: Dockerfile", issues)
        self.assertIn("missing file: .dockerignore", issues)
        self.assertIn("missing file: docker-compose.yml", issues)

    def test_validation_reports_missing_required_snippet(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "Dockerfile").write_text("FROM python:3.11-slim\n", encoding="utf-8")
            (root / ".dockerignore").write_text(".venv\n", encoding="utf-8")
            (root / "docker-compose.yml").write_text("services:\n", encoding="utf-8")

            issues = validate_docker_artifacts(root)

        self.assertTrue(any("Dockerfile missing required snippet" in issue for issue in issues))
        self.assertTrue(any(".dockerignore missing required snippet" in issue for issue in issues))
        self.assertTrue(any("docker-compose.yml missing required snippet" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
