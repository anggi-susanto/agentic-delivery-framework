# Agentic Delivery Framework

**Risk-calibrated workflows, executable evidence gates, and durable review lineage for coding agents.**

Agentic Delivery Framework (ADF) is a tool-agnostic baseline for shipping software with coding agents without treating an agent's “done” message as proof. It works with OpenCode, Codex, Claude Code, Hermes, OpenHands, or a human-led workflow.

ADF is not a coding-agent runtime, issue tracker, or generic project-management system. It defines the delivery controls around a runtime: what must be known before work begins, which risks promote a task, what evidence proves a boundary, who independently verifies it, and how findings remain traceable after a plan changes.

## Why

Coding agents make implementation cheap. They do not make requirements unambiguous, subprocesses safe, migrations reversible, or their own reports independently trustworthy.

ADF keeps the routine path lightweight and applies rigorous controls only when a task owns a real risk boundary.

```text
intake
→ adopt / adapt / custom-domain decision
→ risk lane
→ proportional contract
→ independent design review (when required)
→ scope handshake
→ RED → GREEN → affected verification
→ independent evidence verification
→ fresh staged-diff review
→ immutable review lineage + commit
```

## Four delivery lanes

| Lane | Use for | Required controls |
|---|---|---|
| **Fast** | docs, copy, bounded styling, test-only maintenance, deterministic pure transforms | brief scope, focused checks, independent final review |
| **Standard** | UI/API/CRUD behavior consuming frozen contracts | condensed contract, focused RED/GREEN, one independent design **or** final review |
| **High-risk** | schema, migration, durable worker state, cross-service contracts | full contract, design + final review, scope handshake, boundary verification |
| **Escalation** | hostile input, concurrency, subprocesses, secrets, destructive work, deployment/restore | High-risk controls plus adversarial proof at the actual execution boundary |

See [lane selection](docs/workflow/lanes.md) and the [evidence matrix](docs/workflow/evidence-matrix.md).

## Core principles

1. **Adopt first.** Prefer a maintained component and a thin adapter. Custom code must carry unique domain truth.
2. **Risk is owned, not inherited.** A UI consuming an approved service is not automatically high-risk; a slice that changes its state, authority, or execution boundary is.
3. **A plan is not permission.** High-risk and escalation work need an exact contract, review, and scope handshake before code changes.
4. **Evidence is not self-report.** The implementer produces evidence; an independent verifier decides whether it proves the requirement.
5. **Reviews are history, not a mutable latest verdict.** Findings retain stable identity through resolution, rejection, supersession, and re-anchoring.
6. **Autonomy must stop.** Two non-passing review attempts require an operator decision—not an infinite agent loop.

## Quick start

1. Copy the relevant contract template from `templates/` into your repository.
2. Choose a lane using [docs/workflow/lanes.md](docs/workflow/lanes.md).
3. For high-risk/escalation work, complete the adoption record and scope handshake.
4. Validate a JSON contract:

```bash
python3 scripts/validate_contract.py examples/high-risk-migration/contract.json
```

5. Store review records using `schemas/review-verdict.schema.json`; keep historical records append-only.

The provided validator intentionally checks a small portable baseline. It is not a replacement for project-specific tests, CI, security review, or production controls.

## Repository map

- `docs/principles/` — adoption, proportional risk, independent evidence, bounded autonomy.
- `docs/workflow/` — lifecycle, lane selection, scope handshake, boundary evidence.
- `docs/governance/` — review ledger and re-anchoring model.
- `templates/` — drop-in Fast, Standard, and High-risk contract templates.
- `schemas/` — machine-readable review verdict baseline.
- `scripts/` — dependency-free contract validation.
- `examples/` — a lightweight documentation change and a high-risk migration example.

## Relationship to existing projects

ADF complements—not replaces—excellent public projects:

- [GitHub Spec Kit](https://github.com/github/spec-kit): spec-driven authoring and implementation flow.
- [Superpowers](https://github.com/obra/superpowers): skills-driven engineering methodology and subagent workflow.
- [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD): role-based AI development workflows.
- [OpenHands](https://github.com/OpenHands/OpenHands): control plane and runtime for coding agents.
- [OpenCode](https://github.com/opencode-ai/opencode): terminal coding-agent harness.

ADF's narrower contribution is **risk routing, boundary-specific proof, independent verification, and durable finding lineage**.

## Status

This is the initial public baseline extracted from a production-oriented internal delivery practice and rewritten to be generic. APIs, templates, and schemas may evolve before `1.0`.

## License

Apache-2.0. See [LICENSE](LICENSE).

## Contributing

Contributions should preserve the framework's central trade-off: stronger evidence where a task owns real risk, minimal ceremony where it does not. Please avoid adding vendor-specific assumptions to the core.
