from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass


DEFAULT_BRANCH_NAME = "main"
DEFAULT_WORKFLOW_NAME = "CI"
ADVISORY_CHECK_NAME = "Secret Scan (Advisory)"


class SecureRepoError(RuntimeError):
    """Raised when the secure-repo flow cannot continue."""


@dataclass(frozen=True)
class SecureRepoPlan:
    repo: str
    branch: str
    include_admins: bool
    required_approvals: int
    required_checks: tuple[str, ...]
    branch_protection_payload: dict[str, object]


def parse_non_negative_int(raw_value: str) -> int:
    value = raw_value.strip()
    if value == "" or not value.isdigit():
        raise ValueError("--required-approvals must be a non-negative integer")
    return int(value)


def build_branch_protection_payload(
    *, required_checks: tuple[str, ...], include_admins: bool, required_approvals: int
) -> dict[str, object]:
    return {
        "required_status_checks": {
            "strict": True,
            "contexts": list(required_checks),
        },
        "enforce_admins": include_admins,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": required_approvals,
        },
        "restrictions": None,
        "required_linear_history": True,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "required_conversation_resolution": True,
    }


def run_secure_repo(
    *,
    repo: str | None,
    branch: str,
    required_checks: tuple[str, ...],
    workflow_name: str,
    required_approvals: int,
    auto_detect_checks: bool,
    include_admins: bool,
    dry_run: bool,
) -> int:
    if not auto_detect_checks and not required_checks:
        raise SecureRepoError(
            "no required checks supplied. Add --required-check values or omit --no-auto-detect-checks"
        )

    if _needs_gh(
        dry_run=dry_run,
        repo=repo,
        required_checks=required_checks,
        auto_detect_checks=auto_detect_checks,
    ):
        _ensure_gh_available()

    resolved_repo = repo or _detect_repo_name()
    resolved_checks = _resolve_required_checks(
        repo=resolved_repo,
        branch=branch,
        workflow_name=workflow_name,
        required_checks=required_checks,
        auto_detect_checks=auto_detect_checks,
    )

    plan = SecureRepoPlan(
        repo=resolved_repo,
        branch=branch,
        include_admins=include_admins,
        required_approvals=required_approvals,
        required_checks=resolved_checks,
        branch_protection_payload=build_branch_protection_payload(
            required_checks=resolved_checks,
            include_admins=include_admins,
            required_approvals=required_approvals,
        ),
    )
    _print_plan_summary(plan)

    if dry_run:
        _print_dry_run_summary(plan)
        return 0

    _ensure_gh_auth()
    _enable_dependabot_security_updates(plan.repo)
    _apply_branch_protection(plan)
    _print_verified_state(plan)
    return 0


def _needs_gh(
    *,
    dry_run: bool,
    repo: str | None,
    required_checks: tuple[str, ...],
    auto_detect_checks: bool,
) -> bool:
    if not dry_run:
        return True
    if repo is None:
        return True
    if not required_checks and auto_detect_checks:
        return True
    return False


def _ensure_gh_available() -> None:
    if shutil.which("gh") is None:
        raise SecureRepoError("gh CLI is required for this operation")


def _run_command(
    command: list[str], *, input_text: str | None = None
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            input=input_text,
            check=False,
        )
    except FileNotFoundError as exc:
        raise SecureRepoError("gh CLI is required for this operation") from exc


def _require_success(
    result: subprocess.CompletedProcess[str], *, error_message: str
) -> str:
    if result.returncode == 0:
        return result.stdout.strip()

    details = (result.stderr or result.stdout).strip()
    if details:
        raise SecureRepoError(f"{error_message}: {details}")
    raise SecureRepoError(error_message)


def _detect_repo_name() -> str:
    result = _run_command(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"]
    )
    output = _require_success(result, error_message="failed to auto-detect repository")
    if output == "":
        raise SecureRepoError("failed to auto-detect repository")
    return output


