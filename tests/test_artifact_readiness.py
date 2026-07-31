import importlib.util
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "validate_contract.py"
spec = importlib.util.spec_from_file_location("validate_contract", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ArtifactReadinessTests(unittest.TestCase):
    def load(self, path):
        return json.loads((ROOT / path).read_text(encoding="utf-8"))

    def test_high_risk_readiness_requires_companion_artifacts(self):
        contract = self.load("examples/contracts/high-risk.json")
        errors = module.validate_readiness(contract, None, None)
        self.assertIn("evidence plan is required for high-risk/escalation readiness", errors)
        self.assertIn("scope handshake is required for high-risk/escalation readiness", errors)

    def test_example_readiness_is_valid(self):
        contract = self.load("examples/contracts/high-risk.json")
        evidence = self.load("examples/evidence/schema-migration.json")
        handshake = self.load("examples/handshakes/schema-migration.json")
        self.assertEqual(module.validate_readiness(contract, evidence, handshake), [])

    def test_raw_log_and_secret_like_fields_are_rejected(self):
        contract = self.load("examples/contracts/high-risk.json")
        for field, value in (
            ("claim", "raw-output.log contains result"),
            ("command", "cat logs/raw-output.log"),
            ("environment", "postgres logs/raw-output.txt"),
            ("artifact_ref", "artifacts/raw-output.sha256"),
            ("claim", "raw logfile included"),
            ("command", "raw logfile included"),
            ("environment", "raw logfile included"),
        ):
            with self.subTest(field=field):
                evidence = self.load("examples/evidence/schema-migration.json")
                evidence["proof_items"][0][field] = value
                self.assertTrue(
                    any("must not reference raw logs" in error for error in module.validate_evidence_plan(evidence, contract))
                )
        evidence = self.load("examples/evidence/schema-migration.json")
        evidence["notes"] = "raw-output.log contains password=secret"
        errors = module.validate_evidence_plan(evidence, contract)
        self.assertTrue(any("must not reference raw logs" in error for error in errors))
        self.assertTrue(any("secret-like material" in error for error in errors))
        evidence = self.load("examples/evidence/schema-migration.json")
        evidence["notes"] = "raw logfile included"
        self.assertTrue(
            any("must not reference raw logs" in error for error in module.validate_evidence_plan(evidence, contract))
        )

    def test_evidence_rejects_wrong_shape_and_undeclared_fields(self):
        contract = self.load("examples/contracts/high-risk.json")
        evidence = self.load("examples/evidence/schema-migration.json")
        evidence["notes"] = ["raw logfile"]
        self.assertIn("notes must be a string", module.validate_evidence_plan(evidence, contract))
        evidence = self.load("examples/evidence/schema-migration.json")
        evidence["unexpected"] = "raw logfile"
        self.assertIn("evidence plan contains unknown field: unexpected", module.validate_evidence_plan(evidence, contract))
        evidence = self.load("examples/evidence/schema-migration.json")
        evidence["proof_items"][0]["authorization"] = "Bearer token-value"
        self.assertIn(
            "proof_items[0] contains unknown field: authorization",
            module.validate_evidence_plan(evidence, contract),
        )

    def test_readiness_cli_rejects_missing_companions(self):
        result = subprocess.run(
            ["python3", "scripts/validate_contract.py", "--readiness", "examples/contracts/high-risk.json"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("evidence plan is required", result.stdout)


if __name__ == "__main__":
    unittest.main()
