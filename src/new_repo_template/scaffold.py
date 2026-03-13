from __future__ import annotations

import argparse
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from new_repo_template.snapshot_assets_loader import load_template_text


@dataclass(frozen=True)
class ScaffoldPlan:
    targets: tuple[str, ...]
    output: Path
    paths: tuple[str, ...]
    auth: str | None


TARGET_CHOICES: tuple[str, ...] = (
    "foundation",
    "python",
    "web",
    "backend",
    "desktop",
    "mobile",
    "tv",
)

FOUNDATION_CORE_PATHS: tuple[str, ...] = (
    "apps/",
    "packages/",
    ".gitignore",
    "eslint.config.mjs",
    "package.json",
    "turbo.json",
)

FOUNDATION_GOVERNANCE_PATHS: tuple[str, ...] = (
    "btca.config.jsonc",
    "AGENTS.md",
    "PLAN.md",
    "README.md",
    "README.BMAD-GUIDE.md",
    "README.RALPH.md",
    "PROGRESS.md",
    "scripts/",
    "scripts/RALPH.sh",
    "scripts/configure-repo-protections.sh",
    "scripts/synthetic-quotas.sh",
    "scripts/task-template-schema.json",
    "scripts/validate_template.py",
    "scripts/visualize_plan.py",
    "docs/",
    "docs/archive/",
    "docs/archive/plans/",
    "docs/archive/progress/",
    "docs/session-summaries/",
    "docs/tasks/",
    "docs/tasks/task-template.yaml",
    "docs/tasks/task-template-example.yaml",
    "docs/workflows/",
    "docs/workflows/export-to-ralph/",
    "docs/workflows/export-to-ralph/workflow.md",
    "docs/workflows/export-to-ralph/steps/",
    "docs/workflows/export-to-ralph/steps/step-01-detect-context.md",
    "docs/workflows/export-to-ralph/steps/step-02-extract.md",
    "docs/workflows/export-to-ralph/steps/step-03-transform.md",
    "docs/workflows/export-to-ralph/steps/step-04-write-file.md",
    ".agent/",
    ".agent/rules/",
    ".agent/rules/general-rules.md",
    ".agent/workflows/",
    ".agent/workflows/project/",
    ".agent/workflows/project/project-export-bmad-to-ralph.md",
    ".opencode/",
    ".opencode/command/",
    ".opencode/command/project-export-bmad-to-ralph.md",
    ".opencode/command/project-get-back-to-work.md",
    ".opencode/command/project-resume-progress-from-last-checkpoint.md",
    ".opencode/command/project-save-progress-to-checkpoint.md",
    ".opencode/command/project-setup-or-update-btca.md",
    ".opencode/command/project-where-did-we-leave-off.md",
    ".opencode/command/repo-git-commit-and-push.md",
    ".opencode/command/repo-git-difference-between-branch-and-main.md",
    ".opencode/command/repo-git-merge.md",
    ".opencode/command/repo-git-new-branch.md",
    ".opencode/command/repo-git-what-has-changed.md",
)

FOUNDATION_PATHS: tuple[str, ...] = FOUNDATION_CORE_PATHS + FOUNDATION_GOVERNANCE_PATHS

FOUNDATION_GOVERNANCE_EMPTY_DIRS: tuple[str, ...] = (
    "docs/archive",
    "docs/archive/plans",
    "docs/archive/progress",
    "docs/session-summaries",
)

