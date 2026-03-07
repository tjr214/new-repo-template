# TV Input Checklist

Use this checklist to keep TV behavior remote-primary while preserving keyboard/mouse/gamepad fallback support.
Record execution details in `TV_VALIDATION_LOG.md` while completing each section.

## Focus and Navigation Baseline (remote-primary)

- [x] Initial focus lands on the intended primary control (`hasTVPreferredFocus`).
- [x] Focus state is visible on every focusable element.
- [x] D-pad navigation between key sections is deterministic.
- [x] Select/back behavior is deterministic for remote input.

## Keyboard/Mouse/Gamepad Fallback Support

- [x] Keyboard arrows + enter/escape map to the same navigation/actions as remote input.
- [x] Mouse pointer/click can activate the same controls as remote input.
- [x] Gamepad directional/select/back controls map to the same navigation/actions as remote input.
- [x] Input logging confirms keyboard, mouse, and gamepad paths were exercised.

## Android TV Emulator Validation

- [x] Android TV Emulator image boots and app launches cleanly.
- [x] Emulator D-pad navigation validates remote-primary behavior end-to-end.
- [x] Focus recovery is correct after screen transitions and back navigation.

## NVIDIA Shield Validation

- [x] NVIDIA Shield remote-only pass confirms remote-primary behavior.
- [x] NVIDIA Shield keyboard fallback pass completed.
- [x] NVIDIA Shield mouse fallback pass completed.
- [x] NVIDIA Shield gamepad fallback pass completed.
- [x] Results logged with pass/fail notes for each input path.

Note: keyboard fallback was not directly exercised during the 2026-03-07 Shield session; these keyboard checkboxes were closed by explicit user direction for milestone closeout.
