import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PromptManifestTests(unittest.TestCase):
    def test_every_fixture_has_exactly_one_matched_baseline_and_adf_packet(self):
        fixture_ids = {item["id"] for item in json.loads((ROOT / "evals/fixtures/manifest-v0.1.json").read_text())["fixtures"]}
        manifest = json.loads((ROOT / "evals/prompts/manifest-v0.1.json").read_text())
        self.assertEqual({entry["fixture_id"] for entry in manifest["mappings"]}, fixture_ids)
        self.assertEqual(len(manifest["mappings"]), len(fixture_ids))
        for entry in manifest["mappings"]:
            for key in ("baseline_prompt", "adf_prompt", "contract", "scorer"):
                path = ROOT / entry[key]["path"]
                self.assertTrue(path.is_file(), path)
                self.assertEqual(entry[key]["sha256"], digest(path))
            self.assertEqual(entry["scorer"]["path"], "evals/scripts/score_run.py")
            self.assertEqual(entry["matched_conditions"], {
                "model": "identical-per-pair", "harness": "identical-per-pair",
                "tools": "identical-per-pair", "max_turns": "identical-per-pair",
                "wall_clock": "identical-per-pair", "token_budget": "identical-per-pair",
                "cost_cap": "identical-per-pair", "reviewer": "identical-per-pair",
            })

    def test_baseline_is_not_deliberately_weakened_and_adf_is_the_only_intervention(self):
        baseline = (ROOT / "evals/prompts/baseline.md").read_text()
        adf = (ROOT / "evals/prompts/adf.md").read_text()
        reviewer = (ROOT / "evals/prompts/reviewer.md").read_text()
        self.assertIn("same task brief", baseline)
        self.assertIn("same harness", baseline)
        self.assertIn("Do not withhold", baseline)
        self.assertIn("ADF packet", adf)
        self.assertIn("same model, harness, tools, and budgets", adf)
        self.assertIn("independent review", reviewer)


if __name__ == "__main__":
    unittest.main()
