# Session 107 Summary

## Date and Time

2026-03-14 10:32:20 AM

## Scope

Followed up on the completed multi-project `nurt new` slice by fixing Python workspace ergonomics and improving Textual wizard visual clarity.

## Inputs

- `src/new_repo_template/scaffold.py`
- `src/new_repo_template/interactive_tui.py`
- `src/new_repo_template/version_baseline.py`
- Python and wizard contract suites under `tests/contracts/`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`

## Implementation

- Confirmed via `btca ask -r uv` that uv workspaces intentionally keep one root `.venv`, then fixed member ergonomics by scaffolding `.venv/bin/activate` shims inside Python app/library members that forward to the shared root environment.
- Updated Python library scaffolding so generated libraries now receive their own `.python-version` file just like Python apps.
- Tightened the Textual wizard presentation in `src/new_repo_template/interactive_tui.py` by widening the right-hand summary column, allowing project-name wrapping, and making selected markers more visually distinct.
- Expanded the Python contract coverage so app/library scaffold tests now assert the new activation shim and Python-library `.python-version` behavior.

## Verification

- `uv run pytest`
- `uv run ruff check src/new_repo_template tests/contracts`
- Manual verification: generated a temporary `python + python-lib` workspace, ran `uv sync --package python-app --group dev`, then sourced `apps/python/python-app/.venv/bin/activate` and `packages/python/python-lib/.venv/bin/activate` successfully.

## Documentation Sync

- Updated `PROGRESS.md`.
- Updated `docs/LIVING_DOCS.md`.
- Updated `docs/ARCHITECTURE.md`.

## Outcome

- The reported Python workspace activation issue is fixed for generated Python members, and the wizard is easier to read during target selection and review.
