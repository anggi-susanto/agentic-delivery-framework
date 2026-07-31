# Durable review ledger

Store append-only review records under `ledger/records/` and finding lifecycle events under `ledger/events/`.

Pull-request CI compares this directory with the PR base commit and rejects mutation, deletion, or rename of existing ledger artifacts. New append-only entries are allowed.

The JSON fixtures under `tests/fixtures/ledger/` are test data only; they are not the repository ledger.
