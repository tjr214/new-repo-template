from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import os


def test_foundation_scaffold_non_interactive_dry_run_contract(tmp_path: Path) -> None:
    """RED: foundation scaffold contract should pass once generator exists."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "foundation-output"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "new_repo_template.scaffold",
            "--target",
            "foundation",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, (
        "Expected foundation dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "apps" in combined_output
    assert "packages" in combined_output
    assert ".gitignore" in combined_output
    assert not output_dir.exists(), "--dry-run should not write scaffold output"
