# Contract Test Scaffolding

This directory hosts generator contract and integration tests for the template.

- `tests/contracts/`: scaffold shape and CLI behavior contracts.
- `tests/integration/`: cross-target generation and command smoke checks.
- `tests/fixtures/`: reusable fixture files for deterministic assertions.

Execution policy:

- Tests must use disposable temporary output directories.
- Baseline tests must not require external credentials.
- Tests must assert deterministic file/script/config outcomes.
- Failure-path tests must verify no partial scaffold artifacts remain.
