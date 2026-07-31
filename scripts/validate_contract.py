#!/usr/bin/env python3
"""Validate a small, tool-agnostic agentic delivery contract."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

LANES = {"fast", "standard", "high-risk", "escalation"}
REQUIRED = {"version", "id", "lane", "outcome", "scope", "acceptance", "risk"}
DANGEROUS_BOUNDARIES = {
    "schema", "durable-state", "transaction", "security-authority",
    "network", "subprocess", "secrets", "destructive", "deployment",
}


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED - contract.keys())
    errors.extend(f"missing required field: {name}" for name in missing)

    if contract.get("version") != 1:
        errors.append("version must be 1")
    if not isinstance(contract.get("id"), str) or not contract.get("id", "").strip():
        errors.append("id must be a non-empty string")

    lane = contract.get("lane")
    if lane not in LANES:
        errors.append(f"lane must be one of: {', '.join(sorted(LANES))}")

    if not isinstance(contract.get("outcome"), str) or not contract.get("outcome", "").strip():
        errors.append("outcome must be a non-empty string")

    scope = contract.get("scope")
    allowed_paths = scope.get("allowed_paths") if isinstance(scope, dict) else None
    if not isinstance(allowed_paths, list) or not allowed_paths or not all(isinstance(path, str) and path.strip() for path in allowed_paths):
        errors.append("scope.allowed_paths is required")

    acceptance = contract.get("acceptance")
    if not isinstance(acceptance, list) or not acceptance or not all(isinstance(item, str) and item.strip() for item in acceptance):
        errors.append("acceptance must be a non-empty list of command strings")

    risk = contract.get("risk")
    boundaries = risk.get("boundaries", []) if isinstance(risk, dict) else []
    if not isinstance(boundaries, list) or not all(item in DANGEROUS_BOUNDARIES for item in boundaries):
        errors.append("risk.boundaries contains an unknown boundary")

    requires_full_evidence = lane in {"high-risk", "escalation"} or bool(set(boundaries) & DANGEROUS_BOUNDARIES)
    if requires_full_evidence:
        adoption = contract.get("adoption")
        if not isinstance(adoption, dict) or not adoption.get("mechanical_responsibilities"):
            errors.append("adoption.mechanical_responsibilities is required")
        else:
            for index, item in enumerate(adoption["mechanical_responsibilities"]):
                if not isinstance(item, dict):
                    errors.append(f"adoption.mechanical_responsibilities[{index}] must be an object")
                    continue
                for field in ("responsibility", "decision", "component", "version", "license_review", "adapter_boundary"):
                    if not isinstance(item.get(field), str) or not item[field].strip():
                        errors.append(f"adoption.mechanical_responsibilities[{index}].{field} is required")
                if item.get("decision") not in {"adopt", "adapt", "custom-domain"}:
                    errors.append(f"adoption.mechanical_responsibilities[{index}].decision must be adopt, adapt, or custom-domain")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} CONTRACT.json", file=sys.stderr)
        return 2
    path = Path(argv[1])
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read contract: {exc}", file=sys.stderr)
        return 2
    errors = validate_contract(contract)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Valid contract: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
