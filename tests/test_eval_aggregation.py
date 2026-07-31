import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class EvaluationAggregationTests(unittest.TestCase):
    def test_aggregation_is_byte_stable_and_distinguishes_hidden_failure_from_success(self):
        with tempfile.TemporaryDirectory() as temp:
            runs = Path(temp) / "runs"
            runs.mkdir()
            fixture = "f01-fast-doc"
            records = [
                {"run_id": "r1", "fixture_id": fixture, "arm": "baseline", "claimed_complete": True, "hidden_passed": False, "scope_passed": True, "validated_success": False, "outcome": "completed", "duration_seconds": 12, "cost_usd": None, "rework_cycles": 1, "loop_count": 0, "required_evidence_items": 2, "valid_evidence_items": 2, "seeded_defects": 0, "caught_seeded_defects": 0, "retry_count": 0, "circuit_breaker_triggered": False, "loop_threshold": 3, "fixture_revision": "pin", "prompt_sha256": "a" * 64},
                {"run_id": "r2", "fixture_id": fixture, "arm": "adf", "claimed_complete": True, "hidden_passed": True, "scope_passed": True, "validated_success": True, "outcome": "completed", "duration_seconds": 8, "cost_usd": 0.10, "rework_cycles": 0, "loop_count": 0, "required_evidence_items": 2, "valid_evidence_items": 2, "seeded_defects": 0, "caught_seeded_defects": 0, "retry_count": 0, "circuit_breaker_triggered": False, "loop_threshold": 3, "fixture_revision": "pin", "prompt_sha256": "b" * 64},
                {"run_id": "r3", "fixture_id": fixture, "arm": "baseline", "claimed_complete": False, "hidden_passed": False, "scope_passed": False, "validated_success": False, "outcome": "timeout", "duration_seconds": 30, "cost_usd": 0.20, "rework_cycles": 2, "loop_count": 4, "required_evidence_items": 2, "valid_evidence_items": 1, "seeded_defects": 0, "caught_seeded_defects": 0, "retry_count": 1, "circuit_breaker_triggered": True, "loop_threshold": 3, "fixture_revision": "pin", "prompt_sha256": "a" * 64},
            ]
            for record in records:
                (runs / f"{record['run_id']}.json").write_text(json.dumps(record), encoding="utf-8")
            first = subprocess.run([sys.executable, "evals/scripts/aggregate.py", str(runs)], cwd=ROOT, capture_output=True, text=True, check=False)
            second = subprocess.run([sys.executable, "evals/scripts/aggregate.py", str(runs)], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(first.stdout, second.stdout)
            summary = json.loads(first.stdout)
            self.assertEqual(summary["metrics"]["VTSR"]["adf"], 1.0)
            self.assertEqual(summary["metrics"]["HDER"]["baseline"], 1.0)
            self.assertEqual(summary["missing_cost_run_ids"], ["r1"])

    def test_inconsistent_success_path_traversal_and_renderer_errors_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bad = {"run_id": "../escape", "fixture_id": "f01-fast-doc", "arm": "baseline", "claimed_complete": True, "hidden_passed": False, "scope_passed": False, "validated_success": True, "outcome": "timeout", "duration_seconds": 1, "cost_usd": -1, "rework_cycles": 0, "loop_count": 0, "required_evidence_items": 1, "valid_evidence_items": 1, "seeded_defects": 0, "caught_seeded_defects": 0, "retry_count": 0, "circuit_breaker_triggered": False, "loop_threshold": 0, "fixture_revision": "pin", "prompt_sha256": "z" * 64}
            source = root / "bad.json"; source.write_text(json.dumps(bad))
            writer = subprocess.run([sys.executable, "evals/scripts/record_run.py", str(source), str(root / "runs")], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(writer.returncode, 2)
            self.assertFalse((root / "escape.json").exists())
            malformed = root / "summary.json"; malformed.write_text("{}")
            renderer = subprocess.run([sys.executable, "evals/scripts/render_report.py", str(malformed)], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(renderer.returncode, 2)
            self.assertTrue(json.loads(renderer.stdout)["ok"] is False)
            schema_invalid = root / "schema-invalid.json"
            schema_invalid.write_text(json.dumps({"ok": True, "record_count": True, "metrics": {name: {"baseline": "bad"} for name in ("VTSR", "SCR", "HDER", "ECR", "RCR", "MTVS", "CPVS", "ULR", "RR")}, "paired_deltas": {}, "bootstrap_seed": True, "missing_cost_run_ids": [1]}))
            renderer = subprocess.run([sys.executable, "evals/scripts/render_report.py", str(schema_invalid)], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(renderer.returncode, 2)
            self.assertTrue(json.loads(renderer.stdout)["ok"] is False)
            non_hashable = root / "non-hashable.json"
            non_hashable.write_text(json.dumps({"run_id": "bad", "fixture_id": "f01-fast-doc", "arm": {}, "claimed_complete": False, "hidden_passed": False, "scope_passed": False, "validated_success": False, "outcome": {}, "duration_seconds": 1, "cost_usd": None, "rework_cycles": 0, "loop_count": 0, "required_evidence_items": 1, "valid_evidence_items": 0, "seeded_defects": 0, "caught_seeded_defects": 0, "retry_count": 0, "circuit_breaker_triggered": False, "loop_threshold": 0, "fixture_revision": "pin", "prompt_sha256": "a" * 64}))
            aggregate = subprocess.run([sys.executable, "evals/scripts/aggregate.py", str(root)], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(aggregate.returncode, 2)
            self.assertEqual(json.loads(aggregate.stdout)["ok"], False)
            self.assertNotIn("Traceback", aggregate.stderr)
            schema_negative = root / "schema-negative.json"
            schema_negative.write_text(json.dumps({"ok": True, "record_count": 0, "metrics": {name: {} for name in ("VTSR", "SCR", "HDER", "ECR", "RCR", "MTVS", "CPVS", "ULR", "RR")}, "paired_deltas": {}, "bootstrap_seed": -1, "missing_cost_run_ids": []}))
            renderer = subprocess.run([sys.executable, "evals/scripts/render_report.py", str(schema_negative)], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(renderer.returncode, 2)
            self.assertTrue(json.loads(renderer.stdout)["ok"] is False)

    def test_duplicate_ids_and_mismatched_hashes_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            runs = Path(temp) / "runs"; runs.mkdir()
            record = {"run_id": "same", "fixture_id": "f01-fast-doc", "arm": "baseline", "claimed_complete": True, "hidden_passed": True, "scope_passed": True, "validated_success": True, "outcome": "completed", "duration_seconds": 1, "cost_usd": 1, "rework_cycles": 0, "loop_count": 0, "required_evidence_items": 2, "valid_evidence_items": 2, "seeded_defects": 0, "caught_seeded_defects": 0, "retry_count": 0, "circuit_breaker_triggered": False, "loop_threshold": 3, "fixture_revision": "pin", "prompt_sha256": "a" * 64}
            (runs / "a.json").write_text(json.dumps(record)); (runs / "b.json").write_text(json.dumps(record))
            result = subprocess.run([sys.executable, "evals/scripts/aggregate.py", str(runs)], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertIn("duplicate run_id", json.loads(result.stdout)["errors"][0])


if __name__ == "__main__":
    unittest.main()
