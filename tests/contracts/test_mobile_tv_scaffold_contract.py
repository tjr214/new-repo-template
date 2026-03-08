from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_scaffold_command(
    *, repo_root: Path, args: list[str]
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")
    return subprocess.run(
        [sys.executable, "-m", "new_repo_template.scaffold", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_mobile_only_scaffolds_expo_baseline_files_and_scripts(tmp_path: Path) -> None:
    """Mobile target should scaffold a concrete Expo app baseline."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "mobile-only"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "mobile",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected mobile-only scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    mobile_root = output_dir / "apps" / "mobile"
    expected_paths = (
        mobile_root / "package.json",
        mobile_root / "app.json",
        mobile_root / "eas.json",
        mobile_root / "babel.config.js",
        mobile_root / "index.js",
        mobile_root / "App.tsx",
        mobile_root / "smoke.test.js",
        mobile_root / "tsconfig.json",
    )
    for path in expected_paths:
        assert path.exists(), f"Expected scaffolded mobile file: {path}"

    mobile_manifest = json.loads(
        (mobile_root / "package.json").read_text(encoding="utf-8")
    )
    scripts = mobile_manifest.get("scripts")
    assert isinstance(scripts, dict)
    for script_name in (
        "dev",
        "build",
        "test",
        "lint",
        "typecheck",
        "mobile:start",
        "mobile:android",
        "mobile:ios",
        "mobile:web",
        "mobile:export",
        "mobile:build:ios:development",
        "mobile:build:ios:preview",
        "mobile:lint:smoke",
        "mobile:typecheck:smoke",
        "mobile:test:smoke",
        "mobile:start:smoke",
        "mobile:export:smoke",
    ):
        script_value = scripts.get(script_name)
        assert isinstance(script_value, str) and script_value != ""

    assert scripts.get("lint") == "bun run mobile:lint:smoke"
    assert scripts.get("typecheck") == "bun run mobile:typecheck:smoke"
    assert scripts.get("test") == "bun run mobile:test:smoke"
    assert (
        scripts.get("mobile:build:ios:preview")
        == "bunx eas-cli build --platform ios --profile preview --non-interactive"
    )

    dependencies = mobile_manifest.get("dependencies")
    assert isinstance(dependencies, dict)
    assert "expo" in dependencies
    assert "react" in dependencies
    assert "react-native" in dependencies
    assert "expo-status-bar" in dependencies
    assert dependencies.get("react") == "^19.2.0"
    assert dependencies.get("react-native") == "^0.83.2"

    dev_dependencies = mobile_manifest.get("devDependencies")
    assert isinstance(dev_dependencies, dict)
    assert dev_dependencies.get("babel-preset-expo") == "^55.0.10"
    assert dev_dependencies.get("@types/react") == "^19.2.14"

    app_json_text = (mobile_root / "app.json").read_text(encoding="utf-8")
    assert '"slug": "mobile"' in app_json_text
    assert "@react-native-tvos/config-tv" not in app_json_text

    eas_json_text = (mobile_root / "eas.json").read_text(encoding="utf-8")
    assert '"preview"' in eas_json_text
    assert '"development"' in eas_json_text
    assert '"distribution": "internal"' in eas_json_text


def test_tv_only_scaffolds_expo_tv_baseline_with_isolated_plugin(
    tmp_path: Path,
) -> None:
    """TV target should scaffold TV-specific Expo config without leaking to mobile."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "tv-only"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "tv",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected tv-only scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    tv_root = output_dir / "apps" / "tv"
    expected_paths = (
        tv_root / "package.json",
        tv_root / "app.json",
        tv_root / "babel.config.js",
        tv_root / "index.js",
        tv_root / "App.tsx",
        tv_root / "smoke.test.js",
        tv_root / "tsconfig.json",
        tv_root / "TV_VALIDATION_LOG.md",
    )
    for path in expected_paths:
        assert path.exists(), f"Expected scaffolded tv file: {path}"

    tv_manifest = json.loads((tv_root / "package.json").read_text(encoding="utf-8"))
    scripts = tv_manifest.get("scripts")
    assert isinstance(scripts, dict)
    for script_name in (
        "dev",
        "build",
        "test",
        "lint",
        "typecheck",
        "tv:start",
        "tv:android",
        "tv:export",
        "tv:lint:smoke",
        "tv:typecheck:smoke",
        "tv:test:smoke",
        "tv:start:smoke",
        "tv:export:smoke",
    ):
        script_value = scripts.get(script_name)
        assert isinstance(script_value, str) and script_value != ""

    assert scripts.get("lint") == "bun run tv:lint:smoke"
    assert scripts.get("typecheck") == "bun run tv:typecheck:smoke"
    assert scripts.get("test") == "bun run tv:test:smoke"

    dependencies = tv_manifest.get("dependencies")
    assert isinstance(dependencies, dict)
    assert "expo" in dependencies
    assert "react" in dependencies
    assert "react-native" in dependencies
    assert "react-native-tvos" in dependencies
    assert dependencies.get("react") == "^19.2.0"
    assert dependencies.get("react-native") == "^0.83.2"
    assert dependencies.get("react-native-tvos") == "^0.81.4-0"

    dev_dependencies = tv_manifest.get("devDependencies")
    assert isinstance(dev_dependencies, dict)
    assert "@react-native-tvos/config-tv" in dev_dependencies
    assert dev_dependencies.get("@react-native-community/cli") == "^20.1.2"
    assert dev_dependencies.get("@react-native-community/cli-platform-android") == (
        "^20.1.2"
    )
    assert dev_dependencies.get("babel-preset-expo") == "^55.0.10"
    assert dev_dependencies.get("@types/react") == "^19.2.14"

    app_json_text = (tv_root / "app.json").read_text(encoding="utf-8")
    assert '"slug": "tv"' in app_json_text
    assert '"@react-native-tvos/config-tv"' in app_json_text


def test_mobile_tv_dry_run_reports_separate_mobile_and_tv_paths(tmp_path: Path) -> None:
    """Dry-run for mobile+tv should list distinct app scaffolds and TV wiring."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "mobile-tv-dry-run"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "mobile",
            "--target",
            "tv",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected mobile+tv dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "apps/mobile/app.json" in combined_output
    assert "apps/mobile/App.tsx" in combined_output
    assert "apps/mobile/smoke.test.js" in combined_output
    assert "apps/tv/app.json" in combined_output
    assert "apps/tv/App.tsx" in combined_output
    assert "apps/tv/smoke.test.js" in combined_output
    assert "apps/tv/package.json" in combined_output
    assert "apps/tv/TV_VALIDATION_LOG.md" in combined_output
    assert not output_dir.exists(), "--dry-run should not write scaffold output"
