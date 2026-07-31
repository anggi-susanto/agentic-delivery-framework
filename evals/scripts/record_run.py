#!/usr/bin/env python3
"""Append one validated telemetry record without overwriting prior data."""
import json
import os
import sys
from pathlib import Path
from eval_validation import validate_run


def fail(error):
    print(json.dumps({"ok":False,"error":error},sort_keys=True)); return 2

if len(sys.argv)!=3: raise SystemExit(fail("usage: record_run.py INPUT_JSON RUN_DIRECTORY"))
try: data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
except (OSError,json.JSONDecodeError): raise SystemExit(fail("input unavailable"))
errors=validate_run(data)
if errors: raise SystemExit(fail("; ".join(errors)))
out=Path(sys.argv[2]).resolve(); out.mkdir(parents=True,exist_ok=True)
target=(out/(data["run_id"]+".json")).resolve()
try: target.relative_to(out)
except ValueError: raise SystemExit(fail("invalid run_id"))
try:
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
except FileExistsError: raise SystemExit(fail("append-only conflict"))
with os.fdopen(fd,"w",encoding="utf-8") as handle:
    handle.write(json.dumps(data,sort_keys=True,separators=(",",":"))+"\n")
print(json.dumps({"ok":True,"path":str(target)},sort_keys=True))
