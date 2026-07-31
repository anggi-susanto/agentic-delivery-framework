#!/usr/bin/env python3
"""Retrieve and verify the pinned private evaluator bundle outside agent workspaces."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
BOUNDARY = ROOT / "evals" / "evaluator-boundary-v0.1.json"


def fail(message: str) -> int:
    print(json.dumps({"ok": False, "error": message}, sort_keys=True))
    return 2


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fail("evaluator boundary unavailable")
    destination = args.destination.resolve()
    try:
        destination.relative_to(ROOT)
    except ValueError:
        pass
    else:
        return fail("evaluator destination must be outside the agent repository")
    if destination.exists():
        if not destination.is_dir() or any(destination.iterdir()):
            return fail("evaluator destination must be a new or empty directory")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "clone", "--no-checkout", boundary["repository"], str(destination)],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return fail("evaluator retrieval failed")
    result = subprocess.run(
        ["git", "-C", str(destination), "checkout", "--detach", boundary["revision"]],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        shutil.rmtree(destination)
        return fail("evaluator revision unavailable")
    manifest = destination / boundary["manifest_path"]
    if not manifest.is_file() or sha256(manifest) != boundary["manifest_sha256"]:
        shutil.rmtree(destination)
        return fail("evaluator manifest digest mismatch")
    checks = destination / boundary["hidden_checks_subdirectory"]
    if not checks.is_dir() or len(list(checks.glob("*.py"))) != boundary["verification"]["required_files"]:
        shutil.rmtree(destination)
        return fail("evaluator hidden-check bundle invalid")
    print(json.dumps({"ok": True, "hidden_checks": str(checks), "revision": boundary["revision"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
