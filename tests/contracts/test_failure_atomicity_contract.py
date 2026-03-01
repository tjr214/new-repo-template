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
