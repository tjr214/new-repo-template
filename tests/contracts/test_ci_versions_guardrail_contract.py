from __future__ import annotations

from pathlib import Path


def test_ci_workflow_runs_versions_guardrail_cross_platform_smokes_cache_and_advisory_secret_scan() -> (
    None
):
    """CI must enforce governance, run smoke contracts, and apply cache strategy."""

    repo_root = Path(__file__).resolve().parents[2]
    workflow_path = repo_root / ".github" / "workflows" / "ci.yml"

    assert workflow_path.exists(), "Expected CI workflow at .github/workflows/ci.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")

    assert "windows-latest" in workflow_text
    assert "macos-latest" in workflow_text
    assert "ubuntu-latest" in workflow_text
    assert "concurrency:" in workflow_text
    assert "oven-sh/setup-bun@v2" in workflow_text
    assert "actions/cache@v4" in workflow_text
    assert "~/.cache/uv" in workflow_text
    assert "~/.bun/install/cache" in workflow_text
    assert "Run cross-platform command smoke contracts (non-Windows)" in workflow_text
    assert "Run Windows critical contracts" in workflow_text
    assert "if: ${{ runner.os == 'Windows' }}" in workflow_text
    assert "Run full test suite (non-Windows)" in workflow_text
    assert "if: ${{ runner.os != 'Windows' }}" in workflow_text
    assert "test_bun_workspace_install_contract.py" in workflow_text
    assert "test_convex_backend_smoke_contract.py" in workflow_text
    assert "test_desktop_runtime_smoke_contract.py" in workflow_text
    assert "test_mobile_tv_runtime_smoke_contract.py" in workflow_text
    assert "test_tv_input_hid_contract.py" in workflow_text
    assert "test_turbo_command_smoke_contract.py" in workflow_text
    assert "test_python_target_scaffold_runs_baseline_commands" in workflow_text
    assert "test_required_preset_matrix_contract.py" in workflow_text
    assert "nurt versions check --check-lockfiles --check-latest" in workflow_text
    assert "secret-scan-advisory" in workflow_text
    assert "continue-on-error: true" in workflow_text
    assert "fetch-depth: 0" in workflow_text
    assert "gitleaks/gitleaks-action@v2.3.9" in workflow_text
    assert 'GITLEAKS_ENABLE_COMMENTS: "false"' in workflow_text
    assert 'GITLEAKS_ENABLE_UPLOAD_ARTIFACT: "false"' in workflow_text
