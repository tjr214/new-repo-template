from __future__ import annotations

from pathlib import Path


def test_ci_workflow_runs_versions_guardrail_and_cross_platform_smokes() -> None:
    """CI must enforce governance and run cross-platform command smoke checks."""

    repo_root = Path(__file__).resolve().parents[2]
    workflow_path = repo_root / ".github" / "workflows" / "ci.yml"

    assert workflow_path.exists(), "Expected CI workflow at .github/workflows/ci.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")

    assert "windows-latest" in workflow_text
    assert "macos-latest" in workflow_text
    assert "ubuntu-latest" in workflow_text
    assert "oven-sh/setup-bun@v2" in workflow_text
    assert "Run cross-platform command smoke contracts" in workflow_text
    assert "test_bun_workspace_install_contract.py" in workflow_text
    assert "test_turbo_command_smoke_contract.py" in workflow_text
    assert "test_python_target_scaffold_runs_baseline_commands" in workflow_text
    assert "nurt versions check --check-lockfiles --check-latest" in workflow_text
