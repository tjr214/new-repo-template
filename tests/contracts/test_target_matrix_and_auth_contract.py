from __future__ import annotations

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


def test_web_backend_requires_explicit_auth_in_non_interactive_mode(
    tmp_path: Path,
) -> None:
    """RED: web+backend without auth should fail deterministically."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-backend-no-auth"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 2
    assert (
        "auth option is required when both web and backend targets are selected"
        in result.stderr
    )


def test_web_backend_desktop_requires_explicit_auth_in_non_interactive_mode(
    tmp_path: Path,
) -> None:
    """RED: any mixed preset containing web+backend must require auth."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-backend-desktop-no-auth"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--target",
            "desktop",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 2
    assert (
        "auth option is required when both web and backend targets are selected"
        in result.stderr
    )


def test_web_backend_with_auth_succeeds_and_is_dry_run_only(tmp_path: Path) -> None:
    """RED: web+backend with auth should resolve and avoid writes in dry-run."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-backend-with-auth"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "clerk",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web+backend dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "apps/web/" in combined_output
    assert "apps/backend/" in combined_output
    assert not output_dir.exists(), "--dry-run should not write scaffold output"


def test_foundation_target_cannot_be_combined_with_other_targets(
    tmp_path: Path,
) -> None:
    """RED: foundation must be standalone and fail when mixed."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "foundation-plus-python"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--target",
            "python",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 2
    assert "foundation target cannot be combined with other targets" in result.stderr


def test_mobile_and_tv_targets_create_distinct_apps(tmp_path: Path) -> None:
    """RED: selecting mobile+tv should scaffold both separate app directories."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "mobile-tv-output"

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
    assert (output_dir / "pyproject.toml").exists()
    assert (output_dir / "apps" / "mobile").exists()
    assert (output_dir / "apps" / "tv").exists()


def test_tv_only_scaffold_keeps_root_pyproject_invariant(tmp_path: Path) -> None:
    """TV-only scaffold still requires root pyproject.toml."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "tv-only-output"

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
    assert (output_dir / "pyproject.toml").exists()
    assert (output_dir / "apps" / "tv").exists()


def test_web_only_scaffold_keeps_root_pyproject_invariant(tmp_path: Path) -> None:
    """JS-only web scaffold still requires root pyproject.toml."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-only-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web-only scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert (output_dir / "pyproject.toml").exists()
    assert (output_dir / "apps" / "web").exists()


def test_duplicate_target_selection_fails_deterministically(tmp_path: Path) -> None:
    """RED: duplicate target flags should fail with deterministic guidance."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "duplicate-target-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "web",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 2
    assert "duplicate target selections are not allowed: web" in result.stderr


def test_auth_with_web_desktop_without_backend_fails_deterministically(
    tmp_path: Path,
) -> None:
    """RED: auth must fail when web is selected without backend in mixed presets."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-desktop-auth-invalid"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "desktop",
            "--auth",
            "clerk",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 2
    assert (
        "auth option is only valid when both web and backend targets are selected"
        in result.stderr
    )


def test_auth_with_backend_desktop_without_web_fails_deterministically(
    tmp_path: Path,
) -> None:
    """RED: auth must fail when backend is selected without web in mixed presets."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "backend-desktop-auth-invalid"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "backend",
            "--target",
            "desktop",
            "--auth",
            "better-auth",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 2
    assert (
        "auth option is only valid when both web and backend targets are selected"
        in result.stderr
    )


def test_web_backend_clerk_env_examples_include_required_placeholders(
    tmp_path: Path,
) -> None:
    """RED: clerk auth variant should scaffold expected env placeholders."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-backend-clerk"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "clerk",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web+backend+clerk scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    web_env = (output_dir / "apps" / "web" / ".env.example").read_text(encoding="utf-8")
    backend_env = (output_dir / "apps" / "backend" / ".env.example").read_text(
        encoding="utf-8"
    )

    assert "VITE_CONVEX_URL=" in web_env
    assert "VITE_CLERK_PUBLISHABLE_KEY=" in web_env
    assert "CONVEX_DEPLOYMENT=" in backend_env
    assert "CLERK_FRONTEND_API_URL=" in backend_env


def test_web_backend_better_auth_env_examples_include_required_placeholders(
    tmp_path: Path,
) -> None:
    """RED: better-auth variant should scaffold expected env placeholders."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-backend-better-auth"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "better-auth",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web+backend+better-auth scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    web_env = (output_dir / "apps" / "web" / ".env.example").read_text(encoding="utf-8")
    backend_env = (output_dir / "apps" / "backend" / ".env.example").read_text(
        encoding="utf-8"
    )

    assert "VITE_CONVEX_URL=" in web_env
    assert "VITE_CONVEX_SITE_URL=" in web_env
    assert "VITE_SITE_URL=" in web_env
    assert "CONVEX_DEPLOYMENT=" in backend_env
    assert "SITE_URL=" in backend_env


def test_web_backend_clerk_scaffolds_auth_wiring_placeholders(tmp_path: Path) -> None:
    """RED: Clerk variant should scaffold frontend/backend auth wiring placeholders."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-backend-clerk-wiring"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "clerk",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web+backend+clerk scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    backend_wiring = output_dir / "apps" / "backend" / "convex" / "auth.config.ts"
    frontend_wiring = output_dir / "apps" / "web" / "src" / "auth-provider.ts"

    assert backend_wiring.exists()
    assert frontend_wiring.exists()

    backend_text = backend_wiring.read_text(encoding="utf-8")
    frontend_text = frontend_wiring.read_text(encoding="utf-8")

    assert 'provider: "clerk"' in backend_text
    assert "clerk" in frontend_text.lower()


def test_web_backend_better_auth_scaffolds_auth_wiring_placeholders(
    tmp_path: Path,
) -> None:
    """RED: Better Auth variant should scaffold frontend/backend auth wiring placeholders."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-backend-better-auth-wiring"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "better-auth",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web+backend+better-auth scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    backend_wiring = output_dir / "apps" / "backend" / "convex" / "auth.config.ts"
    frontend_wiring = output_dir / "apps" / "web" / "src" / "auth-client.ts"

    assert backend_wiring.exists()
    assert frontend_wiring.exists()

    backend_text = backend_wiring.read_text(encoding="utf-8")
    frontend_text = frontend_wiring.read_text(encoding="utf-8")

    assert 'provider: "better-auth"' in backend_text
    assert "better auth" in frontend_text.lower()
