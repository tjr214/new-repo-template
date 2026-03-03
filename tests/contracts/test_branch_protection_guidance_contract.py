from __future__ import annotations

from pathlib import Path


def test_branch_protection_guidance_doc_lists_required_status_checks() -> None:
    """Branch protection guidance should document required CI status checks."""

    repo_root = Path(__file__).resolve().parents[2]
    guidance_path = repo_root / "docs" / "BRANCH_PROTECTION.md"

    assert guidance_path.exists(), (
        "Expected branch protection guidance doc at docs/BRANCH_PROTECTION.md"
    )

    guidance_text = guidance_path.read_text(encoding="utf-8")
    assert "Branch Protection" in guidance_text
    assert "Require a pull request before merging" in guidance_text
    assert "Tests (ubuntu-latest)" in guidance_text
    assert "Tests (macos-latest)" in guidance_text
    assert "Tests (windows-latest)" in guidance_text
    assert "Version Baseline Guardrail" in guidance_text
    assert "Secret Scan (Advisory)" in guidance_text
    assert "continue-on-error: true" in guidance_text


def test_readme_links_branch_protection_guidance() -> None:
    """README should link branch-protection guidance for maintainers."""

    repo_root = Path(__file__).resolve().parents[2]
    readme_text = (repo_root / "README.md").read_text(encoding="utf-8")
    assert "docs/BRANCH_PROTECTION.md" in readme_text
