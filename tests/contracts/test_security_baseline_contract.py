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


def test_root_gitignore_includes_secret_env_guards(tmp_path: Path) -> None:
    """RED: generated root should include .gitignore env-secret baseline."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "security-gitignore-output"

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
        "Expected web scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    gitignore_path = output_dir / ".gitignore"
    assert gitignore_path.exists(), "Root .gitignore should be scaffolded"

    gitignore_text = gitignore_path.read_text(encoding="utf-8")
    assert "node_modules/" in gitignore_text
    assert "**/node_modules/" in gitignore_text
    assert ".env" in gitignore_text
    assert ".env.*" in gitignore_text
    assert "!.env.example" in gitignore_text


def test_selected_targets_each_receive_env_example_placeholders(tmp_path: Path) -> None:
    """RED: each selected target should include placeholder-only .env.example."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "security-env-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "python",
            "--target",
            "desktop",
            "--target",
            "mobile",
            "--target",
            "tv",
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
        "Expected multi-target scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    expected_env_examples = [
        output_dir / "apps" / "python" / ".env.example",
        output_dir / "apps" / "desktop" / ".env.example",
        output_dir / "apps" / "mobile" / ".env.example",
        output_dir / "apps" / "tv" / ".env.example",
        output_dir / "apps" / "web" / ".env.example",
        output_dir / "apps" / "backend" / ".env.example",
    ]
    for env_example in expected_env_examples:
        assert env_example.exists(), f"Expected env placeholder file: {env_example}"
        text = env_example.read_text(encoding="utf-8")
        assert "=" in text, "env placeholder file should define variable keys"
        assert "pk_live_" not in text
        assert "sk_live_" not in text


def test_template_env_seed_files_exist_and_are_not_gitignored() -> None:
    """Template env seed files must exist and not be hidden by ignore rules."""

    repo_root = Path(__file__).resolve().parents[2]
    required_template_env_files = [
        "src/new_repo_template/snapshot_assets/templates/env/python.env",
        "src/new_repo_template/snapshot_assets/templates/env/web.env",
        "src/new_repo_template/snapshot_assets/templates/env/backend.env",
        "src/new_repo_template/snapshot_assets/templates/env/desktop.env",
        "src/new_repo_template/snapshot_assets/templates/env/mobile.env",
        "src/new_repo_template/snapshot_assets/templates/env/tv.env",
    ]

    for file_path in required_template_env_files:
        absolute_file_path = repo_root / file_path
        assert absolute_file_path.exists(), (
            "Expected template env seed file to exist for scaffold generation: "
            f"{file_path}"
        )

        result = subprocess.run(
            ["git", "check-ignore", "-q", file_path],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0, (
            "Template env seed file is ignored by git rules, which can cause "
            f"clean CI checkouts to miss scaffold assets: {file_path}\n"
            f"stderr:\n{result.stderr}"
        )
