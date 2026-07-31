import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_contract.py"
spec = importlib.util.spec_from_file_location("validate_contract", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def valid_contract():
    return {
        "version": 1,
        "id": "example-contract",
        "lane": "high-risk",
        "outcome": "Apply an additive database migration safely.",
        "scope": {"allowed_paths": ["migrations/**", "tests/**"]},
        "adoption": {
            "mechanical_responsibilities": [
                {
                    "responsibility": "database migration execution",
                    "decision": "adopt",
                    "component": "Alembic",
                    "version": "pinned by project lockfile",
                    "license_review": "required",
                    "adapter_boundary": "migration wrapper",
                }
            ]
        },
        "acceptance": ["pytest tests/test_migration.py -q"],
        "risk": {"boundaries": ["schema", "durable-state"]},
    }


class ValidateContractTests(unittest.TestCase):
    def test_valid_high_risk_contract_is_accepted(self):
        self.assertEqual(module.validate_contract(valid_contract()), [])

    def test_high_risk_contract_requires_scope_and_adoption_evidence(self):
        contract = valid_contract()
        contract["scope"] = {}
        contract["adoption"] = {}
        errors = module.validate_contract(contract)
        self.assertIn("scope.allowed_paths is required", errors)
        self.assertIn("adoption.mechanical_responsibilities is required", errors)

    def test_fast_contract_does_not_require_adoption_matrix(self):
        contract = {
            "version": 1,
            "id": "copy-change",
            "lane": "fast",
            "outcome": "Correct one spelling mistake.",
            "scope": {"allowed_paths": ["README.md"]},
            "acceptance": ["python3 scripts/validate_contract.py example.json"],
            "risk": {"boundaries": []},
        }
        self.assertEqual(module.validate_contract(contract), [])


if __name__ == "__main__":
    unittest.main()
