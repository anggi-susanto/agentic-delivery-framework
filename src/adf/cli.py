"""Machine-readable ADF validation CLI."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .validation import validate_contract, validate_readiness
from .ledger import validate_ledger
from .projections import write_projections


def _read(path: str) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def _emit(kind: str, path: str, errors: list[str], as_json: bool) -> None:
    if as_json:
        print(json.dumps({"errors": errors, "kind": kind, "ok": not errors, "path": path}, sort_keys=True))
    elif errors:
        for error in errors:
            print(f"ERROR: {error}")
    else:
        print(f"Valid {kind}: {path}")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in args
    args = [arg for arg in args if arg != "--json"]
    base_ref = None
    if "--base-ref" in args:
        index = args.index("--base-ref")
        if index + 1 >= len(args):
            _emit("ledger", "", ["--base-ref requires a Git ref"], as_json)
            return 2
        base_ref = args[index + 1]
        del args[index:index + 2]
    if len(args) >= 2 and args[0] == "ledger" and args[1] in {"validate", "project"}:
        if len(args) != 3:
            _emit("ledger", "", ["ledger directory is required"], as_json)
            return 2
        root = Path(args[2])
        errors = validate_ledger(root, base_ref)
        if args[1] == "project" and not errors:
            outputs = write_projections(root)
            if as_json:
                print(json.dumps({"errors": [], "kind": "ledger-project", "ok": True, "path": str(root), "outputs": sorted(outputs)}, sort_keys=True))
            else:
                print(f"Projected ledger: {root}")
            return 0
        _emit("ledger", str(root), errors, as_json)
        return 1 if errors else 0
    if len(args) < 2 or args[0] != "validate" or args[1] not in {"contract", "evidence"}:
        _emit("usage", "", ["usage: adf validate {contract|evidence} ... [--json]"], as_json)
        return 2
    kind = args[1]
    paths = args[2:]
    if kind == "contract" and not paths:
        _emit(kind, "", ["contract path is required"], as_json)
        return 2
    if kind == "contract" and len(paths) != 1:
        _emit(kind, "", ["contract accepts exactly one path"], as_json)
        return 2
    if kind == "evidence" and len(paths) not in {1, 3}:
        _emit(kind, "", ["evidence requires contract, evidence plan, and scope handshake paths"], as_json)
        return 2
    try:
        contract = _read(paths[0])
        if kind == "contract":
            errors = validate_contract(contract)
        elif len(paths) == 1:
            errors = validate_readiness(contract, None, None)
        else:
            errors = validate_readiness(contract, _read(paths[1]), _read(paths[2]))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _emit(kind, paths[0] if paths else "", [f"cannot read artifact: {exc}"], as_json)
        return 2
    _emit(kind, paths[0], errors, as_json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
