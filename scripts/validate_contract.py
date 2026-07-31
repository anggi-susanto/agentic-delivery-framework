#!/usr/bin/env python3
"""Compatibility wrapper for the pre-0.2 `validate_contract.py` command.

Prefer `adf validate contract CONTRACT.json` or
`adf validate evidence CONTRACT.json EVIDENCE.json HANDSHAKE.json --json`.
This wrapper remains through the 0.1 minor line.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from adf.cli import main  # noqa: E402
from adf.validation import *  # noqa: F403, E402 — legacy import compatibility


if __name__ == "__main__":
    arguments = sys.argv[1:]
    if arguments[:1] == ["--readiness"]:
        arguments = ["validate", "evidence", *arguments[1:]]
    else:
        arguments = ["validate", "contract", *arguments]
    raise SystemExit(main(arguments))
