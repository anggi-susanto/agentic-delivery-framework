"""Validation for append-only review ledgers."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


def _items(directory: Path) -> list[tuple[Path, Any]]:
    if not directory.is_dir():
        return []
    values: list[tuple[Path, Any]] = []
    for path in sorted(directory.glob("*.json")):
        try:
            values.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError) as exc:
            values.append((path, {"_error": str(exc)}))
    return values


def load_ledger(root: Path) -> tuple[list[tuple[Path, Any]], list[tuple[Path, Any]]]:
    return _items(root / "records"), _items(root / "events")


def validate_ledger(root: Path, base_ref: str | None = None) -> list[str]:
    errors: list[str] = []
    records, events = load_ledger(root)
    record_ids: set[str] = set()
    finding_ids: set[str] = set()
    event_ids: set[str] = set()

    for path, record in records:
        if not isinstance(record, dict):
            errors.append(f"record {path.name} must be a JSON object")
            continue
        if "_error" in record:
            errors.append(f"cannot read record {path.name}: {record['_error']}")
            continue
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not record_id:
            errors.append(f"record {path.name} requires record_id")
        elif record_id in record_ids:
            errors.append(f"duplicate record_id: {record_id}")
        else:
            record_ids.add(record_id)
        findings = record.get("findings", [])
        if not isinstance(findings, list):
            errors.append(f"record {path.name} findings must be a list")
            continue
        for finding in findings:
            if not isinstance(finding, dict) or not isinstance(finding.get("id"), str):
                errors.append(f"record {path.name} contains malformed finding")
                continue
            finding_id = finding["id"]
            if finding_id in finding_ids:
                errors.append(f"duplicate finding_id: {finding_id}")
            else:
                finding_ids.add(finding_id)

    for path, event in events:
        if not isinstance(event, dict):
            errors.append(f"event {path.name} must be a JSON object")
            continue
        if "_error" in event:
            errors.append(f"cannot read event {path.name}: {event['_error']}")
            continue
        event_id = event.get("event_id")
        if isinstance(event_id, str) and event_id:
            if event_id in event_ids:
                errors.append(f"duplicate event_id: {event_id}")
            else:
                event_ids.add(event_id)
        else:
            errors.append(f"event {path.name} requires event_id")
        finding_id = event.get("finding_id")
        if finding_id not in finding_ids:
            errors.append(f"event references unknown finding_id: {finding_id}")
        resolution = event.get("resolution")
        if not isinstance(resolution, dict):
            errors.append(f"event {path.name} resolution must be an object")
            continue
        if event.get("event") == "resolved":
            verifier = resolution.get("verification_record_id")
            if not verifier:
                errors.append("resolved event requires resolution.verification_record_id")
            elif verifier not in record_ids:
                errors.append(f"resolved event references unknown verification_record_id: {verifier}")
        if event.get("event") == "reanchored" and not resolution.get("successor_task_id"):
            errors.append("reanchored event requires resolution.successor_task_id")

    if base_ref:
        errors.extend(check_append_only(root, base_ref))
    return errors


def check_append_only(root: Path, base_ref: str) -> list[str]:
    result = subprocess.run(["git", "diff", "--name-status", base_ref, "--", str(root)], capture_output=True, text=True, check=False)
    if result.returncode:
        return [f"cannot diff base ref: {base_ref}"]
    return [f"append-only violation: {line}" for line in result.stdout.splitlines() if line and not line.startswith("A\t")]
