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


def test_tv_only_scaffold_includes_android_build_profiles(tmp_path: Path) -> None:
    """TV target should scaffold a baseline EAS profile config for AndroidTV."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "tv-build-profiles"

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
    eas_json_path = tv_root / "eas.json"
    assert eas_json_path.exists(), (
        f"Expected scaffolded TV EAS config at {eas_json_path}"
    )

    eas_config = json.loads(eas_json_path.read_text(encoding="utf-8"))
    build = eas_config.get("build")
    assert isinstance(build, dict)

    development = build.get("development")
    assert isinstance(development, dict)
    assert development.get("developmentClient") is True
    assert development.get("distribution") == "internal"
    development_android = development.get("android")
    assert isinstance(development_android, dict)
    assert development_android.get("buildType") == "apk"

    preview = build.get("preview")
    assert isinstance(preview, dict)
    assert preview.get("distribution") == "internal"
    preview_android = preview.get("android")
    assert isinstance(preview_android, dict)
    assert preview_android.get("buildType") == "apk"


def test_tv_package_scripts_include_android_profile_build_commands(
    tmp_path: Path,
) -> None:
    """TV target should expose deterministic scripts for Android profile builds."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "tv-build-scripts"

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

    tv_manifest = json.loads(
        (output_dir / "apps" / "tv" / "package.json").read_text(encoding="utf-8")
    )
    scripts = tv_manifest.get("scripts")
    assert isinstance(scripts, dict)

    dev_build = scripts.get("tv:build:development")
    assert isinstance(dev_build, str) and dev_build != ""
    assert "--platform android" in dev_build
    assert "--profile development" in dev_build

    preview_build = scripts.get("tv:build:preview")
    assert isinstance(preview_build, str) and preview_build != ""
    assert "--platform android" in preview_build
    assert "--profile preview" in preview_build


def test_tv_dry_run_reports_android_build_profile_config_path(tmp_path: Path) -> None:
    """Dry-run should include TV EAS profile config in planned output."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "tv-build-dry-run"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "tv",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected tv-only dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "apps/tv/eas.json" in combined_output
    assert not output_dir.exists(), "--dry-run should not write scaffold output"


def test_tv_scaffold_includes_android_wrapper_patch_flow_for_local_builds(
    tmp_path: Path,
) -> None:
    """TV scripts should include local patch flow for Expo Android wrapper compatibility."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "tv-android-wrapper-patch"

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

    tv_manifest = json.loads(
        (output_dir / "apps" / "tv" / "package.json").read_text(encoding="utf-8")
    )
    scripts = tv_manifest.get("scripts")
    assert isinstance(scripts, dict)

    assert (
        scripts.get("tv:android:prepare") == "expo prebuild --clean --platform android"
    )
    assert scripts.get("tv:android:wrapper:patch") == (
        "node ./scripts/patch-android-wrapper.mjs"
    )
    assert scripts.get("tv:android") == (
        "bun run tv:android:prepare && bun run tv:android:wrapper:patch && "
        "cross-env EXPO_USE_COMMUNITY_AUTOLINKING=1 expo run:android --no-install"
    )

    patch_script_path = (
        output_dir / "apps" / "tv" / "scripts" / "patch-android-wrapper.mjs"
    )
    assert patch_script_path.exists(), (
        f"Expected scaffolded Android wrapper patch helper at {patch_script_path}"
    )
