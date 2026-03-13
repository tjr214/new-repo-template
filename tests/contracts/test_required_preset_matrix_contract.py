from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass(frozen=True)
class PresetMatrixCase:
    name: str
    targets: tuple[str, ...]
    auth: str | None


MATRIX_CASES: tuple[PresetMatrixCase, ...] = (
    PresetMatrixCase(
        name="foundation-only",
        targets=("foundation",),
        auth=None,
    ),
    PresetMatrixCase(
        name="python-only",
        targets=("python",),
        auth=None,
    ),
    PresetMatrixCase(
        name="typescript-cli-only",
        targets=("typescript-cli",),
        auth=None,
    ),
    PresetMatrixCase(
        name="web-backend-clerk",
        targets=("web", "backend"),
        auth="clerk",
    ),
    PresetMatrixCase(
        name="web-backend-better-auth",
        targets=("web", "backend"),
        auth="better-auth",
    ),
    PresetMatrixCase(
        name="desktop-only",
        targets=("desktop",),
        auth=None,
    ),
    PresetMatrixCase(
        name="mobile-only",
        targets=("mobile",),
        auth=None,
    ),
    PresetMatrixCase(
        name="tv-only",
        targets=("tv",),
        auth=None,
    ),
    PresetMatrixCase(
        name="mobile-tv-dual",
        targets=("mobile", "tv"),
        auth=None,
    ),
    PresetMatrixCase(
        name="web-backend-clerk-desktop",
        targets=("web", "backend", "desktop"),
        auth="clerk",
    ),
    PresetMatrixCase(
        name="web-backend-better-auth-desktop",
        targets=("web", "backend", "desktop"),
        auth="better-auth",
    ),
    PresetMatrixCase(
        name="web-backend-clerk-mobile-desktop",
        targets=("web", "backend", "mobile", "desktop"),
        auth="clerk",
    ),
    PresetMatrixCase(
        name="web-backend-better-auth-mobile-desktop",
        targets=("web", "backend", "mobile", "desktop"),
        auth="better-auth",
    ),
    PresetMatrixCase(
        name="web-backend-clerk-tv-desktop",
        targets=("web", "backend", "tv", "desktop"),
        auth="clerk",
    ),
    PresetMatrixCase(
        name="web-backend-better-auth-tv-desktop",
        targets=("web", "backend", "tv", "desktop"),
        auth="better-auth",
    ),
    PresetMatrixCase(
        name="web-backend-clerk-mobile-tv-desktop",
        targets=("web", "backend", "mobile", "tv", "desktop"),
        auth="clerk",
    ),
    PresetMatrixCase(
        name="web-backend-better-auth-mobile-tv-desktop",
        targets=("web", "backend", "mobile", "tv", "desktop"),
        auth="better-auth",
    ),
    PresetMatrixCase(
        name="all-targets-clerk",
        targets=(
            "python",
            "typescript-cli",
            "web",
            "backend",
            "mobile",
            "tv",
            "desktop",
        ),
        auth="clerk",
    ),
    PresetMatrixCase(
        name="all-targets-better-auth",
        targets=(
            "python",
            "typescript-cli",
            "web",
            "backend",
            "mobile",
            "tv",
            "desktop",
        ),
        auth="better-auth",
    ),
)


APP_DIRS_BY_TARGET: dict[str, Path] = {
    "python": Path("apps/python"),
    "typescript-cli": Path("apps/typescript-cli"),
    "web": Path("apps/web"),
    "backend": Path("apps/backend"),
    "desktop": Path("apps/desktop"),
    "mobile": Path("apps/mobile"),
    "tv": Path("apps/tv"),
}


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


@pytest.mark.parametrize("case", MATRIX_CASES, ids=[case.name for case in MATRIX_CASES])
def test_required_preset_matrix_scaffold_contract(
    tmp_path: Path,
    case: PresetMatrixCase,
) -> None:
    """Required preset combinations should scaffold successfully with Python files isolated to the lane."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / case.name

    args: list[str] = []
    for target in case.targets:
        args.extend(["--target", target])
    if case.auth is not None:
        args.extend(["--auth", case.auth])
    args.extend(["--no-interactive", "--output", str(output_dir)])

    result = run_scaffold_command(repo_root=repo_root, args=args)

    assert result.returncode == 0, (
        f"Expected preset matrix case '{case.name}' to scaffold successfully.\n"
        f"targets: {case.targets}\n"
        f"auth: {case.auth}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    assert (output_dir / ".gitignore").exists(), "root .gitignore must exist"
    assert not (output_dir / "pyproject.toml").exists(), (
        "root pyproject.toml must not exist"
    )
    assert not (output_dir / ".python-version").exists(), (
        "root .python-version must not exist"
    )

    for target in case.targets:
        app_dir = APP_DIRS_BY_TARGET.get(target)
        if app_dir is not None:
            assert (output_dir / app_dir).exists(), (
                f"Expected app directory for target '{target}' in case '{case.name}'"
            )

    python_lane_pyproject = output_dir / "apps" / "python" / "pyproject.toml"
    if "python" in case.targets:
        assert python_lane_pyproject.exists(), "python target requires lane pyproject"
        assert (output_dir / "apps" / "python" / ".python-version").exists(), (
            "python target requires lane .python-version"
        )
        assert not (output_dir / "apps" / "python" / ".python-version").is_symlink(), (
            "python target keeps .python-version as a lane-local file"
        )

    if case.auth is not None:
        backend_auth_config = (
            output_dir / "apps" / "backend" / "convex" / "auth.config.ts"
        )
        assert backend_auth_config.exists(), (
            "auth matrix cases require backend auth config"
        )

        web_auth_provider = output_dir / "apps" / "web" / "src" / "auth-provider.ts"
        web_auth_client = output_dir / "apps" / "web" / "src" / "auth-client.ts"
        if case.auth == "clerk":
            assert web_auth_provider.exists(), (
                "clerk variants require auth-provider scaffold"
            )
            assert not web_auth_client.exists(), (
                "clerk variants should not scaffold better-auth client"
            )
        if case.auth == "better-auth":
            assert web_auth_client.exists(), (
                "better-auth variants require auth-client scaffold"
            )
            assert not web_auth_provider.exists(), (
                "better-auth variants should not scaffold clerk provider"
            )
