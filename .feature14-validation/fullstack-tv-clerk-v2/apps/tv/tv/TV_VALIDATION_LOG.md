# TV Validation Log

Track execution outcomes for Android TV Emulator and NVIDIA Shield validation.
Use one run ID per end-to-end pass and keep all fields explicit for reproducibility.

## Run Metadata

- Run ID: `ATV-YYYYMMDD-01`
- Date/Time (UTC): `YYYY-MM-DDTHH:MM:SSZ`
- Tester:
- Build Version:
- Git SHA:
- Device / Emulator Profile:

## Android TV Emulator Pass

- Status: [ ] Pending [ ] Pass [ ] Fail
- Remote-primary focus/navigation result:
- Keyboard fallback result:
- Mouse fallback result:
- Gamepad fallback result:
- Notes:

## NVIDIA Shield Pass

- Status: [ ] Pending [ ] Pass [ ] Fail
- Remote-primary focus/navigation result:
- Keyboard fallback result:
- Mouse fallback result:
- Gamepad fallback result:
- Notes:

## Detailed Findings

| Checkpoint ID | Input Path | Expected | Actual | Result | Evidence |
| --- | --- | --- | --- | --- | --- |
| FOCUS-INIT-001 | remote-primary | Initial focus lands on primary control |  |  |  |
| NAV-DPAD-001 | remote-primary | D-pad navigation deterministic |  |  |  |
| FALLBACK-KB-001 | keyboard | Keyboard path matches remote behavior |  |  |  |
| FALLBACK-MOUSE-001 | mouse | Mouse path matches remote behavior |  |  |  |
| FALLBACK-GAMEPAD-001 | gamepad | Gamepad path matches remote behavior |  |  |  |
