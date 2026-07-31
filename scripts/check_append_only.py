#!/usr/bin/env python3
"""Reject edits, deletes, and renames of ledger artifacts relative to a Git ref."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from adf.ledger import check_append_only  # noqa: E402


if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} BASE_REF LEDGER_DIR", file=sys.stderr)
    raise SystemExit(2)

errors = check_append_only(Path(sys.argv[2]), sys.argv[1])
for error in errors:
    print(f"ERROR: {error}")
raise SystemExit(1 if errors else 0)
