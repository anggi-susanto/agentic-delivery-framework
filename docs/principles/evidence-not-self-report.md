# Evidence is not self-report

An agent's implementation summary is useful input. It is not a delivery verdict.

Separate roles when a task owns a durable, security, runtime, or deployment boundary:

| Role | Owns |
|---|---|
| Implementer | focused RED/GREEN evidence and affected tests |
| Verifier/orchestrator | independent rerun of boundary-relevant acceptance |
| Final reviewer | fresh inspection of staged diff, contract alignment, and disputed evidence |
| CI | deterministic checks against the committed tree |

The same human can perform more than one role in a small team, but an agent must not self-certify the work it implemented.

## Evidence shape

Evidence should be executable and tied to a claim:

```text
Claim: migration can upgrade and downgrade a fresh database.
Command: pytest tests/integration/test_migration_lifecycle.py -q
Observed result: pass
Environment: disposable PostgreSQL service, image/version recorded
Verifier: independent agent or human
```

For a real boundary, prefer proof at the actual boundary over helper-only tests. A mock unit test cannot prove that a subprocess tree is cancelled, a redirect policy is enforced, or a file publication is crash-safe.
