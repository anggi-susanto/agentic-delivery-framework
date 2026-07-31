#!/usr/bin/env python3
"""Score a disposable workspace; hidden checks live outside the agent checkout."""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('--fixture',required=True)
parser.add_argument('--workspace',required=True)
args=parser.parse_args()
workspace=Path(args.workspace).resolve()
hidden_root=Path(os.environ.get('ADF_HIDDEN_CHECKS','')).resolve()
hidden=hidden_root/f'{args.fixture}.py'
def emit(error,code=2):
 print(json.dumps({'ok':False,'error':error},sort_keys=True)); raise SystemExit(code)
if not workspace.is_dir(): emit('workspace does not exist')
if not hidden.is_file(): emit('hidden check unavailable')
allowed={'task.md','check_visible.py','app.py','completion.md'}
extra=[p.name for p in workspace.iterdir() if p.name not in allowed]
if extra: emit('scope violation: '+','.join(sorted(extra)),1)
visible=subprocess.run([sys.executable,'check_visible.py'],cwd=workspace,capture_output=True,text=True,timeout=10)
hidden_result=subprocess.run([sys.executable,'-c',hidden.read_text()],cwd=workspace,capture_output=True,text=True,timeout=10)
payload={'fixture':args.fixture,'visible_passed':visible.returncode==0,'hidden_passed':hidden_result.returncode==0,'scope_passed':True}
payload['validated_success']=all((payload['visible_passed'],payload['hidden_passed'],payload['scope_passed']))
print(json.dumps(payload,sort_keys=True))
