# Re-anchor work when its boundary changes

Re-anchoring is a controlled reset of implementation authority. Use it when a task is too broad, a design assumption is invalid, a new risk class appears, or an adopted component makes a planned custom subsystem unnecessary.

## Procedure

1. Preserve the original task and its evidence as history.
2. Mark the old task superseded or split; do not rewrite its review records.
3. Create successor tasks with exact outcomes and dependency edges.
4. Allocate open findings to the successor that owns each concern.
5. Re-run design review for changed contracts; an old approval never automatically transfers.
6. Regenerate status projections from the ledger rather than editing status by hand.

## When to split

Split when one task contains more than one independent security boundary, multiple durable state machines, schema + worker + API + UI + external integration, or more than one independently shippable acceptance story.

Do not split merely to satisfy a reviewer preference. The successor needs a real ownership boundary and an executable outcome.
