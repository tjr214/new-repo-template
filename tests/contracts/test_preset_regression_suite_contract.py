from __future__ import annotations

from pathlib import Path


def test_ci_workflow_includes_dedicated_preset_regression_job() -> None:
    """CI should run a dedicated regression contract suite for preset coverage."""

    repo_root = Path(__file__).resolve().parents[2]
    workflow_text = (repo_root / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )

    assert "preset-regression-suite:" in workflow_text
    assert "name: Preset Regression Suite" in workflow_text
    assert "Run preset regression contract suite" in workflow_text
    assert "tests/contracts/test_required_preset_matrix_contract.py" in workflow_text
    assert "tests/contracts/test_target_matrix_and_auth_contract.py" in workflow_text
    assert "tests/contracts/test_fullstack_auth_wiring_contract.py" in workflow_text


def test_regression_suite_docs_are_present_and_linked() -> None:
    """Regression suite policy should be documented and linked from README."""

    repo_root = Path(__file__).resolve().parents[2]
    policy_path = repo_root / "docs" / "REGRESSION_SUITE.md"

    assert policy_path.exists(), "Expected docs/REGRESSION_SUITE.md"

    policy_text = policy_path.read_text(encoding="utf-8")
    assert "Regression Suite Policy" in policy_text
    assert "Preset Regression Suite" in policy_text
    assert "test_required_preset_matrix_contract.py" in policy_text
    assert "test_target_matrix_and_auth_contract.py" in policy_text
    assert "test_fullstack_auth_wiring_contract.py" in policy_text

    readme_text = (repo_root / "README.md").read_text(encoding="utf-8")
    assert "docs/REGRESSION_SUITE.md" in readme_text
