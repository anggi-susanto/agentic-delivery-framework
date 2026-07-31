import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class CliTests(unittest.TestCase):
    def run_adf(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "-m", "adf.cli", *args],
            cwd=ROOT,
            env={"PYTHONPATH": str(ROOT / "src")},
            capture_output=True,
            text=True,
            check=False,
        )

    def test_validate_contract_emits_machine_readable_success(self):
        result = self.run_adf("validate", "contract", "examples/contracts/fast.json", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {"errors": [], "kind": "contract", "ok": True, "path": "examples/contracts/fast.json"},
        )

    def test_validate_contract_emits_machine_readable_failure(self):
        result = self.run_adf("validate", "contract", "tests/fixtures/contracts/invalid-unknown-lane.json", "--json")
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["kind"], "contract")
        self.assertIn("lane must be one of: escalation, fast, high-risk, standard", payload["errors"])

    def test_validate_evidence_checks_complete_high_risk_readiness(self):
        result = self.run_adf(
            "validate", "evidence", "examples/contracts/high-risk.json",
            "examples/evidence/schema-migration.json", "examples/handshakes/schema-migration.json", "--json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["kind"], "evidence")

    def test_usage_failure_has_deterministic_exit_and_json_error(self):
        result = self.run_adf("validate", "contract", "--json")
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["errors"], ["contract path is required"])


if __name__ == "__main__":
    unittest.main()
