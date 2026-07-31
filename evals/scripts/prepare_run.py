#!/usr/bin/env python3
"""Create a disposable agent-visible fixture workspace without hidden checks."""
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path

ROOT=Path(__file__).parents[2]
parser=argparse.ArgumentParser()
parser.add_argument("fixture")
parser.add_argument("destination")
parser.add_argument("--state", choices=("broken","reference"), default="broken")
args=parser.parse_args()
source=ROOT/'evals/fixtures'/args.fixture
if not source.is_dir(): raise SystemExit(f'unknown fixture: {args.fixture}')
target=Path(args.destination)/args.fixture
if target.exists(): shutil.rmtree(target)
target.mkdir(parents=True)
shutil.copy2(source/'public/task.md', target/'task.md')
shutil.copy2(source/'public/check_visible.py', target/'check_visible.py')
shutil.copy2(source/args.state/'app.py', target/'app.py')
print(json.dumps({'fixture':args.fixture,'workspace':str(target)},sort_keys=True))
