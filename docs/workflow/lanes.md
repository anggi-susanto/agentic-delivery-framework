# Lane selection

Choose the least demanding lane that covers the boundary *owned by the change*. Promote immediately when the work discovers a higher-risk boundary.

| Condition | Lane | Review requirement |
|---|---|---|
| Documentation, copy, bounded CSS, test-only, deterministic pure transform | Fast | final review |
| Existing-contract CRUD, forms, UI, or API behavior | Standard | design **or** final review |
| Schema, migration, durable state, media/file path, cross-service contract | High-risk | design and final review |
| Concurrency, hostile URL/file, subprocess, credentials, destructive operation, deployment/restore | Escalation | escalation design and final review |

## Fast

Use a brief: objective, exact files, exclusions, and affected checks. No design review or full runtime proof unless changed paths activate a boundary.

## Standard

Use a condensed contract: measurable outcome, consumed contracts, exact scope, errors, and focused acceptance. Choose design review if behavior is unsettled; otherwise choose final review.

## High-risk and Escalation

Require a full contract, adoption record, independent design review, scope handshake, focused RED/GREEN, boundary-specific verification, fresh final review, and clean-state proof.

## Promotion rule

A consumer of a previously approved high-risk capability remains Standard when it does not create, modify, validate, or execute the underlying risk boundary. For example, a UI displaying a persisted status is not a schema migration. A UI that mutates lifecycle state may be.
