#!/usr/bin/env python3
"""Fail when a relative Markdown link points to a missing local file."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
LINK_RE = re.compile(r"\[[^]]+\]\(([^)#]+)")


def missing_links(root: Path = ROOT) -> list[str]:
    missing: list[str] = []
    for document in root.rglob("*.md"):
        if ".git" in document.parts or ".hermes" in document.parts:
            continue
        for destination in LINK_RE.findall(document.read_text(encoding="utf-8")):
            if "://" in destination or destination.startswith("#"):
                continue
            if not (document.parent / destination).resolve().exists():
                missing.append(f"{document.relative_to(root)}: {destination}")
    return missing


def main() -> int:
    missing = missing_links()
    if missing:
        print("Missing internal Markdown links:", *missing, sep="\n", file=sys.stderr)
        return 1
    print("Internal Markdown links passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
