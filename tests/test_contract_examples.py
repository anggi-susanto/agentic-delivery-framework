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


class ContractExampleTests(unittest.TestCase):
    def load_fixture(self, relative_path: str) -> dict:
        return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))

    def test_schema_is_valid_json_with_lane_specific_branches(self):
        schema = self.load_fixture("schemas/task-contract.schema.json")
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["properties"]["lane"]["enum"], ["fast", "standard", "high-risk", "escalation"])
        self.assertEqual(len(schema["allOf"][0]["oneOf"]), 4)
        self.assertEqual(schema["allOf"][1]["then"], {"required": ["adoption"]})

    def test_all_lane_examples_are_accepted(self):
        for lane in ("fast", "standard", "high-risk", "escalation"):
            with self.subTest(lane=lane):
                contract = self.load_fixture(f"examples/contracts/{lane}.json")
                self.assertEqual(contract["lane"], lane)
                self.assertEqual(module.validate_contract(contract), [])

    def test_invalid_fixtures_are_rejected_for_their_expected_error(self):
        expected_errors = {
            "invalid-unknown-lane.json": "lane must be one of: escalation, fast, high-risk, standard",
            "invalid-missing-scope.json": "scope.allowed_paths is required",
            "invalid-empty-acceptance.json": "acceptance must be a non-empty list of command strings",
            "invalid-dangerous-boundary-without-adoption.json": "adoption.mechanical_responsibilities is required",
        }
        for fixture, expected_error in expected_errors.items():
            with self.subTest(fixture=fixture):
                errors = module.validate_contract(self.load_fixture(f"tests/fixtures/contracts/{fixture}"))
                self.assertIn(expected_error, errors)

    def test_standard_lane_cannot_own_a_dangerous_boundary_without_adoption(self):
        contract = self.load_fixture("examples/contracts/standard.json")
        contract["risk"]["boundaries"] = ["network"]
        self.assertIn("adoption.mechanical_responsibilities is required", module.validate_contract(contract))


if __name__ == "__main__":
    unittest.main()
