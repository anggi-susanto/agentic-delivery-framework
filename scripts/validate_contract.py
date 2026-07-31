#!/usr/bin/env python3
"""Validate a small, tool-agnostic agentic delivery contract."""
from __future__ import annotations

import hashlib
import json
import re
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


SECRET_LIKE_REF = re.compile(r"(?i)(?:api[_-]?key|credential|password|secret|token)=|(?:api[_-]?key|credential|password|secret|token)\b")
HEX_DIGEST = re.compile(r"^[a-f0-9]{64}$")
SAFE_ARTIFACT_REF = re.compile(r"^artifacts/[a-z0-9][a-z0-9._/-]*\.sha256$")
RAW_LOG_REF = re.compile(r"(?i)\b(?:raw[-_\s]*(?:log(?:file)?|output)|logs?|stdout|stderr)\b|\.log\b")


def contract_sha256(contract: dict[str, Any]) -> str:
    """Return the canonical JSON SHA-256 binding used by dependent artifacts."""
    payload = json.dumps(contract, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_evidence_plan(evidence: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    allowed_fields = {"version", "task_id", "contract_sha256", "verifier", "proof_items", "notes"}
    errors.extend(f"evidence plan contains unknown field: {field}" for field in sorted(set(evidence) - allowed_fields))
    for field in ("version", "task_id", "contract_sha256", "verifier", "proof_items"):
        if field not in evidence:
            errors.append(f"missing required field: {field}")
    if evidence.get("version") != 1:
        errors.append("version must be 1")
    if evidence.get("task_id") != contract.get("id"):
        errors.append("task_id must match contract.id")
    digest = evidence.get("contract_sha256")
    if not isinstance(digest, str) or not HEX_DIGEST.fullmatch(digest):
        errors.append("contract_sha256 must be a lowercase SHA-256 digest")
    elif digest != contract_sha256(contract):
        errors.append("contract_sha256 must match the contract")
    if not isinstance(evidence.get("verifier"), str) or not evidence.get("verifier", "").strip():
        errors.append("verifier must be a non-empty string")
    proof_items = evidence.get("proof_items")
    if not isinstance(proof_items, list) or not proof_items:
        errors.append("proof_items must be a non-empty list")
        return errors
    for index, item in enumerate(proof_items):
        if not isinstance(item, dict):
            errors.append(f"proof_items[{index}] must be an object")
            continue
        allowed_proof_fields = {"claim", "command", "environment", "artifact_ref"}
        for field in sorted(set(item) - allowed_proof_fields):
            errors.append(f"proof_items[{index}] contains unknown field: {field}")
        for field in ("claim", "command", "environment", "artifact_ref"):
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"proof_items[{index}].{field} is required")
            elif SECRET_LIKE_REF.search(value):
                errors.append(f"proof_items[{index}].{field} must not contain secret-like material")
            elif RAW_LOG_REF.search(value):
                errors.append(f"proof_items[{index}].{field} must not reference raw logs")
        artifact_ref = item.get("artifact_ref")
        if isinstance(artifact_ref, str) and not SAFE_ARTIFACT_REF.fullmatch(artifact_ref):
            errors.append(f"proof_items[{index}].artifact_ref must be a sanitized artifact digest reference")
    notes = evidence.get("notes")
    if notes is not None and not isinstance(notes, str):
        errors.append("notes must be a string")
    if isinstance(notes, str) and SECRET_LIKE_REF.search(notes):
        errors.append("notes must not contain secret-like material")
    if isinstance(notes, str) and RAW_LOG_REF.search(notes):
        errors.append("notes must not reference raw logs")
    return errors


def validate_readiness(
    contract: dict[str, Any], evidence: dict[str, Any] | None, handshake: dict[str, Any] | None
) -> list[str]:
    errors = validate_contract(contract)
    if contract.get("lane") not in {"high-risk", "escalation"}:
        return errors
    if evidence is None:
        errors.append("evidence plan is required for high-risk/escalation readiness")
    else:
        errors.extend(validate_evidence_plan(evidence, contract))
    if handshake is None:
        errors.append("scope handshake is required for high-risk/escalation readiness")
    else:
        errors.extend(validate_scope_handshake(handshake, contract))
    return errors


def validate_scope_handshake(handshake: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = (
        "version", "task_id", "contract_sha256", "lane", "objective", "allowed_paths",
        "frozen_invariants", "required_red_tests", "acceptance_commands", "final_reviewer_route",
        "no_files_changed", "commit_allowed_now",
    )
    for field in required:
        if field not in handshake:
            errors.append(f"missing required field: {field}")
    if handshake.get("version") != 1:
        errors.append("version must be 1")
    if handshake.get("task_id") != contract.get("id"):
        errors.append("task_id must match contract.id")
    if handshake.get("lane") != contract.get("lane"):
        errors.append("lane must match contract.lane")
    digest = handshake.get("contract_sha256")
    if not isinstance(digest, str) or not HEX_DIGEST.fullmatch(digest):
        errors.append("contract_sha256 must be a lowercase SHA-256 digest")
    elif digest != contract_sha256(contract):
        errors.append("contract_sha256 must match the contract")
    if handshake.get("allowed_paths") != contract.get("scope", {}).get("allowed_paths"):
        errors.append("allowed_paths must exactly match contract.scope.allowed_paths")
    if handshake.get("acceptance_commands") != contract.get("acceptance"):
        errors.append("acceptance_commands must exactly match contract.acceptance")
    for field in ("objective", "final_reviewer_route"):
        if not isinstance(handshake.get(field), str) or not handshake[field].strip():
            errors.append(f"{field} must be a non-empty string")
    for field in ("frozen_invariants", "required_red_tests"):
        value = handshake.get(field)
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"{field} must be a non-empty list of strings")
    if handshake.get("no_files_changed") is not True:
        errors.append("no_files_changed must be true before implementation")
    if handshake.get("commit_allowed_now") is not False:
        errors.append("commit_allowed_now must be false before implementation")
    return errors


def load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("JSON root must be an object")
    return loaded


def main(argv: list[str]) -> int:
    readiness = len(argv) > 1 and argv[1] == "--readiness"
    valid_arity = len(argv) in ({3, 5} if readiness else {2})
    if not valid_arity:
        usage = f"{argv[0]} --readiness CONTRACT.json [EVIDENCE.json HANDSHAKE.json]" if readiness else f"{argv[0]} CONTRACT.json"
        print(f"usage: {usage}", file=sys.stderr)
        return 2
    try:
        if readiness:
            contract_path = Path(argv[2])
            contract = load_json(contract_path)
            evidence = handshake = None
            if len(argv) == 5:
                evidence = load_json(Path(argv[3]))
                handshake = load_json(Path(argv[4]))
            errors = validate_readiness(contract, evidence, handshake)
            label = f"readiness: {contract_path}"
        else:
            contract_path = Path(argv[1])
            contract = load_json(contract_path)
            errors = validate_contract(contract)
            label = f"contract: {contract_path}"
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"cannot read artifact: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Valid {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
