# Python Metadata Relocation

**Last Updated:** 2026-03-11 09:11:17 PM
**Status:** Completed
**Previous Cycle Archive:** `docs/archive/plans/PLAN_2026-03-08_07-49-04_PM.md`

---

## YELLOW

- [x] Read the scaffold, snapshot-asset, root baseline, contract, and documentation files before editing.
- [x] Run `btca status`; no additional `btca ask ...` lookup was required because this slice stayed within repo-local scaffold file handling.
- [x] Confirm the updated scope: `.python-version`, `pyproject.toml`, and `uv.lock` must exist only in `apps/python` and must not be scaffolded at repo root or in foundation-only output.

## RED

- [x] Updated contract coverage in `tests/` so root Python metadata is absent, Python lane metadata is file-local, JS/foundation presets omit root Python files, and `nurt new` emits `apps/python/uv.lock` instead of root `uv.lock`.

## GREEN

- [x] Removed root `.python-version` and root `pyproject.toml` from scaffold generation, and now write a real `apps/python/.python-version` file beside the lane-local `apps/python/pyproject.toml`.
- [x] Updated lockfile generation so Python-enabled outputs produce `apps/python/uv.lock` while root generation keeps only `bun.lock`.
- [x] Renamed the bundled Python-version snapshot asset to `python_lane_python_version.txt` to match the new placement.

## BLUE

- [x] Revalidated targeted contracts, then reran the full suite with `uv run pytest`.

## Documentation Sync

- [x] Update `PROGRESS.md`.
- [x] Update `docs/LIVING_DOCS.md`.
- [x] Update `docs/ARCHITECTURE.md`.
- [x] Create `docs/session-summaries/SESSION_74_SUMMARY.md`.

## Work Items

- [x] Remove root-scaffolded Python metadata from foundation and all generated repo roots.
- [x] Move generated `.python-version`, `pyproject.toml`, and `uv.lock` into `apps/python` only.
