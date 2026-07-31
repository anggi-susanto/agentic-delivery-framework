import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "validate_contract.py"
spec = importlib.util.spec_from_file_location("validate_contract", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class ArtifactValidationTests(unittest.TestCase):
    def load_json(self, relative_path: str) -> dict:
        return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))

    def test_high_risk_artifacts_are_accepted_when_bound_to_contract(self):
        contract = self.load_json("examples/contracts/high-risk.json")
        evidence = self.load_json("examples/evidence/schema-migration.json")
        handshake = self.load_json("examples/handshakes/schema-migration.json")
        self.assertEqual(module.validate_evidence_plan(evidence, contract), [])
        self.assertEqual(module.validate_scope_handshake(handshake, contract), [])

    def test_evidence_requires_a_safe_artifact_reference(self):
        contract = self.load_json("examples/contracts/high-risk.json")
        evidence = self.load_json("examples/evidence/schema-migration.json")
        evidence["proof_items"][0].pop("artifact_ref")
        self.assertIn(
            "proof_items[0].artifact_ref is required",
            module.validate_evidence_plan(evidence, contract),
        )

    def test_evidence_rejects_secret_like_artifact_reference(self):
        contract = self.load_json("examples/contracts/high-risk.json")
        evidence = self.load_json("examples/evidence/schema-migration.json")
        evidence["proof_items"][0]["artifact_ref"] = "logs/postgres_password=supersecret.txt"
        self.assertIn(
            "proof_items[0].artifact_ref must not contain secret-like material",
            module.validate_evidence_plan(evidence, contract),
        )

    def test_handshake_rejects_scope_expansion(self):
        contract = self.load_json("examples/contracts/high-risk.json")
        handshake = self.load_json("examples/handshakes/schema-migration.json")
        handshake["allowed_paths"].append("deploy/**")
        self.assertIn(
            "allowed_paths must exactly match contract.scope.allowed_paths",
            module.validate_scope_handshake(handshake, contract),
        )

    def test_handshake_requires_pre_change_commit_hold(self):
        contract = self.load_json("examples/contracts/high-risk.json")
        handshake = self.load_json("examples/handshakes/schema-migration.json")
        handshake["commit_allowed_now"] = True
        self.assertIn(
            "commit_allowed_now must be false before implementation",
            module.validate_scope_handshake(handshake, contract),
        )


if __name__ == "__main__":
    unittest.main()
