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


def test_desktop_only_scaffolds_electron_forge_baseline(tmp_path: Path) -> None:
    """Desktop target should scaffold concrete Electron Forge baseline files."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "desktop-only"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "desktop",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected desktop-only scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    desktop_root = output_dir / "apps" / "desktop"
    expected_paths = (
        desktop_root / "package.json",
        desktop_root / "README.md",
        desktop_root / "forge.config.ts",
        desktop_root / "tsconfig.json",
        desktop_root / "index.html",
        desktop_root / "src" / "main.ts",
        desktop_root / "src" / "preload.ts",
        desktop_root / "src" / "renderer.ts",
    )
    for path in expected_paths:
        assert path.exists(), f"Expected scaffolded desktop file: {path}"

    desktop_manifest = json.loads(
        (desktop_root / "package.json").read_text(encoding="utf-8")
    )
    scripts = desktop_manifest.get("scripts")
    assert isinstance(scripts, dict)
    for script_name in (
        "dev",
        "build",
        "test",
        "lint",
        "typecheck",
        "desktop:start",
        "desktop:package",
        "desktop:make",
        "desktop:start:smoke",
        "desktop:package:smoke",
        "desktop:make:smoke",
    ):
        script_value = scripts.get(script_name)
        assert isinstance(script_value, str) and script_value != ""

    dev_dependencies = desktop_manifest.get("devDependencies")
    assert isinstance(dev_dependencies, dict)
    assert "electron" in dev_dependencies
    assert "@electron-forge/cli" in dev_dependencies

    main_text = (desktop_root / "src" / "main.ts").read_text(encoding="utf-8")
    assert "BrowserWindow" in main_text
    assert "loadFile" in main_text

    readme_text = (desktop_root / "README.md").read_text(encoding="utf-8").lower()
    assert "unsigned" in readme_text
    assert "internal" in readme_text


def test_desktop_only_dry_run_lists_electron_forge_paths(tmp_path: Path) -> None:
    """Desktop dry-run should list concrete Electron Forge wiring files."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "desktop-only-dry-run"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "desktop",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected desktop-only dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "apps/desktop/package.json" in combined_output
    assert "apps/desktop/README.md" in combined_output
    assert "apps/desktop/forge.config.ts" in combined_output
    assert "apps/desktop/tsconfig.json" in combined_output
    assert "apps/desktop/index.html" in combined_output
    assert "apps/desktop/src/main.ts" in combined_output
    assert "apps/desktop/src/preload.ts" in combined_output
    assert "apps/desktop/src/renderer.ts" in combined_output


def test_web_desktop_scaffold_reuses_shared_workspace_package(tmp_path: Path) -> None:
    """Web+desktop should share utility package wiring between both apps."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-desktop-shared"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "desktop",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web+desktop scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    shared_manifest = output_dir / "packages" / "shared" / "package.json"
    assert shared_manifest.exists(), "Expected shared workspace package for web+desktop"

    web_manifest = json.loads(
        (output_dir / "apps" / "web" / "package.json").read_text(encoding="utf-8")
    )
    desktop_manifest = json.loads(
        (output_dir / "apps" / "desktop" / "package.json").read_text(encoding="utf-8")
    )

    web_dependencies = web_manifest.get("dependencies")
    assert isinstance(web_dependencies, dict)
    assert web_dependencies.get("@generated/shared") == "workspace:*"

    desktop_dependencies = desktop_manifest.get("dependencies")
    assert isinstance(desktop_dependencies, dict)
    assert desktop_dependencies.get("@generated/shared") == "workspace:*"

    desktop_renderer_text = (
        output_dir / "apps" / "desktop" / "src" / "renderer.ts"
    ).read_text(encoding="utf-8")
    assert 'from "@generated/shared"' in desktop_renderer_text
    assert "NURT_WELCOME_MESSAGE" in desktop_renderer_text
