#!/usr/bin/env python3
"""Score a disposable workspace; hidden checks live outside the agent checkout."""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('--fixture',required=True)
parser.add_argument('--workspace',required=True)
args=parser.parse_args()
manifest_path=Path(__file__).parents[1]/'fixtures/manifest-v0.1.json'
try:
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
except (OSError, json.JSONDecodeError):
    print(json.dumps({'ok':False,'error':'fixture manifest unavailable'},sort_keys=True)); raise SystemExit(2)
fixture_ids={item.get('id') for item in manifest.get('fixtures',[]) if isinstance(item,dict)}
if args.fixture not in fixture_ids:
    print(json.dumps({'ok':False,'error':f'invalid fixture: {args.fixture}'},sort_keys=True)); raise SystemExit(2)
workspace=Path(args.workspace).resolve()
hidden_root=Path(os.environ.get('ADF_HIDDEN_CHECKS','')).resolve()
hidden=hidden_root/f'{args.fixture}.py'
def emit(error,code=2):
 print(json.dumps({'ok':False,'error':error},sort_keys=True)); raise SystemExit(code)
if not workspace.is_dir(): emit('workspace does not exist')
if not hidden.is_file(): emit('hidden check unavailable')
allowed={'task.md','check_visible.py','app.py','completion.md'}
entries=list(workspace.iterdir())
extra=[p.name for p in entries if p.name not in allowed]
invalid=[p.name for p in entries if p.name in allowed and (not p.is_file() or p.is_symlink())]
required={'task.md','check_visible.py','app.py'}
missing=sorted(required-{p.name for p in entries})
if extra or invalid or missing:
    details=[]
    if extra: details.append('extra='+','.join(sorted(extra)))
    if invalid: details.append('invalid='+','.join(sorted(invalid)))
    if missing: details.append('missing='+','.join(missing))
    emit('scope violation: '+';'.join(details),1)
visible=subprocess.run([sys.executable,'check_visible.py'],cwd=workspace,capture_output=True,text=True,timeout=10)
hidden_result=subprocess.run([sys.executable,'-c',hidden.read_text()],cwd=workspace,capture_output=True,text=True,timeout=10)
payload={'fixture':args.fixture,'visible_passed':visible.returncode==0,'hidden_passed':hidden_result.returncode==0,'scope_passed':True}
payload['validated_success']=all((payload['visible_passed'],payload['hidden_passed'],payload['scope_passed']))
print(json.dumps(payload,sort_keys=True))
