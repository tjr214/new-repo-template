# Interactive TUI Overhaul

**Last Updated:** 2026-03-12 02:54:57 PM
**Status:** In Progress
**Previous Cycle Archive:** `docs/archive/plans/PLAN_2026-03-12_02-32-23_PM.md`

---

## Goal

Replace the current prompt-style `nurt new` interaction with a real, professional Textual wizard that supports direct multi-selection, progressive flow, persistent summary context, and deterministic fallback to plain prompts.

---

## YELLOW

- [x] Read the current interactive flow implementation in `src/new_repo_template/nurt_cli.py` and `src/new_repo_template/interactive_ui.py` before editing.
- [x] Read the current CLI contract coverage in `tests/contracts/test_nurt_cli_contract.py` and `tests/README.md` before editing.
- [x] Read and compare the current architecture/tracker docs in `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, `PLAN.md`, and `PROGRESS.md` before editing.
- [x] Run `btca status` and keep project BTCA resources in sync with `docs/BTCA_RESOURCES.md`.
- [x] Add the missing UI/testing BTCA resources for `textual`, `rich`, and `pytest-textual-snapshot`, then revalidate with `btca status` and `btca resources`.
- [x] Run `btca ask` lookups for Textual widget flow, layout guidance, and testing patterns before coding the wizard implementation.
- [x] Confirm the implementation boundary: preserve the existing plain fallback and CLI contract while upgrading the rich/TTY path to a real Textual wizard.

## RED

- [x] Add failing contract/integration tests in `tests/` for a real Textual wizard target-selection flow.
- [x] Add failing tests for keyboard-driven multi-select behavior and `foundation` exclusivity.
- [x] Add failing tests for conditional auth-step visibility and stale-auth clearing when stepping backward.
- [x] Add failing tests for review-step parity with the resolved scaffold plan.
- [ ] Add failing tests for layout/fallback behaviors that must remain deterministic.

## GREEN

- [x] Introduce a dedicated Textual wizard module for `nurt new` interactive mode.
- [x] Implement a shell layout with progress rail, main step content, summary pane, and footer key hints.
- [x] Replace comma-separated target entry with direct keyboard/mouse multi-selection.
- [x] Implement a conditional auth step that appears only for `web` + `backend`.
- [x] Implement a review/confirm step that returns a typed result to `nurt_cli.py`.
- [x] Preserve existing plain prompt fallback when enhanced UI is unavailable or unsafe.

## BLUE

- [ ] Refine the visual system so the TUI feels deliberate and professional rather than decorative.
- [ ] Harden responsive behavior for narrow terminals and 80x24 baseline layouts.
- [ ] Consolidate validation and state transitions into a single typed wizard-state model.
- [ ] Keep the handoff into scaffold generation minimal and deterministic.
- [x] Re-run targeted tests, then the full suite once the slice is stable.

## Documentation Sync

- [x] Update `PROGRESS.md` as milestones land.
- [x] Update `docs/LIVING_DOCS.md` as the interactive TUI architecture evolves.
- [x] Update `docs/ARCHITECTURE.md` to reflect the Textual wizard model.
- [x] Keep `docs/BTCA_RESOURCES.md` synchronized with project BTCA resources.
- [x] Create a new session summary in `docs/session-summaries/` for this execution cycle.

## Screen Architecture

- [x] Create a persistent wizard shell with header, progress rail, main content pane, summary pane, and footer.
- [x] Implement a welcome step with project name and resolved output path context.
- [x] Implement a target-selection step using direct multi-select widgets.
- [x] Implement a conditional auth-selection step with provider notes.
- [x] Implement a review step that mirrors the resolved scaffold plan.

## Widget Map

- [x] Use Textual app/screen primitives for the wizard shell and transitions.
- [x] Use `SelectionList[str]` for targets and `RadioSet` for auth.
- [x] Use reactive summary widgets that update as selections change.
- [x] Add typed state/result dataclasses for wizard orchestration.

## Test Matrix

- [x] Contract parity: interactive wizard resolves the same plan semantics as explicit CLI flags.
- [x] Interaction: keyboard selection, step navigation, review, and confirmation.
- [x] Validation: `foundation` exclusivity, conditional auth, and fallback behavior.
- [ ] Layout: standard-width and constrained terminal sizes.
- [ ] Optional visual regression coverage if `pytest-textual-snapshot` is adopted.

## Delivery Slices

- [x] Slice 0: BTCA/resource setup plus YELLOW research.
- [x] Slice 1: Textual shell and target-selection flow.
- [x] Slice 2: Conditional auth and review/confirm flow.
- [ ] Slice 3: Responsive behavior, polish, and hardening.
- [ ] Slice 4: Regression coverage, docs sync, and closeout.