FOUNDATION_GOVERNANCE_TEMPLATE_FILES: tuple[tuple[str, str], ...] = (
    ("btca.config.jsonc", "foundation/btca.config.jsonc"),
    ("AGENTS.md", "foundation/AGENTS.md"),
    ("PLAN.md", "foundation/PLAN.md"),
    ("README.md", "foundation/README.md"),
    ("README.BMAD-GUIDE.md", "foundation/README.BMAD-GUIDE.md"),
    ("README.RALPH.md", "foundation/README.RALPH.md"),
    ("PROGRESS.md", "foundation/PROGRESS.md"),
    ("scripts/RALPH.sh", "foundation/scripts/RALPH.sh"),
    (
        "scripts/configure-repo-protections.sh",
        "foundation/scripts/configure-repo-protections.sh",
    ),
    (
        "scripts/synthetic-quotas.sh",
        "foundation/scripts/synthetic-quotas.sh",
    ),
    (
        "scripts/task-template-schema.json",
        "foundation/scripts/task-template-schema.json",
    ),
    (
        "scripts/validate_template.py",
        "foundation/scripts/validate_template.py",
    ),
    (
        "scripts/visualize_plan.py",
        "foundation/scripts/visualize_plan.py",
    ),
    ("docs/tasks/task-template.yaml", "foundation/docs/tasks/task-template.yaml"),
    (
        "docs/tasks/task-template-example.yaml",
        "foundation/docs/tasks/task-template-example.yaml",
    ),
    (
        "docs/workflows/export-to-ralph/workflow.md",
        "foundation/docs/workflows/export-to-ralph/workflow.md",
    ),
    (
        "docs/workflows/export-to-ralph/steps/step-01-detect-context.md",
        "foundation/docs/workflows/export-to-ralph/steps/step-01-detect-context.md",
    ),
    (
        "docs/workflows/export-to-ralph/steps/step-02-extract.md",
        "foundation/docs/workflows/export-to-ralph/steps/step-02-extract.md",
    ),
    (
        "docs/workflows/export-to-ralph/steps/step-03-transform.md",
        "foundation/docs/workflows/export-to-ralph/steps/step-03-transform.md",
    ),
    (
        "docs/workflows/export-to-ralph/steps/step-04-write-file.md",
        "foundation/docs/workflows/export-to-ralph/steps/step-04-write-file.md",
    ),
    (".agent/rules/general-rules.md", "foundation/.agent/rules/general-rules.md"),
    (
        ".agent/workflows/project/project-export-bmad-to-ralph.md",
        "foundation/.agent/workflows/project/project-export-bmad-to-ralph.md",
    ),
    (
        ".opencode/command/project-export-bmad-to-ralph.md",
        "foundation/.opencode/command/project-export-bmad-to-ralph.md",
    ),
    (
        ".opencode/command/project-get-back-to-work.md",
        "foundation/.opencode/command/project-get-back-to-work.md",
    ),
    (
        ".opencode/command/project-resume-progress-from-last-checkpoint.md",
        "foundation/.opencode/command/project-resume-progress-from-last-checkpoint.md",
    ),
    (
        ".opencode/command/project-save-progress-to-checkpoint.md",
        "foundation/.opencode/command/project-save-progress-to-checkpoint.md",
    ),
    (
        ".opencode/command/project-setup-or-update-btca.md",
        "foundation/.opencode/command/project-setup-or-update-btca.md",
    ),
    (
        ".opencode/command/project-where-did-we-leave-off.md",
        "foundation/.opencode/command/project-where-did-we-leave-off.md",
    ),
    (
        ".opencode/command/repo-git-commit-and-push.md",
        "foundation/.opencode/command/repo-git-commit-and-push.md",
    ),
    (
        ".opencode/command/repo-git-difference-between-branch-and-main.md",
        "foundation/.opencode/command/repo-git-difference-between-branch-and-main.md",
    ),
    (
        ".opencode/command/repo-git-merge.md",
        "foundation/.opencode/command/repo-git-merge.md",
    ),
    (
        ".opencode/command/repo-git-new-branch.md",
        "foundation/.opencode/command/repo-git-new-branch.md",
    ),
    (
        ".opencode/command/repo-git-what-has-changed.md",
        "foundation/.opencode/command/repo-git-what-has-changed.md",
    ),
)

SHARED_INFRA_PACKAGE_PATHS: tuple[str, ...] = (
    "packages/typescript-config/",
    "packages/typescript-config/package.json",
    "packages/typescript-config/base.json",
    "packages/typescript-config/react-app.json",
    "packages/typescript-config/node.json",
    "packages/typescript-config/expo.json",
    "packages/eslint-config/",
    "packages/eslint-config/package.json",
    "packages/eslint-config/base.mjs",
)

APP_TARGET_DIRS: dict[str, str] = {
    "web": "apps/web/",
    "backend": "apps/backend/",
    "desktop": "apps/desktop/",
    "mobile": "apps/mobile/",
    "tv": "apps/tv/",
}

APP_TARGET_PACKAGE_PATHS: dict[str, str] = {
    "web": "apps/web/package.json",
    "backend": "apps/backend/package.json",
    "desktop": "apps/desktop/package.json",
    "mobile": "apps/mobile/package.json",
    "tv": "apps/tv/package.json",
}

APP_TARGET_PACKAGE_TEMPLATE_FILES: dict[str, str] = {
    "web": "workspace_packages/web_package.json",
    "backend": "workspace_packages/backend_package.json",
    "desktop": "workspace_packages/desktop_package.json",
    "mobile": "workspace_packages/mobile_package.json",
    "tv": "workspace_packages/tv_package.json",
}

WEB_FRAMEWORK_PATHS: tuple[str, ...] = (
    "apps/web/app.config.ts",
    "apps/web/vite.config.ts",
    "apps/web/tsconfig.json",
    "apps/web/index.html",
    "apps/web/src/",
    "apps/web/src/main.tsx",
    "apps/web/src/router.tsx",
    "apps/web/src/routeTree.gen.ts",
    "apps/web/src/styles.css",
    "apps/web/src/routes/",
    "apps/web/src/routes/__root.tsx",
    "apps/web/src/routes/index.tsx",
)

BACKEND_FRAMEWORK_PATHS: tuple[str, ...] = (
    "apps/backend/convex/",
    "apps/backend/convex/http.ts",
    "apps/backend/convex/schema.ts",
    "apps/backend/tsconfig.json",
    "apps/backend/README.md",
)

DESKTOP_FRAMEWORK_PATHS: tuple[str, ...] = (
    "apps/desktop/README.md",
    "apps/desktop/forge.config.ts",
    "apps/desktop/tsconfig.json",
    "apps/desktop/index.html",
    "apps/desktop/src/",
    "apps/desktop/src/main.ts",
    "apps/desktop/src/preload.ts",
    "apps/desktop/src/renderer.ts",
)