def _resolve_required_checks(
    *,
    repo: str,
    branch: str,
    workflow_name: str,
    required_checks: tuple[str, ...],
    auto_detect_checks: bool,
) -> tuple[str, ...]:
    if required_checks:
        normalized_checks = _dedupe_checks(required_checks)
        if normalized_checks:
            return normalized_checks

    if not auto_detect_checks:
        raise SecureRepoError("no required checks configured")

    run_id = _detect_latest_successful_run_id(
        repo=repo,
        branch=branch,
        workflow_name=workflow_name,
    )
    discovered_checks = _discover_required_checks(repo=repo, run_id=run_id)
    if not discovered_checks:
        raise SecureRepoError(
            "auto-detection found no required checks; pass --required-check explicitly"
        )
    return discovered_checks


def _dedupe_checks(required_checks: tuple[str, ...]) -> tuple[str, ...]:
    unique_checks: list[str] = []
    for check in required_checks:
        normalized = check.strip()
        if normalized == "" or normalized in unique_checks:
            continue
        unique_checks.append(normalized)
    return tuple(unique_checks)


def _detect_latest_successful_run_id(
    *, repo: str, branch: str, workflow_name: str
) -> str:
    result = _run_command(
        [
            "gh",
            "run",
            "list",
            "--repo",
            repo,
            "--branch",
            branch,
            "--workflow",
            workflow_name,
            "--status",
            "completed",
            "--json",
            "databaseId,conclusion",
            "--limit",
            "30",
        ]
    )
    output = _require_success(
        result,
        error_message="failed to inspect workflow runs for required-check auto-detection",
    )
    try:
        runs = json.loads(output)
    except json.JSONDecodeError as exc:
        raise SecureRepoError(
            "failed to parse workflow-run data during required-check auto-detection"
        ) from exc

    if not isinstance(runs, list):
        raise SecureRepoError(
            "failed to parse workflow-run data during required-check auto-detection"
        )

    for item in runs:
        if not isinstance(item, dict):
            continue
        if item.get("conclusion") != "success":
            continue
        run_id = item.get("databaseId")
        if isinstance(run_id, int):
            return str(run_id)
        if isinstance(run_id, str) and run_id.strip() != "":
            return run_id.strip()

    raise SecureRepoError(
        "could not auto-detect required checks: no successful workflow run found "
        f"for workflow '{workflow_name}' on branch '{branch}'"
    )


def _discover_required_checks(*, repo: str, run_id: str) -> tuple[str, ...]:
    result = _run_command(
        ["gh", "run", "view", run_id, "--repo", repo, "--json", "jobs"]
    )
    output = _require_success(
        result,
        error_message="failed to inspect workflow jobs for required-check auto-detection",
    )
    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        raise SecureRepoError(
            "failed to parse workflow-job data during required-check auto-detection"
        ) from exc

    if not isinstance(payload, dict):
        raise SecureRepoError(
            "failed to parse workflow-job data during required-check auto-detection"
        )

    jobs = payload.get("jobs", [])
    if not isinstance(jobs, list):
        raise SecureRepoError(
            "failed to parse workflow-job data during required-check auto-detection"
        )

    discovered_checks: list[str] = []
    for job in jobs:
        if not isinstance(job, dict):
            continue
        name = job.get("name")
        if not isinstance(name, str):
            continue
        normalized = name.strip()
        if normalized == "" or normalized == ADVISORY_CHECK_NAME:
            continue
        if normalized not in discovered_checks:
            discovered_checks.append(normalized)

    return tuple(discovered_checks)


def _ensure_gh_auth() -> None:
    result = _run_command(["gh", "auth", "status"])
    if result.returncode != 0:
        raise SecureRepoError("gh auth status failed. Run 'gh auth login' first")


def _enable_dependabot_security_updates(repo: str) -> None:
    result = _run_command(
        [
            "gh",
            "api",
            "--method",
            "PATCH",
            f"repos/{repo}",
            "-f",
            "security_and_analysis[dependabot_security_updates][status]=enabled",
        ]
    )
    _require_success(
        result,
        error_message="failed to enable dependabot_security_updates",
    )


def _apply_branch_protection(plan: SecureRepoPlan) -> None:
    payload_text = json.dumps(plan.branch_protection_payload)
    result = _run_command(
        [
            "gh",
            "api",
            "--method",
            "PUT",
            f"repos/{plan.repo}/branches/{plan.branch}/protection",
            "--input",
            "-",
        ],
        input_text=payload_text,
    )
    _require_success(result, error_message="failed to configure branch protection")


