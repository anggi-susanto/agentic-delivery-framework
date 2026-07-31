# Tool-agnostic integration

ADF deliberately does not require a specific model, vendor, agent runtime, or multi-agent topology.

## Map the roles, not product names

| ADF role | Possible implementation |
|---|---|
| Implementer | OpenCode, Codex, Claude Code, Hermes, OpenHands, or human developer |
| Design reviewer | Separate agent session, model, or qualified human reviewer |
| Evidence verifier | CI job, independent agent, release engineer, or operator |
| Ledger store | Git-tracked JSON/Markdown, issue system plus immutable export, or internal evidence service |

## Minimum integration contract

Whatever harness is used must be able to:

1. read the task contract and repository policy;
2. execute focused tests/commands;
3. provide a diff for a fresh reviewer;
4. record structured review output;
5. prevent or flag work outside declared scope.

## Suggested adapters

- **Spec Kit:** use ADF lane selection and evidence fields as an extension to `specify → plan → tasks → implement`.
- **Superpowers:** map ADF contracts to brainstorming/design/plan and use its subagent process for implementation; retain ADF's boundary evidence and ledger policy.
- **OpenCode/Codex/Claude Code/Hermes:** inject the selected contract and scope handshake into the agent's repository instructions or task prompt; run review in a distinct session.
- **OpenHands:** run implementation and scheduled verification as automations, while retaining the evidence/ledger data in the source repository.

Vendor/model names belong in project policy, not in the framework's core contract.
