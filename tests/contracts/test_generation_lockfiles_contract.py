from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


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


def run_nurt_command(*, cwd: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    repo_root = Path(__file__).resolve().parents[2]
    env["PYTHONPATH"] = str(repo_root / "src")
    env.setdefault("NURT_UPDATE_CHECK_SIMULATE", "none")
    return subprocess.run(
        [sys.executable, "-m", "new_repo_template.nurt_cli", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def _assert_manifest_uses_expected_version_ranges(manifest_path: Path) -> None:
    package_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    for section_name in ("dependencies", "devDependencies"):
        section = package_data.get(section_name, {})
        assert isinstance(section, dict)
        for package_name, version_spec in section.items():
            assert isinstance(version_spec, str), (
                f"Expected string version for {package_name} in {manifest_path}"
            )
            if package_name.startswith("@generated/"):
                assert version_spec == "workspace:*", (
                    f"Expected workspace protocol for internal dependency {package_name} "
                    f"in {manifest_path}, got {version_spec!r}"
                )
                continue
            assert version_spec.startswith("^"), (
                f"Expected caret range for external dependency {package_name} in "
                f"{manifest_path}, got {version_spec!r}"
            )


def test_scaffolded_js_manifests_use_caret_ranges_and_workspace_protocol(
    tmp_path: Path,
) -> None:
    """Generated JS manifests should keep caret ranges while reserving workspace protocol for internal packages."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "js-range-contract"

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
        "Expected JS range contract scaffold to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    manifest_paths = (
        output_dir / "package.json",
        output_dir / "apps" / "web" / "package.json",
        output_dir / "apps" / "backend" / "package.json",
        output_dir / "apps" / "desktop" / "package.json",
        output_dir / "apps" / "mobile" / "package.json",
        output_dir / "apps" / "tv" / "package.json",
        output_dir / "packages" / "shared" / "package.json",
    )

    for manifest_path in manifest_paths:
        assert manifest_path.exists(), f"Expected generated manifest at {manifest_path}"
        _assert_manifest_uses_expected_version_ranges(manifest_path)


def test_nurt_new_generates_root_lockfiles_for_foundation_output(
    tmp_path: Path,
) -> None:
    """Foundation generation should emit only the root Bun lockfile."""

    if shutil.which("uv") is None or shutil.which("bun") is None:
        pytest.skip("uv and bun are required for lockfile generation contract")

    output_dir = tmp_path / "demo-foundation"
    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", output_dir.name, "--no-interactive"],
    )

    assert result.returncode == 0, (
        "Expected nurt new foundation generation to succeed with lockfiles.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    assert (output_dir / "bun.lock").exists(), "nurt new should create a root bun.lock"
    assert not (output_dir / "uv.lock").exists(), (
        "foundation output must not create root uv.lock"
    )


def test_nurt_new_python_target_generates_root_workspace_uv_lockfile(
    tmp_path: Path,
) -> None:
    """Python target generation should create a root uv workspace lockfile."""

    if shutil.which("uv") is None or shutil.which("bun") is None:
        pytest.skip("uv and bun are required for lockfile generation contract")

    output_dir = tmp_path / "demo-python"
    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", output_dir.name, "--target", "python", "--no-interactive"],
    )

    assert result.returncode == 0, (
        "Expected nurt new python generation to succeed with lockfiles.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    lane_root = output_dir / "apps" / "python"
    lane_pyproject = lane_root / "pyproject.toml"
    lane_python_version = lane_root / ".python-version"
    lane_content = lane_pyproject.read_text(encoding="utf-8")
    root_pyproject = output_dir / "pyproject.toml"

    assert (output_dir / "bun.lock").exists(), "root bun.lock should exist"
    assert root_pyproject.exists(), "root pyproject.toml should exist for uv workspace"
    assert not (output_dir / ".python-version").exists(), (
        "root .python-version should not exist"
    )
    assert (output_dir / "uv.lock").exists(), "root uv.lock should exist"
    assert not (lane_root / "uv.lock").exists(), "python lane uv.lock should not exist"
    assert lane_python_version.exists(), "python lane .python-version should exist"
    assert 'requires-python = ">=3.14"' in lane_content
    assert '"pytest>=' in lane_content
    assert '"ruff>=' in lane_content
    assert '"mypy>=' in lane_content
    assert "[tool.uv.workspace]" in root_pyproject.read_text(encoding="utf-8")
