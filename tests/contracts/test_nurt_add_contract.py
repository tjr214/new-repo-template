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


def run_nurt_command(
    *, cwd: Path, args: list[str], env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    command_env = os.environ.copy()
    repo_root = Path(__file__).resolve().parents[2]
    command_env["PYTHONPATH"] = str(repo_root / "src")
    command_env.setdefault("NURT_UPDATE_CHECK_SIMULATE", "none")
    if env is not None:
        command_env.update(env)

    return subprocess.run(
        [sys.executable, "-m", "new_repo_template.nurt_cli", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=command_env,
        check=False,
    )


def scaffold_generated_repo(*, tmp_path: Path, args: list[str]) -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "generated-repo"
    result = run_scaffold_command(
        repo_root=repo_root,
        args=[*args, "--no-interactive", "--output", str(output_dir)],
    )
    assert result.returncode == 0, (
        "Expected scaffold fixture to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    return output_dir


def test_nurt_add_writes_new_js_project_without_running_new_repo_post_create(
    tmp_path: Path,
) -> None:
    """nurt add should add a project in place without repo bootstrap side effects."""

    repo_dir = scaffold_generated_repo(
        tmp_path=tmp_path, args=["--target", "foundation"]
    )

    result = run_nurt_command(
        cwd=repo_dir,
        args=["add", "--target", "desktop", "--no-interactive"],
    )

    assert result.returncode == 0, (
        "Expected nurt add to succeed for a new desktop lane.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert (repo_dir / "apps" / "desktop" / "desktop").is_dir()
    assert (repo_dir / "apps" / "desktop" / "desktop" / "package.json").exists()
    assert (repo_dir / "bun.lock").exists(), "add mode should regenerate bun.lock"
    assert not (repo_dir / ".git").exists(), "add mode must not initialize git"


def test_nurt_add_supports_repeated_same_type_projects(tmp_path: Path) -> None:
    """nurt add should support multiple named projects of the same type."""

    repo_dir = scaffold_generated_repo(
        tmp_path=tmp_path, args=["--target", "foundation"]
    )

    result = run_nurt_command(
        cwd=repo_dir,
        args=[
            "add",
            "--project",
            "desktop:admin",
            "--project",
            "desktop:kiosk",
            "--no-interactive",
        ],
    )

    assert result.returncode == 0, (
        "Expected repeated same-type add command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert (repo_dir / "apps" / "desktop" / "admin").is_dir()
    assert (repo_dir / "apps" / "desktop" / "kiosk").is_dir()


def test_nurt_add_updates_btca_files_for_new_target(tmp_path: Path) -> None:
    """Adding a new target should update BTCA config, sidecar tracking, and docs."""

    repo_dir = scaffold_generated_repo(
        tmp_path=tmp_path, args=["--target", "foundation"]
    )

    result = run_nurt_command(
        cwd=repo_dir,
        args=["add", "--target", "desktop", "--no-interactive"],
    )

    assert result.returncode == 0, (
        "Expected desktop add to update BTCA files successfully.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    btca_config = json.loads(
        (repo_dir / "btca.config.jsonc").read_text(encoding="utf-8")
    )
    btca_sidecar = json.loads(
        (repo_dir / ".nurt" / "btca-managed-resources.json").read_text(encoding="utf-8")
    )
    btca_docs = (repo_dir / "docs" / "BTCA_RESOURCES.md").read_text(encoding="utf-8")

    assert [resource["name"] for resource in btca_config["resources"]] == [
        "turborepo",
        "bun",
        "electron-forge",
        "electron",
        "typescript-docs",
    ]
    assert [record["name"] for record in btca_sidecar["managed_resources"]] == [
        "turborepo",
        "bun",
        "electron-forge",
        "electron",
        "typescript-docs",
    ]
    assert "<name>electron-forge</name>" in btca_docs
    assert "<name>electron</name>" in btca_docs
    assert "<name>typescript-docs</name>" in btca_docs


def test_nurt_add_rejects_existing_project_path_collisions(tmp_path: Path) -> None:
    """nurt add should refuse to overwrite an existing project instance."""

    repo_dir = scaffold_generated_repo(tmp_path=tmp_path, args=["--target", "desktop"])

    result = run_nurt_command(
        cwd=repo_dir,
        args=["add", "--project", "desktop:desktop", "--no-interactive"],
    )

    assert result.returncode == 1
    assert "already exists" in f"{result.stdout}\n{result.stderr}"


def test_nurt_add_preserves_user_btca_entries_and_drifted_managed_resources(
    tmp_path: Path,
) -> None:
    """Add-mode BTCA merging should be additive and warn on drifted managed entries."""

    repo_dir = scaffold_generated_repo(
        tmp_path=tmp_path, args=["--target", "foundation"]
    )

    btca_config_path = repo_dir / "btca.config.jsonc"
    btca_payload = json.loads(btca_config_path.read_text(encoding="utf-8"))
    btca_payload["resources"][1]["url"] = "https://example.com/custom-bun-docs"
    btca_payload["resources"].append(
        {
            "type": "git",
            "name": "custom-docs",
            "url": "https://example.com/custom-docs",
            "branch": "main",
        }
    )
    btca_config_path.write_text(
        json.dumps(btca_payload, indent=2) + "\n", encoding="utf-8"
    )

    result = run_nurt_command(
        cwd=repo_dir,
        args=["add", "--target", "desktop", "--no-interactive"],
    )

    assert result.returncode == 0, (
        "Expected add-mode BTCA merge to preserve user and drifted resources.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    merged_btca_payload = json.loads(btca_config_path.read_text(encoding="utf-8"))
    resource_names = [resource["name"] for resource in merged_btca_payload["resources"]]
    assert resource_names == [
        "turborepo",
        "bun",
        "custom-docs",
        "electron-forge",
        "electron",
        "typescript-docs",
    ]
    assert (
        merged_btca_payload["resources"][1]["url"]
        == "https://example.com/custom-bun-docs"
    )
    assert any(
        resource["name"] == "custom-docs"
        for resource in merged_btca_payload["resources"]
    )
    assert "preserved customized nurt-managed BTCA resource 'bun'" in (
        f"{result.stdout}\n{result.stderr}"
    )


def test_nurt_add_fails_from_nested_subdirectory(tmp_path: Path) -> None:
    """nurt add should only run from the repo root and must not search upward."""

    repo_dir = scaffold_generated_repo(
        tmp_path=tmp_path, args=["--target", "foundation"]
    )
    nested_dir = repo_dir / "apps"

    result = run_nurt_command(
        cwd=nested_dir,
        args=["add", "--target", "desktop", "--dry-run", "--no-interactive"],
    )

    assert result.returncode == 1
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert (
        "nurt add must run from the root of a nurt-generated repository"
        in combined_output
    )
    assert ".nurt/repo.json" in combined_output


def test_nurt_add_python_into_js_repo_creates_root_uv_workspace_and_lockfile(
    tmp_path: Path,
) -> None:
    """Adding the first Python lane should create the root uv workspace metadata."""

    if shutil.which("uv") is None or shutil.which("bun") is None:
        pytest.skip("uv and bun are required for add-mode lockfile coverage")

    repo_dir = scaffold_generated_repo(
        tmp_path=tmp_path, args=["--target", "foundation"]
    )

    result = run_nurt_command(
        cwd=repo_dir,
        args=["add", "--target", "python", "--no-interactive"],
    )

    assert result.returncode == 0, (
        "Expected first Python lane add to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert (repo_dir / "pyproject.toml").exists()
    assert (repo_dir / "uv.lock").exists()
    assert (repo_dir / "apps" / "python" / "python-app" / "pyproject.toml").exists()


def test_nurt_add_python_lib_patches_existing_single_python_app(tmp_path: Path) -> None:
    """Adding python-lib should retrofit a single existing Python app to depend on it."""

    repo_dir = scaffold_generated_repo(tmp_path=tmp_path, args=["--target", "python"])

    result = run_nurt_command(
        cwd=repo_dir,
        args=["add", "--target", "python-lib", "--no-interactive"],
    )

    assert result.returncode == 0, (
        "Expected python-lib retrofit add to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    root_pyproject = (repo_dir / "pyproject.toml").read_text(encoding="utf-8")
    app_pyproject = (
        repo_dir / "apps" / "python" / "python-app" / "pyproject.toml"
    ).read_text(encoding="utf-8")

    assert '"packages/python/*",' in root_pyproject
    assert '"python-lib>=0.1.0",' in app_pyproject
    assert "[tool.uv.sources]" in app_pyproject
    assert "python-lib = { workspace = true }" in app_pyproject


def test_nurt_add_backend_requires_explicit_auth(tmp_path: Path) -> None:
    """Adding backend should enforce an auth choice, including none."""

    repo_dir = scaffold_generated_repo(
        tmp_path=tmp_path, args=["--target", "foundation"]
    )

    result = run_nurt_command(
        cwd=repo_dir,
        args=["add", "--target", "backend", "--no-interactive"],
    )

    assert result.returncode == 1
    assert "auth option is required" in f"{result.stdout}\n{result.stderr}"


def test_nurt_add_web_requires_binding_when_multiple_backends_exist(
    tmp_path: Path,
) -> None:
    """Adding web should require explicit backend binding when multiple backends exist."""

    repo_dir = scaffold_generated_repo(
        tmp_path=tmp_path,
        args=[
            "--project",
            "backend:api",
            "--project",
            "backend:worker",
            "--backend-auth",
            "api:clerk",
            "--backend-auth",
            "worker:none",
        ],
    )

    result = run_nurt_command(
        cwd=repo_dir,
        args=["add", "--target", "web", "--no-interactive"],
    )

    assert result.returncode == 1
    assert "web-backend binding is required" in f"{result.stdout}\n{result.stderr}"


def test_nurt_add_backend_creates_shared_workspace_package_when_missing(
    tmp_path: Path,
) -> None:
    """Adding backend should create packages/shared when required by the supported combo."""

    repo_dir = scaffold_generated_repo(
        tmp_path=tmp_path, args=["--target", "foundation"]
    )

    result = run_nurt_command(
        cwd=repo_dir,
        args=["add", "--target", "backend", "--auth", "none", "--no-interactive"],
    )

    assert result.returncode == 0, (
        "Expected backend add to succeed with shared package bootstrap.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert (repo_dir / "packages" / "shared" / "package.json").exists()


def test_nurt_add_web_retrofits_existing_desktop_for_shared_wiring(
    tmp_path: Path,
) -> None:
    """Adding the first web app should patch existing desktop lanes for shared wiring."""

    repo_dir = scaffold_generated_repo(tmp_path=tmp_path, args=["--target", "desktop"])

    result = run_nurt_command(
        cwd=repo_dir,
        args=["add", "--target", "web", "--no-interactive"],
    )

    assert result.returncode == 0, (
        "Expected web add to retrofit an existing desktop lane.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    desktop_manifest = json.loads(
        (repo_dir / "apps" / "desktop" / "desktop" / "package.json").read_text(
            encoding="utf-8"
        )
    )
    renderer_text = (
        repo_dir / "apps" / "desktop" / "desktop" / "src" / "renderer.ts"
    ).read_text(encoding="utf-8")

    assert desktop_manifest["dependencies"]["@generated/shared"] == "workspace:*"
    assert "@generated/shared" in renderer_text
    assert "NURT_WELCOME_MESSAGE" in renderer_text
