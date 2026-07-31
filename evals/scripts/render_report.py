#!/usr/bin/env python3
"""Render a validated deterministic Markdown evaluation report."""
import json, sys
from pathlib import Path
from eval_validation import validate_summary

def fail(error):
 print(json.dumps({"ok":False,"error":error},sort_keys=True)); return 2

def main():
 if len(sys.argv)!=2:return fail("usage: render_report.py SUMMARY_JSON")
 try: summary=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
 except (OSError,json.JSONDecodeError):return fail("summary unavailable")
 errors=validate_summary(summary)
 if errors:return fail("; ".join(errors))
 lines=["# Evaluation summary","",f"Records: {summary['record_count']}","","| Metric | Baseline | ADF |","|---|---:|---:|"]
 for name in sorted(summary["metrics"]):
  values=summary["metrics"][name];lines.append(f"| {name} | {values.get('baseline')} | {values.get('adf')} |")
 lines += ["","Missing cost runs: "+(", ".join(summary["missing_cost_run_ids"]) or "none")]
 print("\n".join(lines));return 0
if __name__=="__main__":raise SystemExit(main())
