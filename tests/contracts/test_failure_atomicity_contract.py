from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_scaffold_failure_leaves_no_partial_output(tmp_path: Path) -> None:
    """RED: generator failure must not leave partially scaffolded output."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "python-failure-output"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")
    env["NEW_REPO_TEMPLATE_SIMULATE_FAILURE"] = "python-after-root"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "new_repo_template.scaffold",
            "--target",
            "python",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode != 0, "Simulated failure run should return non-zero exit"
    assert not output_dir.exists(), (
        "No partial scaffold output should remain after failure"
    )


def test_add_failure_rolls_back_partial_repo_mutation(tmp_path: Path) -> None:
    """RED: add-mode failure must restore the original repo state."""

    repo_root = Path(__file__).resolve().parents[2]
    generated_repo = tmp_path / "generated-repo"

    scaffold_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "new_repo_template.scaffold",
            "--target",
            "foundation",
            "--no-interactive",
            "--output",
            str(generated_repo),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        check=False,
    )
    assert scaffold_result.returncode == 0, (
        "Expected generated repo fixture to scaffold successfully.\n"
        f"stdout:\n{scaffold_result.stdout}\n"
        f"stderr:\n{scaffold_result.stderr}"
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")
    env["NURT_UPDATE_CHECK_SIMULATE"] = "none"
    env["NURT_ADD_SIMULATE_FAILURE"] = "after-root-python-upgrade"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "new_repo_template.nurt_cli",
            "add",
            "--target",
            "python",
            "--no-interactive",
        ],
        cwd=generated_repo,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode != 0, "Simulated add failure should return non-zero exit"
    assert not (generated_repo / "pyproject.toml").exists(), (
        "Root uv workspace metadata should be rolled back after add failure"
    )
    assert not (generated_repo / "apps" / "python").exists(), (
        "No partial python app tree should remain after add failure"
    )