def _print_plan_summary(plan: SecureRepoPlan) -> None:
    print("Configuring repository protections")
    print(f"- repo: {plan.repo}")
    print(f"- branch: {plan.branch}")
    print(f"- include admins: {1 if plan.include_admins else 0}")
    print(f"- required approvals: {plan.required_approvals}")
    print(f"- required checks ({len(plan.required_checks)}):")
    for check_name in plan.required_checks:
        print(f"  - {check_name}")


def _print_dry_run_summary(plan: SecureRepoPlan) -> None:
    print()
    print("DRY RUN: no GitHub settings were changed.")
    print("- action: Enable dependabot_security_updates")
    print(f"- action: Configure branch protection on {plan.branch}")
    print("  - Require a pull request before merging")
    print("  - Require status checks to pass before merging")
    print("  - Require branches to be up to date before merging")
    print("  - Require conversation resolution")
    print("  - Require linear history")
    print("  - Restrict force pushes and branch deletions")
    print()
    print("Planned branch-protection payload:")
    print(json.dumps(plan.branch_protection_payload, indent=2))


def _fetch_json(endpoint: str) -> dict[str, object]:
    result = _run_command(["gh", "api", endpoint])
    output = _require_success(result, error_message=f"failed to fetch {endpoint}")
    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        raise SecureRepoError(f"failed to parse {endpoint} response") from exc
    if not isinstance(payload, dict):
        raise SecureRepoError(f"failed to parse {endpoint} response")
    return payload


def _print_verified_state(plan: SecureRepoPlan) -> None:
    print()
    print("Protections applied. Verifying state...")
    repo_payload = _fetch_json(f"repos/{plan.repo}")
    repo_security = repo_payload.get("security_and_analysis")
    dependabot_security_updates = None
    if isinstance(repo_security, dict):
        dependabot_payload = repo_security.get("dependabot_security_updates")
        if isinstance(dependabot_payload, dict):
            dependabot_security_updates = dependabot_payload.get("status")

    print(
        json.dumps(
            {
                "visibility": repo_payload.get("visibility"),
                "private": repo_payload.get("private"),
                "default_branch": repo_payload.get("default_branch"),
                "dependabot_security_updates": dependabot_security_updates,
            },
            indent=2,
        )
    )

    protection_payload = _fetch_json(
        f"repos/{plan.repo}/branches/{plan.branch}/protection"
    )
    required_status_checks = protection_payload.get("required_status_checks")
    required_pull_request_reviews = protection_payload.get(
        "required_pull_request_reviews"
    )
    required_conversation_resolution = protection_payload.get(
        "required_conversation_resolution"
    )
    required_linear_history = protection_payload.get("required_linear_history")
    allow_force_pushes = protection_payload.get("allow_force_pushes")
    allow_deletions = protection_payload.get("allow_deletions")
    enforce_admins = protection_payload.get("enforce_admins")

    print(
        json.dumps(
            {
                "required_pull_request_reviews": required_pull_request_reviews
                is not None,
                "enforce_admins": _enabled_flag(enforce_admins),
                "required_status_checks": _contexts(required_status_checks),
                "strict_status_checks": _strict_flag(required_status_checks),
                "required_conversation_resolution": _enabled_flag(
                    required_conversation_resolution
                ),
                "required_linear_history": _enabled_flag(required_linear_history),
                "allow_force_pushes": _enabled_flag(allow_force_pushes),
                "allow_deletions": _enabled_flag(allow_deletions),
            },
            indent=2,
        )
    )
    print()
    print("Done.")


def _enabled_flag(payload: object) -> bool | None:
    if isinstance(payload, dict):
        enabled = payload.get("enabled")
        if isinstance(enabled, bool):
            return enabled
    if isinstance(payload, bool):
        return payload
    return None


def _contexts(payload: object) -> list[str] | None:
    if not isinstance(payload, dict):
        return None
    contexts = payload.get("contexts")
    if not isinstance(contexts, list):
        return None
    return [context for context in contexts if isinstance(context, str)]


def _strict_flag(payload: object) -> bool | None:
    if not isinstance(payload, dict):
        return None
    strict = payload.get("strict")
    if isinstance(strict, bool):
        return strict
    return None
