"""Strict stdlib validation for evaluation telemetry."""
from __future__ import annotations
import re

RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
REQUIRED = {
    "run_id", "fixture_id", "arm", "fixture_revision", "prompt_sha256",
    "claimed_complete", "hidden_passed", "scope_passed", "validated_success",
    "outcome", "duration_seconds", "cost_usd", "rework_cycles", "loop_count",
    "required_evidence_items", "valid_evidence_items", "seeded_defects",
    "caught_seeded_defects", "retry_count", "circuit_breaker_triggered",
    "loop_threshold",
}


def validate_run(record: object) -> list[str]:
    if not isinstance(record, dict):
        return ["record must be an object"]
    errors = []
    missing = REQUIRED - set(record)
    extra = set(record) - REQUIRED
    if missing: errors.append("missing fields: " + ",".join(sorted(missing)))
    if extra: errors.append("undeclared fields: " + ",".join(sorted(extra)))
    if errors: return errors
    if not isinstance(record["run_id"], str) or not RUN_ID.fullmatch(record["run_id"]): errors.append("invalid run_id")
    if not isinstance(record["fixture_id"], str) or not record["fixture_id"]: errors.append("invalid fixture_id")
    if not isinstance(record["arm"], str) or record["arm"] not in {"baseline", "adf"}: errors.append("invalid arm")
    if not isinstance(record["fixture_revision"], str) or not record["fixture_revision"]: errors.append("invalid fixture_revision")
    if not isinstance(record["prompt_sha256"], str) or not SHA256.fullmatch(record["prompt_sha256"]): errors.append("invalid prompt_sha256")
    for key in ("claimed_complete", "hidden_passed", "scope_passed", "validated_success", "circuit_breaker_triggered"):
        if not isinstance(record[key], bool): errors.append(f"{key} must be boolean")
    if not isinstance(record["outcome"], str) or record["outcome"] not in {"completed", "timeout", "model_refusal", "harness_crash", "excluded"}: errors.append("invalid outcome")
    for key in ("duration_seconds", "cost_usd"):
        value=record[key]
        if key == "cost_usd" and value is None: continue
        if isinstance(value, bool) or not isinstance(value, (int,float)) or value < 0: errors.append(f"{key} must be non-negative number or null")
    for key in ("rework_cycles", "loop_count", "required_evidence_items", "valid_evidence_items", "seeded_defects", "caught_seeded_defects", "retry_count", "loop_threshold"):
        value=record[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0: errors.append(f"{key} must be non-negative integer")
    if not errors and record["valid_evidence_items"] > record["required_evidence_items"]: errors.append("valid evidence exceeds required evidence")
    if not errors and record["caught_seeded_defects"] > record["seeded_defects"]: errors.append("caught defects exceed seeded defects")
    if not errors:
        expected_success = record["outcome"] == "completed" and record["hidden_passed"] and record["scope_passed"] and record["valid_evidence_items"] == record["required_evidence_items"]
        if record["validated_success"] != expected_success:
            errors.append("validated_success inconsistent with outcome and validation components")
    return errors


def validate_summary(summary: object) -> list[str]:
    if not isinstance(summary, dict): return ["summary must be an object"]
    required={"ok","record_count","metrics","paired_deltas","bootstrap_seed","missing_cost_run_ids"}
    if set(summary)!=required: return ["summary fields mismatch"]
    if summary["ok"] is not True: return ["invalid summary ok"]
    for key in ("record_count", "bootstrap_seed"):
        if isinstance(summary[key], bool) or not isinstance(summary[key], int) or summary[key] < 0:
            return [f"invalid {key}"]
    metric_names={"VTSR","SCR","HDER","ECR","RCR","MTVS","CPVS","ULR","RR"}
    if not isinstance(summary["metrics"],dict) or set(summary["metrics"]) != metric_names: return ["invalid metrics"]
    for metric, arms in summary["metrics"].items():
        if not isinstance(arms, dict): return [f"invalid metric {metric}"]
        for arm, value in arms.items():
            if arm not in {"baseline", "adf"} or (value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)))):
                return [f"invalid metric value {metric}"]
    if not isinstance(summary["paired_deltas"], dict) or any(isinstance(v, bool) or not isinstance(v, (int,float)) for v in summary["paired_deltas"].values()): return ["invalid paired_deltas"]
    if not isinstance(summary["missing_cost_run_ids"], list) or any(not isinstance(x, str) for x in summary["missing_cost_run_ids"]): return ["invalid missing_cost_run_ids"]
    return []
