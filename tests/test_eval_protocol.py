import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class EvaluationProtocolTests(unittest.TestCase):
    def test_manifest_pre_registers_reproducible_paired_crossover_conditions(self):
        manifest_path = ROOT / "evals/protocols/pilot-v0.1.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        required = {
            "version", "fixture_manifest_sha256", "arms", "harness", "model", "sampling",
            "budgets", "scoring", "repetitions", "randomization", "exclusions", "report_version",
        }
        self.assertTrue(required.issubset(manifest))
        self.assertEqual(manifest["design"], "paired-crossover")
        self.assertEqual(set(manifest["arms"]), {"baseline", "adf"})
        self.assertEqual(manifest["repetitions"], 3)
        self.assertEqual(manifest["sampling"]["temperature"], 0)
        self.assertEqual(manifest["sampling"]["seed_policy"], "record-if-supported")
        digest = __import__("hashlib").sha256((ROOT / "evals/fixtures/manifest-v0.1.json").read_bytes()).hexdigest()
        self.assertEqual(manifest["fixture_manifest_sha256"], digest)
        self.assertTrue((ROOT / "evals/scripts/score_run.py").exists())
        self.assertIn("hidden_acceptance", manifest["scoring"]["success_requirements"])
        self.assertIn("timeout", manifest["exclusions"]["count_as_failure"])

    def test_public_protocol_rejects_general_benchmark_claims(self):
        protocol = (ROOT / "docs/evaluation/protocol-v0.1.md").read_text(encoding="utf-8")
        metrics = (ROOT / "docs/evaluation/metrics.md").read_text(encoding="utf-8")
        self.assertIn("MMLU", protocol)
        self.assertIn("GSM8K", protocol)
        self.assertIn("must not be presented", protocol)
        for metric in ("VTSR", "SCR", "HDER", "ECR", "RCR", "MTVS", "CPVS", "ULR", "RR"):
            self.assertIn(metric, metrics)


if __name__ == "__main__":
    unittest.main()
