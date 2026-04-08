# TV Input Checklist

Use this checklist to keep TV behavior remote-primary while preserving keyboard/mouse/gamepad fallback support.
Record execution details in `TV_VALIDATION_LOG.md` while completing each section.

## Focus and Navigation Baseline (remote-primary)

- [ ] Initial focus lands on the intended primary control (`hasTVPreferredFocus`).
- [ ] Focus state is visible on every focusable element.
- [ ] D-pad navigation between key sections is deterministic.
- [ ] Select/back behavior is deterministic for remote input.

## Keyboard/Mouse/Gamepad Fallback Support

- [ ] Keyboard arrows + enter/escape map to the same navigation/actions as remote input.
- [ ] Mouse pointer/click can activate the same controls as remote input.
- [ ] Gamepad directional/select/back controls map to the same navigation/actions as remote input.
- [ ] Input logging confirms keyboard, mouse, and gamepad paths were exercised.

## Android TV Emulator Validation

- [ ] Android TV Emulator image boots and app launches cleanly.
- [ ] Emulator D-pad navigation validates remote-primary behavior end-to-end.
- [ ] Focus recovery is correct after screen transitions and back navigation.

## NVIDIA Shield Validation

- [ ] NVIDIA Shield remote-only pass confirms remote-primary behavior.
- [ ] NVIDIA Shield keyboard fallback pass completed.
- [ ] NVIDIA Shield mouse fallback pass completed.
- [ ] NVIDIA Shield gamepad fallback pass completed.
- [ ] Results logged with pass/fail notes for each input path.