MOBILE_FRAMEWORK_PATHS: tuple[str, ...] = (
    "apps/mobile/README.md",
    "apps/mobile/app.json",
    "apps/mobile/eas.json",
    "apps/mobile/babel.config.js",
    "apps/mobile/index.js",
    "apps/mobile/App.tsx",
    "apps/mobile/smoke.test.js",
    "apps/mobile/tsconfig.json",
)

TV_FRAMEWORK_PATHS: tuple[str, ...] = (
    "apps/tv/README.md",
    "apps/tv/app.json",
    "apps/tv/eas.json",
    "apps/tv/babel.config.js",
    "apps/tv/index.js",
    "apps/tv/App.tsx",
    "apps/tv/smoke.test.js",
    "apps/tv/tsconfig.json",
    "apps/tv/scripts/",
    "apps/tv/scripts/patch-android-wrapper.mjs",
    "apps/tv/TV_INPUT_CHECKLIST.md",
    "apps/tv/TV_VALIDATION_LOG.md",
)

SHARED_WORKSPACE_PATHS: tuple[str, ...] = (
    "packages/shared/",
    "packages/shared/package.json",
    "packages/shared/src/",
    "packages/shared/src/index.ts",
)

PYTHON_PATHS: tuple[str, ...] = (
    "apps/python/",
    "apps/python/.python-version",
    "apps/python/pyproject.toml",
    "apps/python/README.md",
    "apps/python/src/python_app/",
    "apps/python/tests/",
)

TARGET_ENV_EXAMPLE_PATHS: dict[str, str] = {
    "python": "apps/python/.env.example",
    "web": "apps/web/.env.example",
    "backend": "apps/backend/.env.example",
    "desktop": "apps/desktop/.env.example",
    "mobile": "apps/mobile/.env.example",
    "tv": "apps/tv/.env.example",
}

CLERK_WIRING_PATHS: tuple[str, ...] = (
    "apps/backend/convex/auth.config.ts",
    "apps/web/src/auth-provider.ts",
)

BETTER_AUTH_WIRING_PATHS: tuple[str, ...] = (
    "apps/backend/convex/auth.config.ts",
    "apps/web/src/auth-client.ts",
)

PYTHON_LANE_PYPROJECT = load_template_text("python_lane_pyproject.toml")

PYTHON_LANE_README = load_template_text("python_lane_readme.md")
PYTHON_LANE_INIT = load_template_text("python_lane_init.py")
PYTHON_LANE_TEST = load_template_text("python_lane_test.txt")

TARGET_ENV_TEMPLATE_FILES: dict[str, str] = {
    "python": "env/python.env",
    "web": "env/web.env",
    "backend": "env/backend.env",
    "desktop": "env/desktop.env",
    "mobile": "env/mobile.env",
    "tv": "env/tv.env",
}

AUTH_ENV_TEMPLATE_FILES: dict[str, dict[str, str]] = {
    "clerk": {
        "web": "auth_env/web_clerk.env",
        "backend": "auth_env/backend_clerk.env",
    },
    "better-auth": {
        "web": "auth_env/web_better_auth.env",
        "backend": "auth_env/backend_better_auth.env",
    },
}

