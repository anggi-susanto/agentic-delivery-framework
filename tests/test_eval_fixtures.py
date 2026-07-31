import json
import subprocess
import sys
import tempfile
import unittest
import os
from pathlib import Path

ROOT = Path(__file__).parents[1]
FIXTURES = ROOT / "evals" / "fixtures"
MANIFEST = FIXTURES / "manifest-v0.1.json"


class EvaluationFixtureTests(unittest.TestCase):
    def test_six_fixtures_have_public_brief_visible_check_hidden_check_broken_and_reference_states(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["fixtures"]), 6)
        for entry in manifest["fixtures"]:
            fixture = FIXTURES / entry["id"]
            for relative in ("public/task.md", "public/check_visible.py", "broken/app.py", "reference/app.py"):
                self.assertTrue((fixture / relative).is_file(), f"missing {entry['id']}/{relative}")
            self.assertFalse((ROOT / "evals" / "hidden_checks" / f"{entry['id']}.py").exists())

    def test_prepare_run_excludes_hidden_checks_and_creates_disposable_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, "evals/scripts/prepare_run.py", "f01-fast-doc", temp], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            workspace = Path(payload["workspace"])
            self.assertTrue((workspace / "task.md").is_file())
            self.assertFalse((workspace / "hidden_check.py").exists())

    def test_score_run_rejects_broken_state_and_accepts_reference_state_without_hidden_workspace_leak(self):
        for state, expected in (("broken", False), ("reference", True)):
            with tempfile.TemporaryDirectory() as temp:
                prepare = subprocess.run([sys.executable, "evals/scripts/prepare_run.py", "f01-fast-doc", temp, "--state", state], cwd=ROOT, capture_output=True, text=True, check=False)
                self.assertEqual(prepare.returncode, 0, prepare.stderr)
                workspace = json.loads(prepare.stdout)["workspace"]
                score = subprocess.run([sys.executable, "evals/scripts/score_run.py", "--fixture", "f01-fast-doc", "--workspace", workspace], cwd=ROOT, env={**os.environ, "ADF_HIDDEN_CHECKS": str(Path.home() / ".hermes" / "eval-hidden")}, capture_output=True, text=True, check=False)
                self.assertEqual(score.returncode, 0, score.stderr)
                self.assertEqual(json.loads(score.stdout)["validated_success"], expected)


if __name__ == "__main__":
    unittest.main()
