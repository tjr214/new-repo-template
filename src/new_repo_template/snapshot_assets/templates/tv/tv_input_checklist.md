# TV Input Checklist

Use this checklist to keep TV behavior remote-primary while preserving fallback support.

## Focus and Navigation Baseline (remote-primary)

- [ ] Initial focus lands on the intended primary control (`hasTVPreferredFocus`).
- [ ] Focus state is visible on every focusable element.
- [ ] D-pad navigation between key sections is deterministic.
- [ ] Back-navigation behavior is defined for remote back/menu actions.

## HID Fallback Support

- [ ] Keyboard arrows and enter/escape map to the same navigation/actions as remote input.
- [ ] Mouse pointer/click can activate the same controls as remote input.
- [ ] Gamepad directional/select/back controls map to the same navigation/actions as remote input.
- [ ] Input telemetry/debugging confirms keyboard, mouse, and gamepad paths are exercised.

## Validation Notes

- [ ] AndroidTV emulator checks completed.
- [ ] Manual NVIDIA Shield checklist completed and logged.
