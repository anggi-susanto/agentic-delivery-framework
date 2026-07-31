# Threats to validity

- **Small samples:** pilot estimates are uncertain; report intervals and avoid generalization.
- **Benchmark contamination:** public fixtures/prompts may be known to models; record provenance and revisions.
- **Evaluator leakage:** hidden checks must never enter the agent workspace or prompt.
- **Hidden-test construction bias:** include realistic failure modes and publish scoring rationale.
- **Model drift:** pin or record model revision and execution date.
- **Order effects:** use precommitted paired crossover randomization.
- **Harness and permission drift:** hold versions, tools, environment, and permissions constant per pair.
- **Cost-model uncertainty:** state pricing/metering source and compute assumptions.
- **Flakiness/outages:** apply the same predeclared failure/exclusion rule to both arms.
