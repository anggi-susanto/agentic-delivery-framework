"""Deterministic JSON projections generated from immutable ledger records."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ledger import load_ledger

TERMINAL_FINDING_EVENTS = {"resolved", "rejected", "merged", "reanchored", "superseded"}


def build_projections(root: Path) -> dict[str, dict[str, Any]]:
    records, events = load_ledger(root)
    finding_by_id: dict[str, dict[str, Any]] = {}
    open_ids: set[str] = set()
    task_records: dict[str, dict[str, Any]] = {}
    task_finding_ids: dict[str, set[str]] = {}
    for _, record in records:
        if not isinstance(record, dict) or "_error" in record:
            continue
        for finding in record.get("findings", []):
            if isinstance(finding, dict) and isinstance(finding.get("id"), str):
                finding_by_id[finding["id"]] = finding
        lineage = record.get("lineage", {})
        if isinstance(lineage, dict):
            open_ids.update(x for x in lineage.get("open_finding_ids", []) if isinstance(x, str))
        task_id = record.get("task_id")
        if isinstance(task_id, str):
            task_finding_ids.setdefault(task_id, set()).update(
                finding["id"] for finding in record.get("findings", [])
                if isinstance(finding, dict) and isinstance(finding.get("id"), str)
            )
            previous = task_records.get(task_id)
            if previous is None or (str(record.get("recorded_at", "")), str(record.get("record_id", ""))) > (str(previous.get("recorded_at", "")), str(previous.get("record_id", ""))):
                task_records[task_id] = record
    for _, event in events:
        if isinstance(event, dict) and event.get("event") in TERMINAL_FINDING_EVENTS:
            finding_id = event.get("finding_id")
            if isinstance(finding_id, str):
                open_ids.discard(finding_id)
    active = [finding_by_id[x] for x in sorted(open_ids) if x in finding_by_id]
    tasks: dict[str, dict[str, str]] = {}
    for task_id, record in sorted(task_records.items()):
        outcome = record.get("outcome")
        lineage = record.get("lineage", {})
        task_open = any(finding_id in open_ids for finding_id in task_finding_ids.get(task_id, set())) or (isinstance(lineage, dict) and any(x in open_ids for x in lineage.get("open_finding_ids", [])))
        if outcome == "completed_pass": state = "blocked" if task_open else "approved"
        elif outcome == "completed_with_findings": state = "blocked" if task_open else "reviewed_with_findings"
        elif outcome in {"timeout", "malformed_output", "missing_output"}: state = outcome
        else: state = "review_failed"
        tasks[task_id] = {"latest_record_id": str(record.get("record_id", "")), "state": state}
    return {"active-findings.json": {"active_findings": active}, "review-state.json": {"tasks": tasks}}


def write_projections(root: Path) -> dict[str, dict[str, Any]]:
    outputs = build_projections(root)
    target = root / "projections"
    target.mkdir(exist_ok=True)
    for name, value in outputs.items():
        (target / name).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return outputs

# end
