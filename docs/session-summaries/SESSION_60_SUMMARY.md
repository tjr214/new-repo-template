# Session 60 Summary

## Date and Time

2026-03-03 03:26:36 PM

## Scope

Hardened generated TV Android local-run flow after emulator bring-up surfaced build-path failures, and updated generated `.gitignore` baseline to always ignore `node_modules` across scaffold outputs.

## YELLOW

- Read implementation and contract context before edits:
  - `src/new_repo_template/scaffold.py`
  - `src/new_repo_template/snapshot_assets/templates/workspace_packages/mobile_package.json`
  - `src/new_repo_template/snapshot_assets/templates/workspace_packages/tv_package.json`
  - `src/new_repo_template/snapshot_assets/templates/root_gitignore.txt`
  - `tests/contracts/test_mobile_tv_scaffold_contract.py`
  - `tests/contracts/test_tv_android_build_profile_contract.py`
  - `tests/contracts/test_security_baseline_contract.py`
  - `docs/MOBILE_TV_SETUP.md`
  - `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`
- Ran BTCA dependency-context lookups for Expo/TV compatibility and Android build behavior:
  - `btca ask -r expo-docs -r react-native-tvos -r expo-tv-config -q "For an Expo TV app using react-native-tvos with Expo SDK 55, what exact react, react-native, and react-native-tvos versions should be used to avoid Android build/prebuild mismatches?" --sub-agent`
  - `btca ask -r expo-docs -r react-native-tvos -q "When running expo run:android for a TV app, can mismatched react-native/react-native-tvos versions cause Gradle runtime errors, and what remediation does Expo recommend?" --sub-agent`
  - `btca ask -r expo-docs -q "For Expo SDK 55 Android projects, what Gradle wrapper version is expected/compatible for expo run:android? Is Gradle 9 supported?" --sub-agent`

## RED

- Added/expanded failing contracts:
  - `tests/contracts/test_security_baseline_contract.py`
    - assert generated root `.gitignore` includes `node_modules/` and `**/node_modules/`
  - `tests/contracts/test_mobile_tv_scaffold_contract.py`
    - assert Expo-compatible dependency pins for generated mobile/tv manifests
  - `tests/contracts/test_tv_android_build_profile_contract.py`
    - assert TV scaffold includes deterministic local Android wrapper patch flow and helper script
- Verified RED:
  - `uv run pytest tests/contracts/test_mobile_tv_scaffold_contract.py tests/contracts/test_security_baseline_contract.py tests/contracts/test_tv_android_build_profile_contract.py`
  - Result: 4 failed / 6 passed (expected RED)

## GREEN

- Implemented scaffold/template updates:
  - Added generated root `.gitignore` node_modules guards:
    - `src/new_repo_template/snapshot_assets/templates/root_gitignore.txt`
    - `.gitignore`
  - Aligned Expo mobile/TV baseline dependency pins:
    - `src/new_repo_template/snapshot_assets/templates/workspace_packages/mobile_package.json`
    - `src/new_repo_template/snapshot_assets/templates/workspace_packages/tv_package.json`
  - Added TV Android compatibility script flow:
    - new script file: `src/new_repo_template/snapshot_assets/templates/tv/tv_patch_android_wrapper.mjs`
    - scaffold planning/writing updates: `src/new_repo_template/scaffold.py`
    - generated TV manifest scripts now include:
      - `tv:android:prepare`
      - `tv:android:wrapper:patch`
      - `tv:android` orchestration with community autolinking toggle
  - Updated generated TV setup docs and template-level mobile/TV setup docs:
    - `src/new_repo_template/snapshot_assets/templates/tv/tv_readme.md`
    - `docs/MOBILE_TV_SETUP.md`

## BLUE Verification

- Focused suites:
  - `uv run pytest tests/contracts/test_mobile_tv_scaffold_contract.py tests/contracts/test_security_baseline_contract.py tests/contracts/test_tv_android_build_profile_contract.py` (10 passed)
  - `uv run pytest tests/contracts/test_mobile_tv_setup_docs_contract.py tests/contracts/test_mobile_tv_scaffold_contract.py tests/contracts/test_tv_android_build_profile_contract.py` (10 passed)
- Full suite:
  - `uv run pytest` (116 passed)
- Runtime sanity on fresh generated TV scaffold:
  - `tv:android` now executes deterministic prebuild + Gradle-wrapper patch + community autolinking flow and progresses into native Android build stage.
  - Remaining failure observed is environment-side NDK integrity (`source.properties` missing under `~/Library/Android/sdk/ndk/27.1.12297006`), not scaffold-path wiring.

## Documentation/Tracking Sync

- Updated:
  - `PROGRESS.md`
  - `docs/LIVING_DOCS.md`
  - `docs/ARCHITECTURE.md`
  - `docs/MOBILE_TV_SETUP.md`
- Added this new session summary without overwriting prior session summaries.

## Outcome

Generated TV scaffolds now include a resilient local Android run pipeline that patches known wrapper/toolchain incompatibility points before running Expo Android, and generated root `.gitignore` baselines now always ignore `node_modules` directories.
