from __future__ import annotations

from pathlib import Path


def test_dependency_upgrade_policy_doc_is_present_and_linked() -> None:
    """M5 should document dependency-upgrade governance and maintainer commands."""

    repo_root = Path(__file__).resolve().parents[2]
    policy_path = repo_root / "docs" / "DEPENDENCY_UPGRADE_POLICY.md"

    assert policy_path.exists(), "Expected docs/DEPENDENCY_UPGRADE_POLICY.md"

    policy_text = policy_path.read_text(encoding="utf-8")
    assert "Dependency Upgrade and Versioning Policy" in policy_text
    assert "nurt versions check --check-lockfiles --check-latest" in policy_text
    assert "nurt versions update" in policy_text
    assert "bun.lock" in policy_text
    assert "weekly" in policy_text
    assert "monthly" in policy_text

    readme_text = (repo_root / "README.md").read_text(encoding="utf-8")
    assert "docs/DEPENDENCY_UPGRADE_POLICY.md" in readme_text


def test_optional_signing_design_is_documented_and_has_disabled_default_workflow() -> (
    None
):
    """Optional signing must be documented with a disabled-by-default workflow path."""

    repo_root = Path(__file__).resolve().parents[2]
    signing_path = repo_root / "docs" / "OPTIONAL_SIGNING_PIPELINE.md"
    release_workflow_path = repo_root / ".github" / "workflows" / "release.yml"

    assert signing_path.exists(), "Expected docs/OPTIONAL_SIGNING_PIPELINE.md"
    assert release_workflow_path.exists(), "Expected .github/workflows/release.yml"

    signing_text = signing_path.read_text(encoding="utf-8")
    assert "Optional Signing Pipeline" in signing_text
    assert "disabled by default" in signing_text
    assert "MACOS_CERTIFICATE_P12_BASE64" in signing_text
    assert "MACOS_CERTIFICATE_PASSWORD" in signing_text
    assert "APPLE_DEVELOPER_ID" in signing_text
    assert "APPLE_TEAM_ID" in signing_text
    assert "ANDROID_KEYSTORE_BASE64" in signing_text
    assert "ANDROID_KEYSTORE_PASSWORD" in signing_text
    assert "ANDROID_KEY_ALIAS" in signing_text
    assert "ANDROID_KEY_PASSWORD" in signing_text

    release_workflow_text = release_workflow_path.read_text(encoding="utf-8")
    assert "workflow_dispatch" in release_workflow_text
    assert "enable_signing" in release_workflow_text
    assert 'default: "false"' in release_workflow_text
    assert "if: ${{ inputs.enable_signing == 'true' }}" in release_workflow_text


def test_release_checklist_doc_is_present_and_linked() -> None:
    """Phased rollout release checklist should be documented for M5 closeout."""

    repo_root = Path(__file__).resolve().parents[2]
    checklist_path = repo_root / "docs" / "RELEASE_CHECKLIST.md"

    assert checklist_path.exists(), "Expected docs/RELEASE_CHECKLIST.md"

    checklist_text = checklist_path.read_text(encoding="utf-8")
    assert "Release Checklist" in checklist_text
    assert "M4 carryover gate" in checklist_text
    assert "Android TV Emulator" in checklist_text
    assert "NVIDIA Shield" in checklist_text
    assert "Preset Regression Suite" in checklist_text
    assert "Version Baseline Guardrail" in checklist_text

    readme_text = (repo_root / "README.md").read_text(encoding="utf-8")
    assert "docs/RELEASE_CHECKLIST.md" in readme_text