BACKEND_AUTH_CONFIG_TEMPLATE = load_template_text("wiring/backend_auth_config.ts")
WEB_AUTH_PROVIDER_CLERK_TEMPLATE = load_template_text(
    "wiring/web_auth_provider_clerk.ts"
)
WEB_AUTH_CLIENT_BETTER_AUTH_TEMPLATE = load_template_text(
    "wiring/web_auth_client_better_auth.ts"
)
WEB_MAIN_TEMPLATE = load_template_text("fullstack/web_main.tsx")
WEB_ROUTER_TEMPLATE = load_template_text("fullstack/web_router.tsx")
WEB_ROOT_ROUTE_TEMPLATE = load_template_text("fullstack/web_root_route.tsx")
WEB_INDEX_ROUTE_TEMPLATE = load_template_text("fullstack/web_index_route.tsx")
WEB_ROUTE_TREE_TEMPLATE = load_template_text("fullstack/web_route_tree.gen.ts")
WEB_APP_CONFIG_TEMPLATE = load_template_text("fullstack/web_app.config.ts")
WEB_VITE_CONFIG_TEMPLATE = load_template_text("fullstack/web_vite.config.ts")
WEB_TSCONFIG_TEMPLATE = load_template_text("fullstack/web_tsconfig.json")
WEB_INDEX_HTML_TEMPLATE = load_template_text("fullstack/web_index.html")
WEB_STYLES_TEMPLATE = load_template_text("fullstack/web_styles.css")
BACKEND_HTTP_TEMPLATE = load_template_text("fullstack/backend_http.ts")
BACKEND_SCHEMA_TEMPLATE = load_template_text("fullstack/backend_schema.ts")
BACKEND_README_TEMPLATE = load_template_text("fullstack/backend_readme.md")
DESKTOP_MAIN_TEMPLATE = load_template_text("desktop/desktop_main.ts")
DESKTOP_PRELOAD_TEMPLATE = load_template_text("desktop/desktop_preload.ts")
DESKTOP_RENDERER_TEMPLATE = load_template_text("desktop/desktop_renderer.ts")
DESKTOP_RENDERER_WITH_SHARED_TEMPLATE = load_template_text(
    "desktop/desktop_renderer_with_shared.ts"
)
DESKTOP_INDEX_HTML_TEMPLATE = load_template_text("desktop/desktop_index.html")
DESKTOP_TSCONFIG_TEMPLATE = load_template_text("desktop/desktop_tsconfig.json")
DESKTOP_FORGE_CONFIG_TEMPLATE = load_template_text("desktop/desktop_forge.config.ts")
DESKTOP_README_TEMPLATE = load_template_text("desktop/desktop_readme.md")
MOBILE_APP_JSON_TEMPLATE = load_template_text("mobile/mobile_app.json")
MOBILE_EAS_JSON_TEMPLATE = load_template_text("mobile/mobile_eas.json")
MOBILE_BABEL_CONFIG_TEMPLATE = load_template_text("mobile/mobile_babel.config.js")
MOBILE_INDEX_TEMPLATE = load_template_text("mobile/mobile_index.js")
MOBILE_APP_TEMPLATE = load_template_text("mobile/mobile_app.tsx")
MOBILE_SMOKE_TEST_TEMPLATE = load_template_text("mobile/mobile_smoke.test.js")
MOBILE_TSCONFIG_TEMPLATE = load_template_text("mobile/mobile_tsconfig.json")
MOBILE_README_TEMPLATE = load_template_text("mobile/mobile_readme.md")
TV_APP_JSON_TEMPLATE = load_template_text("tv/tv_app.json")
TV_EAS_JSON_TEMPLATE = load_template_text("tv/tv_eas.json")
TV_BABEL_CONFIG_TEMPLATE = load_template_text("tv/tv_babel.config.js")
TV_INDEX_TEMPLATE = load_template_text("tv/tv_index.js")
TV_APP_TEMPLATE = load_template_text("tv/tv_app.tsx")
TV_SMOKE_TEST_TEMPLATE = load_template_text("tv/tv_smoke.test.js")
TV_TSCONFIG_TEMPLATE = load_template_text("tv/tv_tsconfig.json")
TV_PATCH_ANDROID_WRAPPER_TEMPLATE = load_template_text(
    "tv/tv_patch_android_wrapper.mjs"
)
TV_INPUT_CHECKLIST_TEMPLATE = load_template_text("tv/tv_input_checklist.md")
TV_VALIDATION_LOG_TEMPLATE = load_template_text("tv/tv_validation_log.md")
TV_README_TEMPLATE = load_template_text("tv/tv_readme.md")
SHARED_PACKAGE_TEMPLATE = load_template_text("workspace_packages/shared_package.json")
DESKTOP_PACKAGE_WITH_SHARED_TEMPLATE = load_template_text(
    "workspace_packages/desktop_package_with_shared.json"
)
SHARED_INDEX_TEMPLATE = load_template_text("shared/shared_index.ts")
ROOT_GITIGNORE = load_template_text("root_gitignore.txt")
PYTHON_LANE_PYTHON_VERSION = load_template_text(
    "python_lane_python_version.txt"
).rstrip("\n")
ROOT_ESLINT_CONFIG = load_template_text("root_eslint.config.mjs")
ROOT_PACKAGE_JSON = load_template_text("root_package.json")
ROOT_TURBO_JSON = load_template_text("root_turbo.json")
TYPESCRIPT_CONFIG_PACKAGE_TEMPLATE = load_template_text(
    "workspace_packages/typescript_config_package.json"
)
TYPESCRIPT_CONFIG_BASE_TEMPLATE = load_template_text("typescript_configs/base.json")
TYPESCRIPT_CONFIG_REACT_APP_TEMPLATE = load_template_text(
    "typescript_configs/react-app.json"
)
TYPESCRIPT_CONFIG_NODE_TEMPLATE = load_template_text("typescript_configs/node.json")
TYPESCRIPT_CONFIG_EXPO_TEMPLATE = load_template_text("typescript_configs/expo.json")
ESLINT_CONFIG_PACKAGE_TEMPLATE = load_template_text(
    "workspace_packages/eslint_config_package.json"
)
ESLINT_CONFIG_BASE_TEMPLATE = load_template_text("eslint/base.mjs")
BACKEND_TSCONFIG_TEMPLATE = load_template_text("fullstack/backend_tsconfig.json")

