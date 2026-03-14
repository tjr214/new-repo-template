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


def test_foundation_scaffold_includes_shared_infra_config_packages(
    tmp_path: Path,
) -> None:
    """Foundation scaffold should include reusable TypeScript and lint config packages."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "foundation-infra"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected foundation scaffold with infra packages to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    expected_paths = (
        output_dir / "eslint.config.mjs",
        output_dir / "packages" / "typescript-config" / "package.json",
        output_dir / "packages" / "typescript-config" / "base.json",
        output_dir / "packages" / "typescript-config" / "react-app.json",
        output_dir / "packages" / "typescript-config" / "node.json",
        output_dir / "packages" / "typescript-config" / "expo.json",
        output_dir / "packages" / "eslint-config" / "package.json",
        output_dir / "packages" / "eslint-config" / "base.mjs",
    )

    for path in expected_paths:
        assert path.exists(), f"Expected shared infra scaffold file: {path}"

    root_manifest = json.loads(
        (output_dir / "package.json").read_text(encoding="utf-8")
    )
    root_dev_dependencies = root_manifest.get("devDependencies")
    assert isinstance(root_dev_dependencies, dict)
    assert root_dev_dependencies.get("@generated/eslint-config") == "workspace:*"

    root_eslint_text = (output_dir / "eslint.config.mjs").read_text(encoding="utf-8")
    assert "@generated/eslint-config/base.mjs" in root_eslint_text


def test_shared_infra_packages_are_wired_into_generated_app_configs(
    tmp_path: Path,
) -> None:
    """Generated app manifests and tsconfigs should consume shared workspace config packages."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "all-config-wiring"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--target",
            "desktop",
            "--target",
            "mobile",
            "--target",
            "tv",
            "--auth",
            "clerk",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected scaffold with app config wiring to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    expected_extends = {
        output_dir
        / "apps"
        / "web"
        / "web"
        / "tsconfig.json": "@generated/typescript-config/react-app.json",
        output_dir
        / "apps"
        / "backend"
        / "backend"
        / "tsconfig.json": "@generated/typescript-config/node.json",
        output_dir
        / "apps"
        / "desktop"
        / "desktop"
        / "tsconfig.json": "@generated/typescript-config/node.json",
        output_dir
        / "apps"
        / "mobile"
        / "mobile"
        / "tsconfig.json": "@generated/typescript-config/expo.json",
        output_dir
        / "apps"
        / "tv"
        / "tv"
        / "tsconfig.json": "@generated/typescript-config/expo.json",
    }

    for tsconfig_path, expected_extends in expected_extends.items():
        config_text = tsconfig_path.read_text(encoding="utf-8")
        assert expected_extends in config_text, (
            f"Expected {tsconfig_path} to extend shared config {expected_extends}"
        )

    manifest_paths = (
        output_dir / "apps" / "web" / "web" / "package.json",
        output_dir / "apps" / "backend" / "backend" / "package.json",
        output_dir / "apps" / "desktop" / "desktop" / "package.json",
        output_dir / "apps" / "mobile" / "mobile" / "package.json",
        output_dir / "apps" / "tv" / "tv" / "package.json",
    )
    for manifest_path in manifest_paths:
        package_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        dev_dependencies = package_data.get("devDependencies")
        assert isinstance(dev_dependencies, dict)
        assert dev_dependencies.get("@generated/typescript-config") == "workspace:*"


def test_shared_infra_packages_appear_in_dry_run_plan(tmp_path: Path) -> None:
    """Dry-run plan should expose shared infra package paths for review."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "infra-dry-run"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected shared infra dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "eslint.config.mjs" in combined_output
    assert "packages/typescript-config/package.json" in combined_output
    assert "packages/eslint-config/package.json" in combined_output
