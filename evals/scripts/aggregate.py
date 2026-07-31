#!/usr/bin/env python3
"""Deterministically aggregate validated append-only run records."""
import json, statistics, sys
from pathlib import Path
from eval_validation import validate_run

METRICS=("VTSR","SCR","HDER","ECR","RCR","MTVS","CPVS","ULR","RR")
def emit(payload,code): print(json.dumps(payload,sort_keys=True,separators=(",",":"))); return code
def rate(items,predicate): return round(sum(bool(predicate(x)) for x in items)/len(items),6) if items else None

def main():
 if len(sys.argv)!=2:return emit({"ok":False,"errors":["usage: aggregate.py RUN_DIRECTORY"]},2)
 directory=Path(sys.argv[1])
 if not directory.is_dir():return emit({"ok":False,"errors":["run directory unavailable"]},2)
 records=[];errors=[];ids=set(); hashes={}
 for path in sorted(directory.glob("*.json")):
  try:r=json.loads(path.read_text(encoding="utf-8"))
  except (OSError,json.JSONDecodeError):errors.append("invalid JSON: "+path.name);continue
  for error in validate_run(r): errors.append(path.name+": "+error)
  if validate_run(r):continue
  if r["run_id"] in ids:errors.append("duplicate run_id: "+r["run_id"])
  ids.add(r["run_id"]); hashes.setdefault((r["fixture_id"],r["arm"]),set()).add((r["fixture_revision"],r["prompt_sha256"]));records.append(r)
 for (fixture,arm),values in hashes.items():
  if len(values)>1:errors.append("mismatched fixture/prompt hashes: "+fixture+"/"+arm)
 if errors:return emit({"ok":False,"errors":sorted(errors)},2)
 metrics={m:{} for m in METRICS};missing=[]
 for arm in sorted({r["arm"] for r in records}):
  xs=[r for r in records if r["arm"]==arm];eligible=[r for r in xs if r["outcome"]!="excluded"];success=[r for r in eligible if r["validated_success"]];claimed=[r for r in xs if r["claimed_complete"]]
  missing += [r["run_id"] for r in xs if r["cost_usd"] is None]
  metrics["VTSR"][arm]=rate(eligible,lambda r:r["validated_success"]);metrics["SCR"][arm]=rate(xs,lambda r:r["scope_passed"]);metrics["HDER"][arm]=rate(claimed,lambda r:not r["hidden_passed"])
  required=sum(r["required_evidence_items"] for r in xs);valid=sum(r["valid_evidence_items"] for r in xs);metrics["ECR"][arm]=round(valid/required,6) if required else None
  seeded=sum(r["seeded_defects"] for r in xs);caught=sum(r["caught_seeded_defects"] for r in xs);metrics["RCR"][arm]=round(caught/seeded,6) if seeded else None
  metrics["MTVS"][arm]=statistics.median([r["duration_seconds"] for r in success]) if success else None
  costs=[r["cost_usd"] for r in xs];metrics["CPVS"][arm]=round(sum(costs)/len(success),6) if success and all(c is not None for c in costs) else None
  metrics["ULR"][arm]=rate(xs,lambda r:r["loop_count"]>r["loop_threshold"]);completed=[r for r in xs if r["outcome"]=="completed"];metrics["RR"][arm]=round(sum(r["rework_cycles"] for r in completed)/len(completed),6) if completed else None
 paired={}
 if {"baseline","adf"}.issubset(metrics["VTSR"]):paired["VTSR_delta_adf_minus_baseline"]=round(metrics["VTSR"]["adf"]-metrics["VTSR"]["baseline"],6)
 return emit({"ok":True,"record_count":len(records),"metrics":metrics,"paired_deltas":paired,"bootstrap_seed":0,"missing_cost_run_ids":sorted(missing)},0)
if __name__=="__main__":raise SystemExit(main())
