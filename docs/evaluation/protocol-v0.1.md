# ADF evaluation protocol v0.1

This committed protocol is registered **before** comparative results are collected. The intervention is workflow material, not a better model, budget, permissions, or hidden hint.

## Design

Use paired crossover: each task/repetition runs Baseline and ADF under the identical fixture revision, harness/version, model revision, permissions, turn/token/cost/wall-clock budgets, and scorer. Precommit a balanced randomization order. Run three repetitions per task in the pilot and preserve raw run records.

The versioned machine-readable source is [`evals/protocols/pilot-v0.1.json`](../../evals/protocols/pilot-v0.1.json). It records task-manifest digest, arms, harness/model identity, sampling, budgets, scoring command, repetitions, randomization, exclusions, and report version. The manifest is [`evals/fixtures/manifest-v0.1.json`](../../evals/fixtures/manifest-v0.1.json), and its current digest is verified by tests. Fixture revisions intentionally remain placeholders until Issue #9 creates the immutable fixture repositories; collection is prohibited until they are replaced and the digest is amended.

## Success and exclusions

Validated Task Success requires hidden acceptance, project checks, scope policy, and required evidence where applicable. Timeout, refusal, harness crash, and a flaky test after predeclared recheck count as failures. Exclude only a documented outage affecting both arms or predeclared fixture invalidity; report every failure, timeout, and exclusion.

## Claims

Report confidence intervals and eligible-run denominators. Claims must name the fixture set, model/harness revisions, budgets, failure/exclusion policy, and uncertainty. MMLU and GSM8K measure general model capabilities; they **must not be presented** as evidence that ADF improves software-delivery workflow or process quality.

No comparative result exists yet.

## Reproducibility

Before collection, a third party must be able to recover fixture digest, prompts, contract revision, model/harness identity, sampling/seed policy, permissions, numeric budgets, scoring command, randomized order, raw runs, calculations, exclusions, and report renderer from committed artifacts. This v0.1 pre-registration is collection-gated: Issues #9–#11 must add and pin those run artifacts before any result can be recorded.
