# Adopt first; own the domain boundary

Before building a mechanical capability, ask in this order:

1. Which maintained OSS component, library, CLI, or managed primitive already solves it?
2. Can the team use it directly?
3. If not, can a fixed, pinned adapter solve it?
4. What exact product policy, authorization, provenance, approval, or UX truth remains uniquely owned?
5. What license, supply-chain, operational, and upgrade risks remain?

## Required adoption record

A High-risk or Escalation contract records, for each mechanical responsibility:

- the responsibility and candidate component;
- decision: `adopt`, `adapt`, or `custom-domain`;
- pinned version/configuration or model identifier;
- license and supply-chain review requirement;
- the fixed adapter boundary and normalized output;
- why a custom mechanism is necessary, if one is proposed;
- a deterministic fixture for input, output, and failure behavior.

## Default rule

Do not build custom queues, downloaders, protocol engines, inference engines, renderers, monitoring platforms, backup systems, or deployment platforms merely because an agent can generate them quickly.

Custom code belongs where a generic component cannot own the product truth: authorization, policy, project scope, audit/provenance, approvals, irreversible publication, or distinct user experience.

## Example

A product needs video transcription.

- **Mechanical capability:** speech-to-text inference.
- **Decision:** adapt a pinned ASR engine behind a fixed invocation.
- **Product-owned truth:** who may request transcription, source rights, normalized transcript versioning, human correction, and provenance.
- **Not product-owned:** another general-purpose ASR engine, scheduler, or model runner.

This is an architecture decision, not a claim that adopted components are automatically secure or compliant. Validate licenses, terms, configuration, and execution boundaries separately.
