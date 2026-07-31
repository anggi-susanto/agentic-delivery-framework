import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "ledger" / "valid"


class LedgerTests(unittest.TestCase):
    def copy_fixture(self) -> tempfile.TemporaryDirectory[str]:
        directory = tempfile.TemporaryDirectory()
        shutil.copytree(FIXTURE, Path(directory.name) / "ledger")
        return directory

    def test_valid_ledger_projects_active_finding_and_review_state_deterministically(self):
        from adf.ledger import validate_ledger
        from adf.projections import build_projections

        with self.copy_fixture() as directory:
            ledger = Path(directory) / "ledger"
            self.assertEqual(validate_ledger(ledger), [])
            first = build_projections(ledger)
            second = build_projections(ledger)
            self.assertEqual(first, second)
            self.assertEqual(first["active-findings.json"]["active_findings"], [])
            self.assertEqual(first["review-state.json"]["tasks"]["task-a"]["state"], "approved")

    def test_duplicate_ids_and_invalid_lifecycle_events_are_rejected(self):
        from adf.ledger import validate_ledger

        with self.copy_fixture() as directory:
            ledger = Path(directory) / "ledger"
            duplicate = ledger / "records" / "duplicate.json"
            duplicate.write_text((ledger / "records" / "blocking.json").read_text(), encoding="utf-8")
            errors = validate_ledger(ledger)
            self.assertTrue(any("duplicate record_id" in error for error in errors))

        with self.copy_fixture() as directory:
            ledger = Path(directory) / "ledger"
            event = json.loads((ledger / "events" / "resolution.json").read_text())
            del event["resolution"]["verification_record_id"]
            (ledger / "events" / "resolution.json").write_text(json.dumps(event), encoding="utf-8")
            errors = validate_ledger(ledger)
            self.assertTrue(any("resolved event requires resolution.verification_record_id" in error for error in errors))

        with self.copy_fixture() as directory:
            ledger = Path(directory) / "ledger"
            event = json.loads((ledger / "events" / "resolution.json").read_text())
            event.pop("event_id", None)
            (ledger / "events" / "resolution.json").write_text(json.dumps(event), encoding="utf-8")
            self.assertTrue(any("requires event_id" in error for error in validate_ledger(ledger)))

        with self.copy_fixture() as directory:
            ledger = Path(directory) / "ledger"
            record = json.loads((ledger / "records" / "blocking.json").read_text())
            record["findings"].append(record["findings"][0])
            (ledger / "records" / "blocking.json").write_text(json.dumps(record), encoding="utf-8")
            self.assertTrue(any("duplicate finding_id" in error for error in validate_ledger(ledger)))

        with self.copy_fixture() as directory:
            ledger = Path(directory) / "ledger"
            event = json.loads((ledger / "events" / "resolution.json").read_text())
            event["event"] = "reanchored"
            event["resolution"] = {"rationale": "split"}
            (ledger / "events" / "resolution.json").write_text(json.dumps(event), encoding="utf-8")
            errors = validate_ledger(ledger)
            self.assertTrue(any("reanchored event requires resolution.successor_task_id" in error for error in errors))

    def test_cli_validate_and_project_are_machine_readable_and_write_byte_stable_files(self):
        with self.copy_fixture() as directory:
            ledger = Path(directory) / "ledger"
            command = ["python3", "-m", "adf.cli", "ledger", "validate", str(ledger), "--json"]
            result = subprocess.run(command, cwd=ROOT, env={"PYTHONPATH": str(ROOT / "src")}, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["ok"])
            command = ["python3", "-m", "adf.cli", "ledger", "project", str(ledger), "--json"]
            result = subprocess.run(command, cwd=ROOT, env={"PYTHONPATH": str(ROOT / "src")}, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            before = (ledger / "projections" / "active-findings.json").read_bytes()
            result = subprocess.run(command, cwd=ROOT, env={"PYTHONPATH": str(ROOT / "src")}, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(before, (ledger / "projections" / "active-findings.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
