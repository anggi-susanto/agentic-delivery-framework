# Evaluation metrics

All metrics are calculated per committed protocol and reported with raw numerator/denominator, uncertainty, failures, and exclusions.

| Metric | Definition | Direction |
|---|---|---|
| VTSR | Validated Task Success Rate = successful eligible runs / eligible runs | higher |
| SCR | Scope Compliance Rate = scope-compliant runs / all runs | higher |
| HDER | Hidden Defect Escape Rate = claimed-complete runs failing hidden acceptance / claimed-complete runs | lower |
| ECR | Evidence Completeness Rate = valid required evidence items / required items | higher |
| RCR | Review Catch Rate = seeded defects caught before acceptance / detectable seeded defects | higher |
| MTVS | Median Time to Validated Success across successful runs | lower |
| CPVS | Cost per Validated Success = total metered cost / successful runs | lower |
| ULR | Unproductive Loop Rate = runs exceeding the predeclared loop threshold / all runs | lower |
| RR | Rework Rate = post-review change cycles / completed runs | lower |

VTSR is primary. Secondary metrics diagnose why an arm differs; they do not justify a broad claim independently.
