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


def test_shared_react_boundaries_keep_routes_local_and_non_web_ui_unwired(
    tmp_path: Path,
) -> None:
    """Shared React packages should stay platform-agnostic while apps own runtime wiring."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "shared-react-boundaries"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "desktop",
            "--target",
            "mobile",
            "--target",
            "tv",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web+desktop+mobile+tv scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    shared_index = output_dir / "packages" / "shared" / "src" / "index.ts"
    design_tokens_index = output_dir / "packages" / "design-tokens" / "src" / "index.ts"
    web_route_tree = output_dir / "apps" / "web" / "web" / "src" / "routeTree.gen.ts"
    web_index_route = (
        output_dir / "apps" / "web" / "web" / "src" / "routes" / "index.tsx"
    )
    mobile_app = output_dir / "apps" / "mobile" / "mobile" / "App.tsx"
    tv_app = output_dir / "apps" / "tv" / "tv" / "App.tsx"

    for path in (
        shared_index,
        design_tokens_index,
        web_route_tree,
        web_index_route,
        mobile_app,
        tv_app,
    ):
        assert path.exists(), f"Expected shared React boundary file: {path}"

    forbidden_shared_markers = (
        'from "react-dom',
        "from 'react-dom",
        'from "electron"',
        "from 'electron'",
        'from "react-native"',
        "from 'react-native'",
        'from "@react-native',
        "from '@react-native",
        "window.",
        "document.",
        "localStorage",
        "navigator.",
    )
    for file_path in (shared_index, design_tokens_index):
        text = file_path.read_text(encoding="utf-8")
        for marker in forbidden_shared_markers:
            assert marker not in text, (
                f"Expected {file_path} to stay renderer-agnostic; found forbidden marker {marker!r}"
            )

    assert not (output_dir / "packages" / "shared" / "src" / "routes").exists()
    assert not (
        output_dir / "packages" / "design-tokens" / "src" / "routeTree.gen.ts"
    ).exists()

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
    mobile_manifest = json.loads(
        (output_dir / "apps" / "mobile" / "mobile" / "package.json").read_text(
            encoding="utf-8"
        )
    )
    tv_manifest = json.loads(
        (output_dir / "apps" / "tv" / "tv" / "package.json").read_text(encoding="utf-8")
    )

    web_dependencies = web_manifest.get("dependencies", {})
    desktop_dependencies = desktop_manifest.get("dependencies", {})
    mobile_dependencies = mobile_manifest.get("dependencies", {})
    tv_dependencies = tv_manifest.get("dependencies", {})

    assert web_dependencies.get("@generated/shared") == "workspace:*"
    assert web_dependencies.get("@generated/design-tokens") == "workspace:*"
    assert web_dependencies.get("@generated/ui") == "workspace:*"

    assert desktop_dependencies.get("@generated/shared") == "workspace:*"
    assert desktop_dependencies.get("@generated/design-tokens") == "workspace:*"
    assert "@generated/ui" not in desktop_dependencies

    assert mobile_dependencies.get("@generated/shared") == "workspace:*"
    assert "@generated/ui" not in mobile_dependencies

    assert tv_dependencies.get("@generated/shared") == "workspace:*"
    assert "@generated/ui" not in tv_dependencies

    mobile_app_text = mobile_app.read_text(encoding="utf-8")
    tv_app_text = tv_app.read_text(encoding="utf-8")
    assert "@generated/shared" in mobile_app_text
    assert "NURT_FRONTEND_COPY" in mobile_app_text
    assert "@generated/shared" in tv_app_text
    assert "NURT_FRONTEND_COPY" in tv_app_text


def test_mobile_tv_only_scaffold_bootstraps_shared_non_visual_foundation(
    tmp_path: Path,
) -> None:
    """Mobile+tv should get the shared non-visual package even without web or desktop."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "mobile-tv-shared-foundation"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "mobile",
            "--target",
            "tv",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected mobile+tv scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    assert (output_dir / "packages" / "shared" / "package.json").exists()
    assert not (output_dir / "packages" / "ui" / "package.json").exists()
    assert not (output_dir / "packages" / "design-tokens" / "package.json").exists()

    mobile_manifest = json.loads(
        (output_dir / "apps" / "mobile" / "mobile" / "package.json").read_text(
            encoding="utf-8"
        )
    )
    tv_manifest = json.loads(
        (output_dir / "apps" / "tv" / "tv" / "package.json").read_text(encoding="utf-8")
    )

    assert mobile_manifest["dependencies"]["@generated/shared"] == "workspace:*"
    assert tv_manifest["dependencies"]["@generated/shared"] == "workspace:*"
