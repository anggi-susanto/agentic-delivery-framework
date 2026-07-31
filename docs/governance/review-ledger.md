# Durable review lineage

A review result is not merely a comment on the latest diff. It is evidence bound to a specific contract, dependencies, reviewer identity, and point in time.

## Immutable record

Keep review records append-only. A record should bind:

- task identity and parent/feature identity where applicable;
- review kind and risk lane;
- exact subject contract path and content hash;
- consumed dependency contracts and hashes;
- relevant decisions/configuration revision;
- actual client, provider, model, variant, and review level;
- raw structured output hash, normalized outcome, findings, and timestamp.

Use `schemas/review-verdict.schema.json` as a portable verdict baseline.

## Finding lifecycle

Give findings stable IDs. A blocking finding prevents approval until one of these explicit events occurs:

- resolved, with fixing artifact and verifying review;
- rejected, with an accountable rationale;
- merged into a canonical duplicate;
- re-anchored to a successor task;
- superseded because an operator-approved contract changes the relevant scope.

A later passing review does **not** silently close an earlier blocker.

## Approval versus readiness

Keep these states distinct:

```text
Planning → Design Approved → Implementation Ready → In Progress
→ Implementation Reviewed → Shipped
```

Design approval means an exact contract passed the needed review. Implementation readiness additionally needs dependencies, a released planning hold, and a scope handshake. A parent task's old pass does not automatically approve a child task.

## Why append-only

This preserves rejected approaches and prevents the same defect from being rediscovered after a task is split, retried, or rewritten. It also provides an auditable answer to: *what was reviewed, against which requirements, and why did the team decide to proceed?*
