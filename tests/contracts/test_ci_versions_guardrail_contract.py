from __future__ import annotations

from pathlib import Path


def test_ci_workflow_runs_versions_guardrail_command() -> None:
    """RED: CI must enforce versions+lockfile guardrail command."""

    repo_root = Path(__file__).resolve().parents[2]
    workflow_path = repo_root / ".github" / "workflows" / "ci.yml"

    assert workflow_path.exists(), "Expected CI workflow at .github/workflows/ci.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")

    assert "nurt versions check --check-lockfiles --check-latest" in workflow_text
