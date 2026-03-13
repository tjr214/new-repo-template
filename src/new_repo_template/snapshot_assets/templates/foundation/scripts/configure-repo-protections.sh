#!/bin/sh

# Configure baseline repository protections for this template and generated repos.
#
# Baseline actions:
# 1) Enable Dependabot security updates.
# 2) Configure branch protection on the target branch:
#    - require pull request before merge
#    - require status checks to pass (and branch up-to-date)
#    - require conversation resolution
#    - require linear history
#    - disable force pushes and branch deletions

set -eu

SCRIPT_NAME=$(basename "$0")
WORKFLOW_NAME="CI"
REPO=""
BRANCH="main"
DRY_RUN=0
AUTO_DETECT_CHECKS=1
INCLUDE_ADMINS=1
REQUIRED_APPROVALS=0
REQUIRED_CHECKS_RAW=""

usage() {
    cat <<EOF
Usage: sh scripts/$SCRIPT_NAME [options]

Options:
  --repo <owner/name>          Target repository (default: current gh repo)
  --branch <branch>            Target protected branch (default: main)
  --required-check <name>      Required status check name (repeatable)
  --workflow <name>            Workflow name used for check auto-discovery (default: CI)
  --required-approvals <n>     Required approving reviews (default: 0)
  --no-auto-detect-checks      Disable check auto-discovery when none are supplied
  --exclude-admins             Do not enforce protections for admins
  --dry-run, -n                Print planned API operations without applying changes
  --help, -h                   Show this help text

Examples:
  sh scripts/$SCRIPT_NAME --repo your-org/your-repo
  sh scripts/$SCRIPT_NAME --dry-run --repo your-org/your-repo \
    --required-check "Tests (ubuntu-latest)" --required-check "Version Baseline Guardrail"
EOF
}

error() {
    printf "Error: %s\n" "$1" >&2
    exit 1
}

has_command() {
    command -v "$1" >/dev/null 2>&1
}

append_required_check() {
    check_name="$1"
    if [ -z "$check_name" ]; then
        error "required check name cannot be empty"
    fi

    if [ -z "$REQUIRED_CHECKS_RAW" ]; then
        REQUIRED_CHECKS_RAW="$check_name"
    else
        REQUIRED_CHECKS_RAW="$REQUIRED_CHECKS_RAW
$check_name"
    fi
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --repo)
            [ "$#" -ge 2 ] || error "--repo requires a value"
            REPO="$2"
            shift 2
            ;;
        --branch)
            [ "$#" -ge 2 ] || error "--branch requires a value"
            BRANCH="$2"
            shift 2
            ;;
        --required-check)
            [ "$#" -ge 2 ] || error "--required-check requires a value"
            append_required_check "$2"
            shift 2
            ;;
        --workflow)
            [ "$#" -ge 2 ] || error "--workflow requires a value"
            WORKFLOW_NAME="$2"
            shift 2
            ;;
        --required-approvals)
            [ "$#" -ge 2 ] || error "--required-approvals requires a value"
            REQUIRED_APPROVALS="$2"
            shift 2
            ;;
        --no-auto-detect-checks)
            AUTO_DETECT_CHECKS=0
            shift 1
            ;;
        --exclude-admins)
            INCLUDE_ADMINS=0
            shift 1
            ;;
        --dry-run|-n)
            DRY_RUN=1
            shift 1
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            error "unknown argument: $1"
            ;;
    esac
done

case "$REQUIRED_APPROVALS" in
    ''|*[!0-9]*)
        error "--required-approvals must be a non-negative integer"
        ;;
esac

if [ "$AUTO_DETECT_CHECKS" -eq 0 ] && [ -z "$REQUIRED_CHECKS_RAW" ]; then
    error "no required checks supplied. Add --required-check values or omit --no-auto-detect-checks"
fi

need_gh=0
if [ "$DRY_RUN" -eq 0 ]; then
    need_gh=1
fi
if [ -z "$REPO" ]; then
    need_gh=1
fi
if [ -z "$REQUIRED_CHECKS_RAW" ] && [ "$AUTO_DETECT_CHECKS" -eq 1 ]; then
    need_gh=1
fi

if [ "$need_gh" -eq 1 ] && ! has_command gh; then
    error "gh CLI is required for this operation"
fi

if [ -z "$REPO" ]; then
    REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
fi

