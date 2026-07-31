# Boundary evidence matrix

Map a task's owned boundary to proof that exercises the boundary itself.

| Owned boundary | Minimum meaningful proof |
|---|---|
| Schema / migration | Fresh database upgrade, constraints, and downgrade/rollback where supported |
| Durable lifecycle / transaction | State transition tests, idempotency, and failure/recovery behavior |
| Concurrency / ownership | Controlled interleavings; stale owner cannot mutate current state |
| Network | DNS/IP/redirect/TLS policy enforced at the actual request boundary |
| Subprocess | Process-group ownership, timeout, cancellation, bounded output, secret exclusion |
| Filesystem publication | Trusted-root/no-follow path behavior, atomic promotion, reconciliation after interruption |
| Destructive operation | Target identity, dry-run or confirmation, recovery/rollback evidence |
| Deployment / restore | Disposable target, health/rollback path, recorded environment |
| UI / pure domain logic | Focused behavior tests; typecheck/build when affected |

Do not turn the table into generic ceremony. Only run proof for boundaries the slice owns or changes.