SIMULATE_FAILURE_ENV = "NEW_REPO_TEMPLATE_SIMULATE_FAILURE"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="new-repo-template")
    parser.add_argument(
        "--target",
        required=True,
        action="append",
        choices=TARGET_CHOICES,
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--auth", choices=("clerk", "better-auth", "none"))
    parser.add_argument("--no-interactive", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def normalize_targets(raw_targets: list[str]) -> tuple[str, ...]:
    ordered_unique: list[str] = []
    seen: set[str] = set()
    for target in raw_targets:
        if target in seen:
            continue
        seen.add(target)
        ordered_unique.append(target)
    return tuple(ordered_unique)


def validate_args(
    parser: argparse.ArgumentParser, args: argparse.Namespace
) -> tuple[tuple[str, ...], str | None]:
    duplicate_targets: list[str] = []
    seen: set[str] = set()
    for target in args.target:
        if target in seen and target not in duplicate_targets:
            duplicate_targets.append(target)
        seen.add(target)
    if duplicate_targets:
        parser.error(
            "duplicate target selections are not allowed: "
            + ", ".join(duplicate_targets)
        )

    selected_targets = normalize_targets(args.target)

    if "foundation" in selected_targets and len(selected_targets) > 1:
        parser.error("foundation target cannot be combined with other targets")

    has_backend = "backend" in selected_targets
    if has_backend and args.auth is None:
        parser.error(
            "auth option is required when backend target is selected; use clerk, better-auth, or none"
        )

    if args.auth is not None and not has_backend:
        parser.error("auth option is only valid when backend target is selected")

    resolved_auth = None if args.auth in {None, "none"} else str(args.auth)
    return selected_targets, resolved_auth


def resolve_paths(*, targets: tuple[str, ...], auth: str | None) -> tuple[str, ...]:
    paths: list[str] = list(FOUNDATION_PATHS)
    paths.extend(SHARED_INFRA_PACKAGE_PATHS)

    for target in targets:
        if target in APP_TARGET_DIRS:
            paths.append(APP_TARGET_DIRS[target])
        if target in APP_TARGET_PACKAGE_PATHS:
            paths.append(APP_TARGET_PACKAGE_PATHS[target])
        if target == "web":
            paths.extend(WEB_FRAMEWORK_PATHS)
        if target == "backend":
            paths.extend(BACKEND_FRAMEWORK_PATHS)
        if target == "desktop":
            paths.extend(DESKTOP_FRAMEWORK_PATHS)
        if target == "mobile":
            paths.extend(MOBILE_FRAMEWORK_PATHS)
        if target == "tv":
            paths.extend(TV_FRAMEWORK_PATHS)
        if target == "python":
            paths.extend(PYTHON_PATHS)
        if target in TARGET_ENV_EXAMPLE_PATHS:
            paths.append(TARGET_ENV_EXAMPLE_PATHS[target])

    has_shared_workspace = "web" in targets or "backend" in targets
    if has_shared_workspace:
        paths.extend(SHARED_WORKSPACE_PATHS)

    has_backend = "backend" in targets
    if has_backend and auth is not None:
        paths.append("apps/backend/convex/auth.config.ts")
        if "web" in targets and auth == "clerk":
            paths.append("apps/web/src/auth-provider.ts")
        if "web" in targets and auth == "better-auth":
            paths.append("apps/web/src/auth-client.ts")

    return tuple(paths)


def resolve_plan(
    *, targets: tuple[str, ...], output: Path, auth: str | None
) -> ScaffoldPlan:
    return ScaffoldPlan(
        targets=targets,
        output=output,
        paths=resolve_paths(targets=targets, auth=auth),
        auth=auth,
    )


def render_plan(plan: ScaffoldPlan) -> str:
    lines = [
        "Resolved scaffold plan:",
        f"- targets: {', '.join(plan.targets)}",
        f"- output: {plan.output}",
        f"- auth: {plan.auth if plan.auth is not None else 'none'}",
        "- root layout:",
    ]
    lines.extend(f"  - {path}" for path in plan.paths)
    return "\n".join(lines)


def write_root_gitignore(*, output_root: Path) -> None:
    (output_root / ".gitignore").write_text(ROOT_GITIGNORE, encoding="utf-8")


def write_python_lane_python_version(*, lane_root: Path) -> None:
    (lane_root / ".python-version").write_text(
        PYTHON_LANE_PYTHON_VERSION,
        encoding="utf-8",
    )


def write_root_eslint_config(*, output_root: Path) -> None:
    (output_root / "eslint.config.mjs").write_text(
        ROOT_ESLINT_CONFIG,
        encoding="utf-8",
    )


def write_root_package_json(*, output_root: Path) -> None:
    (output_root / "package.json").write_text(ROOT_PACKAGE_JSON, encoding="utf-8")


def write_root_turbo_json(*, output_root: Path) -> None:
    (output_root / "turbo.json").write_text(ROOT_TURBO_JSON, encoding="utf-8")


def write_foundation_governance_assets(*, output_root: Path) -> None:
    for relative_dir in FOUNDATION_GOVERNANCE_EMPTY_DIRS:
        (output_root / relative_dir).mkdir(parents=True, exist_ok=True)

    for destination_relative, template_relative in FOUNDATION_GOVERNANCE_TEMPLATE_FILES:
        destination_path = output_root / destination_relative
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_text(
            load_template_text(template_relative),
            encoding="utf-8",
        )

    for executable_relative in (
        "scripts/RALPH.sh",
        "scripts/configure-repo-protections.sh",
        "scripts/synthetic-quotas.sh",
        "scripts/validate_template.py",
        "scripts/visualize_plan.py",
    ):
        (output_root / executable_relative).chmod(0o755)


def scaffold_foundation_core(*, output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=False)
    (output_root / "apps").mkdir()
    (output_root / "packages").mkdir()
    write_root_gitignore(output_root=output_root)
    write_root_eslint_config(output_root=output_root)
    write_root_package_json(output_root=output_root)
    write_root_turbo_json(output_root=output_root)
    write_foundation_governance_assets(output_root=output_root)


def scaffold_shared_infra_packages(*, output_root: Path) -> None:
    typescript_config_root = output_root / "packages" / "typescript-config"
    typescript_config_root.mkdir(parents=True, exist_ok=True)
    (typescript_config_root / "package.json").write_text(
        TYPESCRIPT_CONFIG_PACKAGE_TEMPLATE,
        encoding="utf-8",
    )
    (typescript_config_root / "base.json").write_text(
        TYPESCRIPT_CONFIG_BASE_TEMPLATE,
        encoding="utf-8",
    )
    (typescript_config_root / "react-app.json").write_text(
        TYPESCRIPT_CONFIG_REACT_APP_TEMPLATE,
        encoding="utf-8",
    )
    (typescript_config_root / "node.json").write_text(
        TYPESCRIPT_CONFIG_NODE_TEMPLATE,
        encoding="utf-8",
    )
    (typescript_config_root / "expo.json").write_text(
        TYPESCRIPT_CONFIG_EXPO_TEMPLATE,
        encoding="utf-8",
    )

    eslint_config_root = output_root / "packages" / "eslint-config"
    eslint_config_root.mkdir(parents=True, exist_ok=True)
    (eslint_config_root / "package.json").write_text(
        ESLINT_CONFIG_PACKAGE_TEMPLATE,
        encoding="utf-8",
    )
    (eslint_config_root / "base.mjs").write_text(
        ESLINT_CONFIG_BASE_TEMPLATE,
        encoding="utf-8",
    )


def scaffold_python_lane(*, output_root: Path) -> None:
    if os.environ.get(SIMULATE_FAILURE_ENV) == "python-after-root":
        raise RuntimeError("simulated scaffold failure after root generation")

    lane_root = output_root / "apps" / "python"
    (lane_root / "src" / "python_app").mkdir(parents=True)
    (lane_root / "tests").mkdir()
    write_python_lane_python_version(lane_root=lane_root)
    (lane_root / "pyproject.toml").write_text(PYTHON_LANE_PYPROJECT, encoding="utf-8")
    (lane_root / "README.md").write_text(PYTHON_LANE_README, encoding="utf-8")
    (lane_root / "src" / "python_app" / "__init__.py").write_text(
        PYTHON_LANE_INIT,
        encoding="utf-8",
    )
    (lane_root / "tests" / "test_smoke.py").write_text(
        PYTHON_LANE_TEST,
        encoding="utf-8",
    )


def scaffold_app_targets(*, output_root: Path, targets: tuple[str, ...]) -> None:
    for target in targets:
        if target in APP_TARGET_DIRS:
            (output_root / APP_TARGET_DIRS[target]).mkdir(parents=True, exist_ok=True)
        package_path = APP_TARGET_PACKAGE_PATHS.get(target)
        if package_path is None:
            continue
        package_template = load_template_text(APP_TARGET_PACKAGE_TEMPLATE_FILES[target])
        if target == "desktop" and "web" in targets:
            package_template = DESKTOP_PACKAGE_WITH_SHARED_TEMPLATE
        (output_root / package_path).write_text(package_template, encoding="utf-8")


def scaffold_web_framework_files(
    *, output_root: Path, targets: tuple[str, ...]
) -> None:
    if "web" not in targets:
        return

    web_root = output_root / "apps" / "web"
    web_src = output_root / "apps" / "web" / "src"
    routes_dir = web_src / "routes"
    routes_dir.mkdir(parents=True, exist_ok=True)

    (web_root / "app.config.ts").write_text(WEB_APP_CONFIG_TEMPLATE, encoding="utf-8")
    (web_root / "vite.config.ts").write_text(WEB_VITE_CONFIG_TEMPLATE, encoding="utf-8")
    (web_root / "tsconfig.json").write_text(WEB_TSCONFIG_TEMPLATE, encoding="utf-8")
    (web_root / "index.html").write_text(WEB_INDEX_HTML_TEMPLATE, encoding="utf-8")

    (web_src / "main.tsx").write_text(WEB_MAIN_TEMPLATE, encoding="utf-8")
    (web_src / "router.tsx").write_text(WEB_ROUTER_TEMPLATE, encoding="utf-8")
    (web_src / "routeTree.gen.ts").write_text(WEB_ROUTE_TREE_TEMPLATE, encoding="utf-8")
    (web_src / "styles.css").write_text(WEB_STYLES_TEMPLATE, encoding="utf-8")
    (routes_dir / "__root.tsx").write_text(WEB_ROOT_ROUTE_TEMPLATE, encoding="utf-8")
    (routes_dir / "index.tsx").write_text(WEB_INDEX_ROUTE_TEMPLATE, encoding="utf-8")


def scaffold_backend_framework_files(
    *, output_root: Path, targets: tuple[str, ...]
) -> None:
    if "backend" not in targets:
        return

    convex_dir = output_root / "apps" / "backend" / "convex"
    convex_dir.mkdir(parents=True, exist_ok=True)

    (convex_dir / "http.ts").write_text(BACKEND_HTTP_TEMPLATE, encoding="utf-8")
    (convex_dir / "schema.ts").write_text(BACKEND_SCHEMA_TEMPLATE, encoding="utf-8")
    (output_root / "apps" / "backend" / "tsconfig.json").write_text(
        BACKEND_TSCONFIG_TEMPLATE,
        encoding="utf-8",
    )
    (output_root / "apps" / "backend" / "README.md").write_text(
        BACKEND_README_TEMPLATE,
        encoding="utf-8",
    )


def scaffold_desktop_framework_files(
    *, output_root: Path, targets: tuple[str, ...]
) -> None:
    if "desktop" not in targets:
        return

    desktop_root = output_root / "apps" / "desktop"
    desktop_src = desktop_root / "src"
    desktop_src.mkdir(parents=True, exist_ok=True)

    (desktop_root / "README.md").write_text(DESKTOP_README_TEMPLATE, encoding="utf-8")
    (desktop_root / "forge.config.ts").write_text(
        DESKTOP_FORGE_CONFIG_TEMPLATE,
        encoding="utf-8",
    )
    (desktop_root / "tsconfig.json").write_text(
        DESKTOP_TSCONFIG_TEMPLATE,
        encoding="utf-8",
    )
    (desktop_root / "index.html").write_text(
        DESKTOP_INDEX_HTML_TEMPLATE,
        encoding="utf-8",
    )
    (desktop_src / "main.ts").write_text(DESKTOP_MAIN_TEMPLATE, encoding="utf-8")
    (desktop_src / "preload.ts").write_text(
        DESKTOP_PRELOAD_TEMPLATE,
        encoding="utf-8",
    )
    renderer_template = DESKTOP_RENDERER_TEMPLATE
    if "web" in targets:
        renderer_template = DESKTOP_RENDERER_WITH_SHARED_TEMPLATE
    (desktop_src / "renderer.ts").write_text(
        renderer_template,
        encoding="utf-8",
    )


def scaffold_shared_workspace_package(
    *, output_root: Path, targets: tuple[str, ...]
) -> None:
    has_shared_workspace = "web" in targets or "backend" in targets
    if not has_shared_workspace:
        return

    shared_src_dir = output_root / "packages" / "shared" / "src"
    shared_src_dir.mkdir(parents=True, exist_ok=True)
    (output_root / "packages" / "shared" / "package.json").write_text(
        SHARED_PACKAGE_TEMPLATE,
        encoding="utf-8",
    )
    (shared_src_dir / "index.ts").write_text(SHARED_INDEX_TEMPLATE, encoding="utf-8")


def scaffold_mobile_framework_files(
    *, output_root: Path, targets: tuple[str, ...]
) -> None:
    if "mobile" not in targets:
        return

    mobile_root = output_root / "apps" / "mobile"
    mobile_root.mkdir(parents=True, exist_ok=True)

    (mobile_root / "README.md").write_text(MOBILE_README_TEMPLATE, encoding="utf-8")
    (mobile_root / "app.json").write_text(MOBILE_APP_JSON_TEMPLATE, encoding="utf-8")
    (mobile_root / "eas.json").write_text(MOBILE_EAS_JSON_TEMPLATE, encoding="utf-8")
    (mobile_root / "babel.config.js").write_text(
        MOBILE_BABEL_CONFIG_TEMPLATE,
        encoding="utf-8",
    )
    (mobile_root / "index.js").write_text(MOBILE_INDEX_TEMPLATE, encoding="utf-8")
    (mobile_root / "App.tsx").write_text(MOBILE_APP_TEMPLATE, encoding="utf-8")
    (mobile_root / "smoke.test.js").write_text(
        MOBILE_SMOKE_TEST_TEMPLATE,
        encoding="utf-8",
    )
    (mobile_root / "tsconfig.json").write_text(
        MOBILE_TSCONFIG_TEMPLATE,
        encoding="utf-8",
    )


def scaffold_tv_framework_files(*, output_root: Path, targets: tuple[str, ...]) -> None:
    if "tv" not in targets:
        return

    tv_root = output_root / "apps" / "tv"
    tv_scripts_dir = tv_root / "scripts"
    tv_root.mkdir(parents=True, exist_ok=True)
    tv_scripts_dir.mkdir(parents=True, exist_ok=True)

    (tv_root / "README.md").write_text(TV_README_TEMPLATE, encoding="utf-8")
    (tv_root / "app.json").write_text(TV_APP_JSON_TEMPLATE, encoding="utf-8")
    (tv_root / "eas.json").write_text(TV_EAS_JSON_TEMPLATE, encoding="utf-8")
    (tv_root / "babel.config.js").write_text(TV_BABEL_CONFIG_TEMPLATE, encoding="utf-8")
    (tv_root / "index.js").write_text(TV_INDEX_TEMPLATE, encoding="utf-8")
    (tv_root / "App.tsx").write_text(TV_APP_TEMPLATE, encoding="utf-8")
    (tv_root / "smoke.test.js").write_text(TV_SMOKE_TEST_TEMPLATE, encoding="utf-8")
    (tv_root / "tsconfig.json").write_text(TV_TSCONFIG_TEMPLATE, encoding="utf-8")
    (tv_scripts_dir / "patch-android-wrapper.mjs").write_text(
        TV_PATCH_ANDROID_WRAPPER_TEMPLATE,
        encoding="utf-8",
    )
    (tv_root / "TV_INPUT_CHECKLIST.md").write_text(
        TV_INPUT_CHECKLIST_TEMPLATE,
        encoding="utf-8",
    )
    (tv_root / "TV_VALIDATION_LOG.md").write_text(
        TV_VALIDATION_LOG_TEMPLATE,
        encoding="utf-8",
    )


def scaffold_target_env_examples(
    *, output_root: Path, targets: tuple[str, ...]
) -> None:
    for target in targets:
        env_path = TARGET_ENV_EXAMPLE_PATHS.get(target)
        if env_path is None:
            continue
        env_template_path = TARGET_ENV_TEMPLATE_FILES[target]
        env_content = load_template_text(env_template_path)
        target_env_file = output_root / env_path
        target_env_file.parent.mkdir(parents=True, exist_ok=True)
        target_env_file.write_text(env_content, encoding="utf-8")


def scaffold_web_backend_env_examples(
    *, output_root: Path, auth: str | None, targets: tuple[str, ...]
) -> None:
    has_web_backend = "web" in targets and "backend" in targets
    if not has_web_backend or auth is None:
        return

    auth_templates = AUTH_ENV_TEMPLATE_FILES[auth]
    web_env = load_template_text(auth_templates["web"])
    backend_env = load_template_text(auth_templates["backend"])

    (output_root / "apps" / "web" / ".env.example").write_text(
        web_env,
        encoding="utf-8",
    )
    (output_root / "apps" / "backend" / ".env.example").write_text(
        backend_env,
        encoding="utf-8",
    )


def scaffold_web_backend_auth_wiring(
    *, output_root: Path, auth: str | None, targets: tuple[str, ...]
) -> None:
    has_backend = "backend" in targets
    if not has_backend or auth is None:
        return

    backend_convex_dir = output_root / "apps" / "backend" / "convex"
    backend_convex_dir.mkdir(parents=True, exist_ok=True)

    backend_auth_config = BACKEND_AUTH_CONFIG_TEMPLATE.replace(
        "{{AUTH_PROVIDER}}", auth
    )
    (backend_convex_dir / "auth.config.ts").write_text(
        backend_auth_config,
        encoding="utf-8",
    )

    has_web = "web" in targets
    if not has_web:
        return

    web_src_dir = output_root / "apps" / "web" / "src"
    web_src_dir.mkdir(parents=True, exist_ok=True)

    if auth == "clerk":
        (web_src_dir / "auth-provider.ts").write_text(
            WEB_AUTH_PROVIDER_CLERK_TEMPLATE,
            encoding="utf-8",
        )
        return

    if auth == "better-auth":
        (web_src_dir / "auth-client.ts").write_text(
            WEB_AUTH_CLIENT_BETTER_AUTH_TEMPLATE,
            encoding="utf-8",
        )


def execute_scaffold_direct(plan: ScaffoldPlan) -> None:
    scaffold_foundation_core(output_root=plan.output)
    scaffold_shared_infra_packages(output_root=plan.output)
    scaffold_app_targets(output_root=plan.output, targets=plan.targets)
    scaffold_web_framework_files(output_root=plan.output, targets=plan.targets)
    scaffold_backend_framework_files(output_root=plan.output, targets=plan.targets)
    scaffold_desktop_framework_files(output_root=plan.output, targets=plan.targets)
    scaffold_mobile_framework_files(output_root=plan.output, targets=plan.targets)
    scaffold_tv_framework_files(output_root=plan.output, targets=plan.targets)
    scaffold_shared_workspace_package(output_root=plan.output, targets=plan.targets)

    if "python" in plan.targets:
        scaffold_python_lane(output_root=plan.output)

    scaffold_target_env_examples(output_root=plan.output, targets=plan.targets)

    scaffold_web_backend_env_examples(
        output_root=plan.output,
        auth=plan.auth,
        targets=plan.targets,
    )
    scaffold_web_backend_auth_wiring(
        output_root=plan.output,
        auth=plan.auth,
        targets=plan.targets,
    )


def execute_scaffold(plan: ScaffoldPlan) -> None:
    if plan.output.exists():
        raise FileExistsError(f"Output path already exists: {plan.output}")

    plan.output.parent.mkdir(parents=True, exist_ok=True)
    stage_container = Path(
        tempfile.mkdtemp(prefix=f".{plan.output.name}.staging-", dir=plan.output.parent)
    )
    stage_output = stage_container / plan.output.name
    staged_plan = ScaffoldPlan(
        targets=plan.targets,
        output=stage_output,
        paths=plan.paths,
        auth=plan.auth,
    )

    try:
        execute_scaffold_direct(staged_plan)
        stage_output.replace(plan.output)
    except Exception:
        shutil.rmtree(stage_container, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(stage_container, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    selected_targets, resolved_auth = validate_args(parser, args)

    if not args.no_interactive:
        parser.error("interactive mode is not implemented yet; use --no-interactive")

    plan = resolve_plan(
        targets=selected_targets, output=args.output, auth=resolved_auth
    )

    if args.dry_run:
        print(render_plan(plan))
        return 0

    try:
        execute_scaffold(plan)
    except Exception as exc:
        parser.exit(status=1, message=f"scaffold failed: {exc}\n")

    print(render_plan(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