if [ -z "$REQUIRED_CHECKS_RAW" ] && [ "$AUTO_DETECT_CHECKS" -eq 1 ]; then
    runs_json=$(gh run list --repo "$REPO" --branch "$BRANCH" --workflow "$WORKFLOW_NAME" --status completed --json databaseId,conclusion --limit 30)

    run_id=$(printf "%s" "$runs_json" | python3 -c '
import json
import sys

items = json.load(sys.stdin)
for item in items:
    if item.get("conclusion") == "success":
        print(item.get("databaseId", ""))
        break
')

    if [ -z "$run_id" ]; then
        error "could not auto-detect required checks: no successful workflow run found for workflow '$WORKFLOW_NAME' on branch '$BRANCH'"
    fi

    jobs_json=$(gh run view "$run_id" --repo "$REPO" --json jobs)
    discovered_checks=$(printf "%s" "$jobs_json" | python3 -c '
import json
import sys

payload = json.load(sys.stdin)
seen = set()
for job in payload.get("jobs", []):
    name = job.get("name", "").strip()
    if not name:
        continue
    if name == "Secret Scan (Advisory)":
        continue
    if name in seen:
        continue
    seen.add(name)
    print(name)
')

    if [ -z "$discovered_checks" ]; then
        error "auto-detection found no required checks; pass --required-check explicitly"
    fi

    while IFS= read -r check_name; do
        if [ -n "$check_name" ]; then
            append_required_check "$check_name"
        fi
    done <<EOF
$discovered_checks
EOF
fi

if [ -z "$REQUIRED_CHECKS_RAW" ]; then
    error "no required checks configured"
fi

check_count=$(printf "%s\n" "$REQUIRED_CHECKS_RAW" | python3 -c '
import sys
checks = [line.strip() for line in sys.stdin.read().splitlines() if line.strip()]
print(len(checks))
')

if [ "$check_count" -eq 0 ]; then
    error "no required checks configured"
fi

branch_protection_payload=$(REQUIRED_CHECKS_RAW="$REQUIRED_CHECKS_RAW" INCLUDE_ADMINS="$INCLUDE_ADMINS" REQUIRED_APPROVALS="$REQUIRED_APPROVALS" python3 -c '
import json
import os

checks = [line.strip() for line in os.environ.get("REQUIRED_CHECKS_RAW", "").splitlines() if line.strip()]
include_admins = os.environ.get("INCLUDE_ADMINS", "1") == "1"
required_approvals = int(os.environ.get("REQUIRED_APPROVALS", "0"))

payload = {
    "required_status_checks": {
        "strict": True,
        "contexts": checks,
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

print(json.dumps(payload))
')

printf "Configuring repository protections\n"
printf -- "- repo: %s\n" "$REPO"
printf -- "- branch: %s\n" "$BRANCH"
printf -- "- include admins: %s\n" "$INCLUDE_ADMINS"
printf -- "- required approvals: %s\n" "$REQUIRED_APPROVALS"
printf -- "- required checks (%s):\n" "$check_count"
printf "%s\n" "$REQUIRED_CHECKS_RAW" | while IFS= read -r check_name; do
    if [ -n "$check_name" ]; then
        printf "  - %s\n" "$check_name"
    fi
done

if [ "$DRY_RUN" -eq 1 ]; then
    printf "\nDRY RUN: no GitHub settings were changed.\n"
    printf -- "- action: Enable dependabot_security_updates\n"
    printf -- "- action: Configure branch protection on %s\n" "$BRANCH"
    printf "  - Require a pull request before merging\n"
    printf "  - Require status checks to pass before merging\n"
    printf "  - Require branches to be up to date before merging\n"
    printf "  - Require conversation resolution\n"
    printf "  - Require linear history\n"
    printf "  - Restrict force pushes and branch deletions\n"
    printf "\nPlanned branch-protection payload:\n%s\n" "$branch_protection_payload"
    exit 0
fi

if ! gh auth status >/dev/null 2>&1; then
    error "gh auth status failed. Run 'gh auth login' first"
fi

gh api --method PATCH "repos/$REPO" -f "security_and_analysis[dependabot_security_updates][status]=enabled" >/dev/null

printf "%s" "$branch_protection_payload" | gh api --method PUT "repos/$REPO/branches/$BRANCH/protection" --input - >/dev/null

printf "\nProtections applied. Verifying state...\n"
gh api "repos/$REPO" --jq '{visibility, private, default_branch, dependabot_security_updates: .security_and_analysis.dependabot_security_updates.status}'
gh api "repos/$REPO/branches/$BRANCH/protection" --jq '{required_pull_request_reviews: (.required_pull_request_reviews != null), enforce_admins: .enforce_admins.enabled, required_status_checks: .required_status_checks.contexts, strict_status_checks: .required_status_checks.strict, required_conversation_resolution: .required_conversation_resolution.enabled, required_linear_history: .required_linear_history.enabled, allow_force_pushes: .allow_force_pushes.enabled, allow_deletions: .allow_deletions.enabled}'

printf "\nDone.\n"
