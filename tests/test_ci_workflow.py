import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class CiWorkflowTests(unittest.TestCase):
    def test_framework_ci_covers_supported_python_and_ledger_append_only_policy(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("3.11", workflow)
        self.assertIn("3.12", workflow)
        self.assertIn("make verify", workflow)
        self.assertIn("check_append_only.py", workflow)
        self.assertIn("github.event.pull_request.base.sha", workflow)
        self.assertIn("check_append_only.py", workflow)
        self.assertIn(" ledger", workflow)
        self.assertNotIn("tests/fixtures/ledger/valid", workflow)
        self.assertIn("fetch-depth: 0", workflow)


if __name__ == "__main__":
    unittest.main()
