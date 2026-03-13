from __future__ import annotations

from pathlib import Path

import yaml


def _expected_required_check_names(repo_root: Path) -> list[str]:
    workflow_path = repo_root / ".github" / "workflows" / "ci.yml"
    workflow_data = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    jobs = workflow_data["jobs"]

    matrix_job = jobs["test-matrix"]
    matrix_name_template = matrix_job["name"]
    matrix_values = matrix_job["strategy"]["matrix"]["os"]
    matrix_names = [
        matrix_name_template.replace("${{ matrix.os }}", os_name)
        for os_name in matrix_values
    ]

    return [
        *matrix_names,
        jobs["preset-regression-suite"]["name"],
        jobs["versions-guardrail"]["name"],
    ]


def test_branch_protection_guidance_doc_lists_required_status_checks() -> None:
    """Branch protection guidance should document required CI status checks."""

    repo_root = Path(__file__).resolve().parents[2]
    guidance_path = repo_root / "docs" / "BRANCH_PROTECTION.md"

    assert guidance_path.exists(), (
        "Expected branch protection guidance doc at docs/BRANCH_PROTECTION.md"
    )

    guidance_text = guidance_path.read_text(encoding="utf-8")
    assert "Branch Protection" in guidance_text
    assert "scripts/configure-repo-protections.sh" in guidance_text
    assert "Require a pull request before merging" in guidance_text

    for check_name in _expected_required_check_names(repo_root):
        assert check_name in guidance_text

    assert "Secret Scan (Advisory)" in guidance_text
    assert "continue-on-error: true" in guidance_text


def test_readme_links_branch_protection_guidance() -> None:
    """README should link branch-protection guidance for maintainers."""

    repo_root = Path(__file__).resolve().parents[2]
    readme_text = (repo_root / "README.md").read_text(encoding="utf-8")
    assert "docs/BRANCH_PROTECTION.md" in readme_text
