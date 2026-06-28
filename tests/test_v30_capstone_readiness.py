from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_capstone_readiness import (
    REQUIRED_CATEGORIES,
    REQUIRED_RELEASE_GATES,
    load_capstone_manifest,
    validate_capstone_readiness,
    validate_release_gates,
)


class TestV30CapstoneReadiness(unittest.TestCase):
    def test_current_capstone_manifest_is_valid(self):
        self.assertEqual(validate_capstone_readiness(), [])

    def test_current_manifest_has_required_version_and_baseline(self):
        manifest = load_capstone_manifest()

        self.assertEqual(manifest["version"], "v30.0.0")
        self.assertEqual(manifest["baseline_version"], "v29.0.0")
        self.assertEqual(manifest["status"], "capstone-ready")

    def test_required_categories_are_present(self):
        manifest = load_capstone_manifest()
        categories = {item["name"] for item in manifest["production_readiness_categories"]}

        self.assertEqual(categories, REQUIRED_CATEGORIES)

    def test_required_release_gates_are_present(self):
        manifest = load_capstone_manifest()
        gates = set(manifest["required_release_gates"])

        self.assertTrue(REQUIRED_RELEASE_GATES.issubset(gates))

    def test_v31_and_profile_update_deferral_are_explicit(self):
        manifest = load_capstone_manifest()

        self.assertEqual(manifest["profile_update_status"], "deferred-until-v31-final-phase")
        self.assertIn("v31.0.0 - Live Public API Integration Testing Framework", manifest["post_capstone_backlog"])

    def test_missing_required_gate_is_detected(self):
        manifest = {"required_release_gates": ["python syntax"]}

        issues = validate_release_gates(manifest)

        self.assertTrue(any("missing required release gate" in issue for issue in issues))

    def test_invalid_version_is_rejected(self):
        manifest = load_capstone_manifest()
        manifest["version"] = "v29.0.0"

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            issues = validate_capstone_readiness(path)

        self.assertTrue(any("version must be v30.0.0" in issue for issue in issues))

    def test_missing_evidence_file_is_detected(self):
        manifest = load_capstone_manifest()
        manifest["production_readiness_categories"][0]["evidence"][0] = "missing/evidence/file.md"

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            issues = validate_capstone_readiness(path)

        self.assertTrue(any("evidence file missing" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
