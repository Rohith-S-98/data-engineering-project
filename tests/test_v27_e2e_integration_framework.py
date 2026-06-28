from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.run_e2e_integration_tests import (
    IntegrationGate,
    load_manifest,
    render_command,
    run_e2e_manifest,
    select_gates,
)


class TestV27E2EIntegrationFramework(unittest.TestCase):
    def test_current_manifest_loads_and_selects_smoke_gates(self):
        manifest = load_manifest()
        gates = select_gates(manifest, "smoke")
        gate_names = [gate.name for gate in gates]

        self.assertIn("config-validation", gate_names)
        self.assertIn("environment-validation", gate_names)
        self.assertIn("dry-run-orchestrator", gate_names)
        self.assertIn("runtime-cleanliness", gate_names)

    def test_full_mode_includes_full_only_gates(self):
        manifest = load_manifest()
        gates = select_gates(manifest, "full")
        gate_names = [gate.name for gate in gates]

        self.assertIn("adf-artifact-validation", gate_names)
        self.assertIn("powerbi-artifact-validation", gate_names)

    def test_render_command_replaces_tokens(self):
        command = render_command(["{python}", "-m", "sample", "--run-date", "{run_date}"], "2026-06-23")

        self.assertEqual(command[1:], ["-m", "sample", "--run-date", "2026-06-23"])
        self.assertTrue(command[0])

    def test_runner_stops_after_first_failed_gate(self):
        manifest = {
            "default_run_date": "2026-06-23",
            "gates": [
                {"name": "first", "mode": "smoke", "command": ["cmd1"]},
                {"name": "second", "mode": "smoke", "command": ["cmd2"]},
            ],
        }
        calls: list[list[str]] = []

        def fake_runner(command, check=False):
            calls.append(command)
            return subprocess.CompletedProcess(command, returncode=1)

        results = run_e2e_manifest(manifest, mode="smoke", run_date="2026-06-23", command_runner=fake_runner)

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].success)
        self.assertEqual(calls, [["cmd1"]])

    def test_runner_records_successful_gates(self):
        manifest = {
            "default_run_date": "2026-06-23",
            "gates": [
                {"name": "first", "mode": "smoke", "command": ["cmd1"]},
                {"name": "second", "mode": "smoke", "command": ["cmd2"]},
            ],
        }

        def fake_runner(command, check=False):
            return subprocess.CompletedProcess(command, returncode=0)

        results = run_e2e_manifest(manifest, mode="smoke", run_date="2026-06-23", command_runner=fake_runner)

        self.assertEqual([result.name for result in results], ["first", "second"])
        self.assertTrue(all(result.success for result in results))

    def test_manifest_without_gates_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "manifest.json"
            path.write_text('{"gates": []}', encoding="utf-8")

            with self.assertRaises(ValueError):
                load_manifest(path)

    def test_invalid_mode_is_rejected(self):
        manifest = {
            "gates": [
                {"name": "bad", "mode": "unknown", "command": ["cmd"]},
            ]
        }

        with self.assertRaises(ValueError):
            select_gates(manifest, "full")

    def test_integration_gate_dataclass(self):
        gate = IntegrationGate(name="example", command=["cmd"], mode="smoke")

        self.assertEqual(gate.name, "example")
        self.assertEqual(gate.command, ["cmd"])
        self.assertEqual(gate.mode, "smoke")


if __name__ == "__main__":
    unittest.main()
