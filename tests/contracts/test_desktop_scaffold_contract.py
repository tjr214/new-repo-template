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

    desktop_root = output_dir / "apps" / "desktop" / "desktop"
    expected_paths = (
        desktop_root / "package.json",
        desktop_root / "README.md",
        desktop_root / "forge.config.ts",
        desktop_root / "tsconfig.json",
        desktop_root / "vite.main.config.ts",
        desktop_root / "vite.preload.config.ts",
        desktop_root / "vite.renderer.config.ts",
        desktop_root / "index.html",
        desktop_root / "src" / "app.ts",
        desktop_root / "src" / "main.ts",
        desktop_root / "src" / "preload.ts",
        desktop_root / "src" / "router.ts",
        desktop_root / "src" / "renderer.ts",
        output_dir / "packages" / "shared" / "package.json",
        output_dir / "packages" / "design-tokens" / "package.json",
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
    assert "@electron-forge/plugin-vite" in dev_dependencies
    assert desktop_manifest.get("main") == ".vite/build/main.js"

    dependencies = desktop_manifest.get("dependencies")
    assert isinstance(dependencies, dict)
    assert dependencies.get("@generated/shared") == "workspace:*"
    assert dependencies.get("@generated/design-tokens") == "workspace:*"
    assert "@tanstack/history" in dependencies
    assert "@tanstack/router-core" in dependencies
    assert "@tanstack/react-store" in dependencies
    assert "@tanstack/react-router" in dependencies
    assert "@tanstack/store" in dependencies
    assert "use-sync-external-store" in dependencies

    main_text = (desktop_root / "src" / "main.ts").read_text(encoding="utf-8")
    assert "BrowserWindow" in main_text
    assert "MAIN_WINDOW_VITE_DEV_SERVER_URL" in main_text
    assert "loadFile" in main_text
    assert "loadURL" in main_text

    renderer_text = (desktop_root / "src" / "renderer.ts").read_text(encoding="utf-8")
    assert "RouterProvider" in renderer_text
    assert "getRouter" in renderer_text

    router_text = (desktop_root / "src" / "router.ts").read_text(encoding="utf-8")
    assert "createHashHistory" in router_text
    assert "createRouter" in router_text

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
    assert "apps/desktop/desktop/package.json" in combined_output
    assert "apps/desktop/desktop/README.md" in combined_output
    assert "apps/desktop/desktop/forge.config.ts" in combined_output
    assert "apps/desktop/desktop/tsconfig.json" in combined_output
    assert "apps/desktop/desktop/vite.main.config.ts" in combined_output
    assert "apps/desktop/desktop/vite.preload.config.ts" in combined_output
    assert "apps/desktop/desktop/vite.renderer.config.ts" in combined_output
    assert "apps/desktop/desktop/index.html" in combined_output
    assert "apps/desktop/desktop/src/app.ts" in combined_output
    assert "apps/desktop/desktop/src/main.ts" in combined_output
    assert "apps/desktop/desktop/src/preload.ts" in combined_output
    assert "apps/desktop/desktop/src/router.ts" in combined_output
    assert "apps/desktop/desktop/src/renderer.ts" in combined_output
    assert "packages/shared/package.json" in combined_output
    assert "packages/design-tokens/package.json" in combined_output


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
    design_tokens_manifest = output_dir / "packages" / "design-tokens" / "package.json"
    ui_manifest = output_dir / "packages" / "ui" / "package.json"
    assert design_tokens_manifest.exists(), "Expected design tokens package"
    assert ui_manifest.exists(), "Expected owned web UI package"

    web_manifest = json.loads(
        (output_dir / "apps" / "web" / "web" / "package.json").read_text(
            encoding="utf-8"
        )
    )
    desktop_manifest = json.loads(
        (output_dir / "apps" / "desktop" / "desktop" / "package.json").read_text(
            encoding="utf-8"
        )
    )

    web_dependencies = web_manifest.get("dependencies")
    assert isinstance(web_dependencies, dict)
    assert web_dependencies.get("@generated/shared") == "workspace:*"

    desktop_dependencies = desktop_manifest.get("dependencies")
    assert isinstance(desktop_dependencies, dict)
    assert desktop_dependencies.get("@generated/shared") == "workspace:*"
    assert desktop_dependencies.get("@generated/design-tokens") == "workspace:*"

    desktop_renderer_text = (
        output_dir / "apps" / "desktop" / "desktop" / "src" / "renderer.ts"
    ).read_text(encoding="utf-8")
    assert "RouterProvider" in desktop_renderer_text

    desktop_router_text = (
        output_dir / "apps" / "desktop" / "desktop" / "src" / "router.ts"
    ).read_text(encoding="utf-8")
    assert "createHashHistory" in desktop_router_text
