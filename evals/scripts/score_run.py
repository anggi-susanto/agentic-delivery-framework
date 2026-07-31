#!/usr/bin/env python3
"""Reserved deterministic scorer interface for the pre-registered protocol.

Issue #9 supplies fixtures and hidden checks; this pre-registration intentionally
refuses collection until those artifacts replace the manifest placeholders.
"""
from __future__ import annotations

import json
import sys


def main() -> int:
    print(json.dumps({
        "ok": False,
        "error": "scoring is unavailable until issue #9 pins fixture revisions and hidden checks",
    }, sort_keys=True))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
