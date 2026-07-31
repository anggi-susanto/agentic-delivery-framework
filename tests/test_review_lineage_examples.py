import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class ReviewLineageExampleTests(unittest.TestCase):
    def load(self, relative_path: str) -> dict:
        return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))

    def test_review_record_schema_requires_distinct_execution_outcomes(self):
        schema = self.load("schemas/review-record.schema.json")
        outcomes = schema["properties"]["outcome"]["enum"]
        self.assertEqual(
            outcomes,
            ["completed_pass", "completed_with_findings", "timeout", "malformed_output", "missing_output"],
        )
        self.assertEqual(schema["$defs"]["finding"]["properties"]["severity"]["enum"], ["blocking", "advisory"])

    def test_finding_event_schema_requires_lifecycle_events(self):
        schema = self.load("schemas/finding-event.schema.json")
        events = schema["properties"]["event"]["enum"]
        self.assertEqual(events, ["opened", "resolved", "rejected", "merged", "reanchored", "superseded"])

    def test_completed_pass_timeout_and_blocking_records_are_distinct(self):
        passed = self.load("examples/reviews/completed-pass.json")
        timeout = self.load("examples/reviews/timeout.json")
        blocking = self.load("examples/reviews/blocking-finding.json")
        advisory = self.load("examples/reviews/advisory-finding.json")
        self.assertEqual(passed["outcome"], "completed_pass")
        self.assertEqual(passed["findings"], [])
        self.assertEqual(timeout["outcome"], "timeout")
        self.assertEqual(blocking["findings"][0]["severity"], "blocking")
        self.assertEqual(blocking["findings"][0]["id"], "FND-001")
        self.assertEqual(advisory["findings"][0]["severity"], "advisory")
        self.assertEqual(advisory["findings"][0]["id"], "FND-002")

    def test_later_pass_keeps_prior_blocker_open_until_resolution_is_referenced(self):
        blocking = self.load("examples/reviews/blocking-finding.json")
        later_pass = self.load("examples/reviews/later-pass-with-open-blocker.json")
        resolved_pass = self.load("examples/reviews/later-pass-after-resolution.json")
        self.assertIn(blocking["record_id"], later_pass["lineage"]["prior_record_ids"])
        self.assertIn("FND-001", later_pass["lineage"]["open_finding_ids"])
        self.assertEqual(later_pass["lineage"]["resolved_finding_event_ids"], [])
        self.assertNotIn("FND-001", resolved_pass["lineage"]["open_finding_ids"])
        self.assertIn("FND-EVT-2026-0001", resolved_pass["lineage"]["resolved_finding_event_ids"])

    def test_resolution_and_reanchor_keep_the_original_finding_id(self):
        resolution = self.load("examples/finding-events/resolution.json")
        reanchor = self.load("examples/finding-events/reanchor.json")
        self.assertEqual(resolution["finding_id"], "FND-001")
        self.assertEqual(reanchor["finding_id"], "FND-001")
        self.assertEqual(reanchor["event"], "reanchored")
        self.assertIn("successor_task_id", reanchor["resolution"])


if __name__ == "__main__":
    unittest.main()
