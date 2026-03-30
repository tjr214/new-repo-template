from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from new_repo_template.btca_config_manager import (
    BTCA_CONFIG_RELATIVE_PATH,
    BTCA_DOCS_RELATIVE_PATH,
    BTCA_SIDECAR_RELATIVE_PATH,
    generate_scaffold_btca_files,
    project_contexts_from_projects,
)
from new_repo_template.foundation_manifest import (
    get_foundation_empty_directories,
    get_foundation_scaffold_paths,
    get_foundation_template_file_pairs,
)
from new_repo_template.project_naming import normalize_project_name
from new_repo_template.snapshot_assets_loader import load_template_text


@dataclass(frozen=True)
class ProjectSpec:
    kind: str
    name: str
    auth: str | None = None
    backend_binding: str | None = None
    local_auth: str | None = None
    prod_auth: str | None = None

    @property
    def local_auth_provider(self) -> str | None:
        if self.local_auth is not None:
            return self.local_auth
        return self.auth

    @property
    def prod_auth_provider(self) -> str | None:
        if self.prod_auth is not None:
            return self.prod_auth
        return self.auth

    @property
    def auth_matrix_enabled(self) -> bool:
        return (
            self.local_auth_provider is not None or self.prod_auth_provider is not None
        )

    @property
    def uses_clerk_auth(self) -> bool:
        return "clerk" in {self.local_auth_provider, self.prod_auth_provider}

    @property
    def uses_better_auth(self) -> bool:
        return "better-auth" in {self.local_auth_provider, self.prod_auth_provider}


@dataclass(frozen=True)
class ScaffoldPlan:
    projects: tuple[ProjectSpec, ...]
    output: Path
    paths: tuple[str, ...]


DEFAULT_PROJECT_NAMES: dict[str, str] = {
    "python": "python-app",
    "web": "web",
    "backend": "backend",
    "desktop": "desktop",
    "mobile": "mobile",
    "tv": "tv",
    "typescript-cli": "typescript-cli",
    "python-lib": "python-lib",
    "typescript-lib": "typescript-lib",
}

APP_PROJECT_KINDS: tuple[str, ...] = (
    "python",
    "web",
    "backend",
    "desktop",
    "mobile",
    "tv",
    "typescript-cli",
)

LIBRARY_PROJECT_KINDS: tuple[str, ...] = ("python-lib", "typescript-lib")


TARGET_CHOICES: tuple[str, ...] = (
    "foundation",
    "python",
    "web",
    "backend",
    "desktop",
    "mobile",
    "tv",
    "typescript-cli",
    "python-lib",
    "typescript-lib",
)

FOUNDATION_CORE_PATHS: tuple[str, ...] = (
    "apps/",
    "packages/",
    ".gitignore",
    "eslint.config.mjs",
    "package.json",
    "turbo.json",
)

FOUNDATION_GOVERNANCE_PATHS: tuple[str, ...] = get_foundation_scaffold_paths()

FOUNDATION_PATHS: tuple[str, ...] = FOUNDATION_CORE_PATHS + FOUNDATION_GOVERNANCE_PATHS

FOUNDATION_GOVERNANCE_EMPTY_DIRS: tuple[str, ...] = get_foundation_empty_directories()

FOUNDATION_GOVERNANCE_TEMPLATE_FILES: tuple[tuple[str, str], ...] = (
    get_foundation_template_file_pairs()
)

GENERATED_BTCA_PATHS: tuple[str, ...] = (
    BTCA_CONFIG_RELATIVE_PATH,
    BTCA_SIDECAR_RELATIVE_PATH,
    BTCA_DOCS_RELATIVE_PATH,
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
    "typescript-cli": "apps/typescript-cli/",
}

LIBRARY_TARGET_DIRS: dict[str, str] = {
    "python-lib": "packages/python/",
    "typescript-lib": "packages/typescript/",
}

APP_TARGET_PACKAGE_PATHS: dict[str, str] = {
    "web": "apps/web/package.json",
    "backend": "apps/backend/package.json",
    "desktop": "apps/desktop/package.json",
    "mobile": "apps/mobile/package.json",
    "tv": "apps/tv/package.json",
    "typescript-cli": "apps/typescript-cli/package.json",
}

APP_TARGET_PACKAGE_TEMPLATE_FILES: dict[str, str] = {
    "web": "workspace_packages/web_package.json",
    "backend": "workspace_packages/backend_package.json",
    "desktop": "workspace_packages/desktop_package.json",
    "mobile": "workspace_packages/mobile_package.json",
    "tv": "workspace_packages/tv_package.json",
    "typescript-cli": "workspace_packages/typescript_cli_package.json",
}

LIBRARY_TARGET_PACKAGE_PATHS: dict[str, str] = {
    "typescript-lib": "packages/typescript/package.json",
}

LIBRARY_TARGET_PACKAGE_TEMPLATE_FILES: dict[str, str] = {
    "typescript-lib": "workspace_packages/typescript_lib_package.json",
}

WEB_FRAMEWORK_PATHS: tuple[str, ...] = (
    "apps/web/vite.config.ts",
    "apps/web/tsconfig.json",
    "apps/web/components.json",
    "apps/web/src/",
    "apps/web/src/client.tsx",
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
    "apps/desktop/vite.main.config.ts",
    "apps/desktop/vite.preload.config.ts",
    "apps/desktop/vite.renderer.config.ts",
    "apps/desktop/index.html",
    "apps/desktop/src/",
    "apps/desktop/src/app.ts",
    "apps/desktop/src/main.ts",
    "apps/desktop/src/preload.ts",
    "apps/desktop/src/router.ts",
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

TYPESCRIPT_CLI_FRAMEWORK_PATHS: tuple[str, ...] = (
    "apps/typescript-cli/README.md",
    "apps/typescript-cli/tsconfig.json",
    "apps/typescript-cli/src/",
    "apps/typescript-cli/src/cli.ts",
    "apps/typescript-cli/src/index.ts",
    "apps/typescript-cli/smoke.test.ts",
)

SHARED_WORKSPACE_PATHS: tuple[str, ...] = (
    "packages/shared/",
    "packages/shared/package.json",
    "packages/shared/src/",
    "packages/shared/src/index.ts",
)

DESIGN_TOKENS_WORKSPACE_PATHS: tuple[str, ...] = (
    "packages/design-tokens/",
    "packages/design-tokens/package.json",
    "packages/design-tokens/src/",
    "packages/design-tokens/src/index.ts",
)

UI_WORKSPACE_PATHS: tuple[str, ...] = (
    "packages/ui/",
    "packages/ui/package.json",
    "packages/ui/src/",
    "packages/ui/src/index.ts",
    "packages/ui/src/components/",
    "packages/ui/src/components/button.tsx",
    "packages/ui/src/lib/",
    "packages/ui/src/lib/utils.ts",
    "packages/ui/src/styles/",
    "packages/ui/src/styles/globals.css",
)

PYTHON_PATHS: tuple[str, ...] = (
    "apps/python/",
    "apps/python/.python-version",
    "apps/python/.venv/",
    "apps/python/.venv/bin/",
    "apps/python/.venv/bin/activate",
    "apps/python/pyproject.toml",
    "apps/python/README.md",
    "apps/python/src/python_app/",
    "apps/python/src/python_app/__init__.py",
    "apps/python/src/python_app/core.py",
    "apps/python/src/python_app/cli.py",
    "apps/python/src/python_app/tui.py",
    "apps/python/src/python_app/entry_points.py",
    "apps/python/src/python_app/app.tcss",
    "apps/python/tests/",
    "apps/python/tests/test_smoke.py",
    "apps/python/tests/test_core.py",
)

PYTHON_LIBRARY_PATHS: tuple[str, ...] = (
    "packages/python/",
    "packages/python/.python-version",
    "packages/python/.venv/",
    "packages/python/.venv/bin/",
    "packages/python/.venv/bin/activate",
    "packages/python/pyproject.toml",
    "packages/python/README.md",
    "packages/python/src/",
    "packages/python/src/python_lib/",
    "packages/python/src/python_lib/__init__.py",
    "packages/python/src/python_lib/core.py",
    "packages/python/tests/",
    "packages/python/tests/test_core.py",
)

TYPESCRIPT_LIBRARY_PATHS: tuple[str, ...] = (
    "packages/typescript/",
    "packages/typescript/package.json",
    "packages/typescript/README.md",
    "packages/typescript/tsconfig.json",
    "packages/typescript/src/",
    "packages/typescript/src/index.ts",
    "packages/typescript/tests/",
    "packages/typescript/tests/typescript_lib.test.ts",
)

TARGET_ENV_EXAMPLE_PATHS: dict[str, str] = {
    "python": "apps/python/.env.example",
    "web": "apps/web/.env.example",
    "backend": "apps/backend/.env.example",
    "desktop": "apps/desktop/.env.example",
    "mobile": "apps/mobile/.env.example",
    "tv": "apps/tv/.env.example",
    "typescript-cli": "apps/typescript-cli/.env.example",
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
PYTHON_LANE_CORE = load_template_text("python_lane_core.txt")
PYTHON_LANE_CORE_WITH_LIBRARY = load_template_text("python_lane_core_with_library.txt")
PYTHON_LANE_CLI = load_template_text("python_lane_cli.txt")
PYTHON_LANE_TUI = load_template_text("python_lane_tui.txt")
PYTHON_LANE_ENTRY_POINTS = load_template_text("python_lane_entry_points.txt")
PYTHON_LANE_APP_CSS = load_template_text("python_lane_app.tcss")
PYTHON_LANE_TEST = load_template_text("python_lane_test.txt")
PYTHON_LANE_TEST_CORE = load_template_text("python_lane_test_core.txt")
ROOT_PYTHON_WORKSPACE_PYPROJECT = load_template_text(
    "root_python_workspace_pyproject.toml"
)
PYTHON_LIBRARY_PYPROJECT = load_template_text("python_lib/python_lib_pyproject.toml")
PYTHON_LIBRARY_README = load_template_text("python_lib/python_lib_readme.md")
PYTHON_LIBRARY_INIT = load_template_text("python_lib/python_lib_init.py")
PYTHON_LIBRARY_CORE = load_template_text("python_lib/python_lib_core.py")
PYTHON_LIBRARY_TEST = load_template_text("python_lib/python_lib_test_core.py")

TARGET_ENV_TEMPLATE_FILES: dict[str, str] = {
    "python": "env/python.env",
    "web": "env/web.env",
    "backend": "env/backend.env",
    "desktop": "env/desktop.env",
    "mobile": "env/mobile.env",
    "tv": "env/tv.env",
    "typescript-cli": "env/typescript-cli.env",
}

AUTH_PROVIDER_CHOICES: tuple[str, str, str] = ("clerk", "better-auth", "none")
SUPPORTED_AUTH_MATRIX: tuple[tuple[str | None, str | None], ...] = (
    (None, None),
    ("better-auth", "clerk"),
    ("better-auth", "better-auth"),
    ("clerk", "clerk"),
)

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
WEB_APP_AUTH_TEMPLATE = load_template_text("wiring/web_app_auth.ts")
WEB_AUTH_RUNTIME_TEMPLATE = load_template_text("wiring/web_auth_runtime.ts")
WEB_AUTH_PROVIDER_CLERK_TEMPLATE = load_template_text(
    "wiring/web_auth_provider_clerk.ts"
)
WEB_AUTH_CLIENT_BETTER_AUTH_TEMPLATE = load_template_text(
    "wiring/web_auth_client_better_auth.ts"
)
WEB_CLIENT_TEMPLATE = load_template_text("fullstack/web_client.tsx")
WEB_ROUTER_TEMPLATE = load_template_text("fullstack/web_router.tsx")
WEB_ROOT_ROUTE_TEMPLATE = load_template_text("fullstack/web_root_route.tsx")
WEB_INDEX_ROUTE_TEMPLATE = load_template_text("fullstack/web_index_route.tsx")
WEB_ROUTE_TREE_TEMPLATE = load_template_text("fullstack/web_route_tree.gen.ts")
WEB_VITE_CONFIG_TEMPLATE = load_template_text("fullstack/web_vite.config.ts")
WEB_TSCONFIG_TEMPLATE = load_template_text("fullstack/web_tsconfig.json")
WEB_COMPONENTS_JSON_TEMPLATE = load_template_text("fullstack/web_components.json")
WEB_STYLES_TEMPLATE = load_template_text("fullstack/web_styles.css")
BACKEND_HTTP_TEMPLATE = load_template_text("fullstack/backend_http.ts")
BACKEND_SCHEMA_TEMPLATE = load_template_text("fullstack/backend_schema.ts")
BACKEND_README_TEMPLATE = load_template_text("fullstack/backend_readme.md")
COMPOSE_TEMPLATE = load_template_text("fullstack/compose.yaml")
COMPOSE_OVERRIDE_TEMPLATE = load_template_text("fullstack/compose.override.yaml")
DESKTOP_APP_TEMPLATE = load_template_text("desktop/desktop_app.ts")
DESKTOP_MAIN_TEMPLATE = load_template_text("desktop/desktop_main.ts")
DESKTOP_PRELOAD_TEMPLATE = load_template_text("desktop/desktop_preload.ts")
DESKTOP_RENDERER_TEMPLATE = load_template_text("desktop/desktop_renderer.ts")
DESKTOP_RENDERER_WITH_SHARED_TEMPLATE = load_template_text(
    "desktop/desktop_renderer_with_shared.ts"
)
DESKTOP_ROUTER_TEMPLATE = load_template_text("desktop/desktop_router.ts")
DESKTOP_INDEX_HTML_TEMPLATE = load_template_text("desktop/desktop_index.html")
DESKTOP_TSCONFIG_TEMPLATE = load_template_text("desktop/desktop_tsconfig.json")
DESKTOP_FORGE_CONFIG_TEMPLATE = load_template_text("desktop/desktop_forge.config.ts")
DESKTOP_VITE_MAIN_CONFIG_TEMPLATE = load_template_text(
    "desktop/desktop_vite.main.config.ts"
)
DESKTOP_VITE_PRELOAD_CONFIG_TEMPLATE = load_template_text(
    "desktop/desktop_vite.preload.config.ts"
)
DESKTOP_VITE_RENDERER_CONFIG_TEMPLATE = load_template_text(
    "desktop/desktop_vite.renderer.config.ts"
)
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
TYPESCRIPT_CLI_TSCONFIG_TEMPLATE = load_template_text(
    "typescript_cli/typescript_cli_tsconfig.json"
)
TYPESCRIPT_CLI_README_TEMPLATE = load_template_text(
    "typescript_cli/typescript_cli_readme.md"
)
TYPESCRIPT_CLI_CLI_TEMPLATE = load_template_text("typescript_cli/typescript_cli_cli.ts")
TYPESCRIPT_CLI_INDEX_TEMPLATE = load_template_text(
    "typescript_cli/typescript_cli_index.ts"
)
TYPESCRIPT_CLI_SMOKE_TEST_TEMPLATE = load_template_text(
    "typescript_cli/typescript_cli_smoke.test.ts"
)
TYPESCRIPT_LIBRARY_TSCONFIG_TEMPLATE = load_template_text(
    "typescript_lib/typescript_lib_tsconfig.json"
)
TYPESCRIPT_LIBRARY_README_TEMPLATE = load_template_text(
    "typescript_lib/typescript_lib_readme.md"
)
TYPESCRIPT_LIBRARY_INDEX_TEMPLATE = load_template_text(
    "typescript_lib/typescript_lib_index.ts"
)
TYPESCRIPT_LIBRARY_TEST_TEMPLATE = load_template_text(
    "typescript_lib/typescript_lib_test.ts"
)
SHARED_PACKAGE_TEMPLATE = load_template_text("workspace_packages/shared_package.json")
DESIGN_TOKENS_PACKAGE_TEMPLATE = load_template_text(
    "workspace_packages/design_tokens_package.json"
)
UI_PACKAGE_TEMPLATE = load_template_text("workspace_packages/ui_package.json")
DESKTOP_PACKAGE_WITH_SHARED_TEMPLATE = load_template_text(
    "workspace_packages/desktop_package_with_shared.json"
)
DESIGN_TOKENS_INDEX_TEMPLATE = load_template_text(
    "design_tokens/design_tokens_index.ts"
)
SHARED_INDEX_TEMPLATE = load_template_text("shared/shared_index.ts")
UI_INDEX_TEMPLATE = load_template_text("ui/ui_index.ts")
UI_BUTTON_TEMPLATE = load_template_text("ui/ui_button.tsx")
UI_UTILS_TEMPLATE = load_template_text("ui/ui_utils.ts")
UI_GLOBALS_TEMPLATE = load_template_text("ui/ui_globals.css")
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
        action="append",
        choices=TARGET_CHOICES,
    )
    parser.add_argument("--project", action="append")
    parser.add_argument("--backend-auth", action="append")
    parser.add_argument("--backend-local-auth", action="append")
    parser.add_argument("--backend-prod-auth", action="append")
    parser.add_argument("--web-backend", action="append")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--auth", choices=AUTH_PROVIDER_CHOICES)
    parser.add_argument("--local-auth", choices=AUTH_PROVIDER_CHOICES)
    parser.add_argument("--prod-auth", choices=AUTH_PROVIDER_CHOICES)
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


def default_project_name(kind: str) -> str:
    return DEFAULT_PROJECT_NAMES[kind]


def project_relative_root(project: ProjectSpec) -> str:
    if project.kind == "python":
        return f"apps/python/{project.name}"
    if project.kind == "web":
        return f"apps/web/{project.name}"
    if project.kind == "backend":
        return f"apps/backend/{project.name}"
    if project.kind == "desktop":
        return f"apps/desktop/{project.name}"
    if project.kind == "mobile":
        return f"apps/mobile/{project.name}"
    if project.kind == "tv":
        return f"apps/tv/{project.name}"
    if project.kind == "typescript-cli":
        return f"apps/typescript-cli/{project.name}"
    if project.kind == "python-lib":
        return f"packages/python/{project.name}"
    if project.kind == "typescript-lib":
        return f"packages/typescript/{project.name}"
    raise ValueError(f"Unsupported project kind: {project.kind}")


def python_distribution_name(project: ProjectSpec) -> str:
    prefix = "python-app" if project.kind == "python" else "python-lib"
    default_name = default_project_name(project.kind)
    if project.name == default_name:
        return prefix
    return f"{prefix}-{project.name}"


def python_module_name(project: ProjectSpec) -> str:
    default_name = default_project_name(project.kind)
    if project.kind == "python":
        base = "python_app"
    else:
        base = "python_lib"
    if project.name == default_name:
        return base
    return f"{base}_{project.name.replace('-', '_')}"


def python_cli_script_name(project: ProjectSpec) -> str:
    default_name = default_project_name(project.kind)
    if project.name == default_name:
        return "python-app"
    return f"python-app-{project.name}"


def python_tui_script_name(project: ProjectSpec) -> str:
    base = python_cli_script_name(project)
    return f"{base}-tui"


def npm_package_name(project: ProjectSpec) -> str:
    default_name = default_project_name(project.kind)
    if project.name == default_name:
        return f"@generated/{project.kind}"
    return f"@generated/{project.kind}-{project.name}"


def typescript_cli_bin_name(project: ProjectSpec) -> str:
    default_name = default_project_name(project.kind)
    if project.name == default_name:
        return "typescript-cli"
    return f"typescript-cli-{project.name}"


def _parse_project_token(token: str) -> ProjectSpec:
    if ":" not in token:
        raise ValueError(
            "project must use the form <type>:<name>, for example web:dashboard"
        )
    raw_kind, raw_name = token.split(":", 1)
    kind = raw_kind.strip().lower()
    if kind not in TARGET_CHOICES or kind == "foundation":
        raise ValueError(f"unsupported project type: {raw_kind}")
    name = normalize_project_name(raw_name)
    return ProjectSpec(kind=kind, name=name)


def _parse_mapping_option(
    *, token: str, option_name: str, allowed_values: tuple[str, ...] | None = None
) -> tuple[str, str]:
    if ":" not in token:
        raise ValueError(
            f"{option_name} must use the form <name>:<value>, got {token!r}"
        )
    raw_name, raw_value = token.split(":", 1)
    name = normalize_project_name(raw_name)
    value = raw_value.strip().lower()
    if value == "":
        raise ValueError(f"{option_name} value cannot be empty")
    if allowed_values is not None and value not in allowed_values:
        raise ValueError(
            f"{option_name} value must be one of {', '.join(allowed_values)}"
        )
    return name, value


def _normalize_auth_choice(raw_value: str | None) -> str | None:
    if raw_value in {None, "none"}:
        return None
    return raw_value


def _auth_matrix_is_supported(*, local_auth: str | None, prod_auth: str | None) -> bool:
    return (local_auth, prod_auth) in SUPPORTED_AUTH_MATRIX


def _format_supported_auth_matrix() -> str:
    return ", ".join(
        f"{local or 'none'}/{prod or 'none'}" for local, prod in SUPPORTED_AUTH_MATRIX
    )


def _build_backend_auth_matrix(
    *,
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
    backend_names: set[str],
) -> dict[str, tuple[str | None, str | None]]:
    has_backend = bool(backend_names)
    if args.auth is not None and (
        args.local_auth is not None or args.prod_auth is not None
    ):
        parser.error("--auth cannot be combined with --local-auth or --prod-auth")
    if list(args.backend_auth or []) and (
        list(args.backend_local_auth or []) or list(args.backend_prod_auth or [])
    ):
        parser.error(
            "--backend-auth cannot be combined with --backend-local-auth or --backend-prod-auth"
        )

    if (
        args.auth is not None
        or args.local_auth is not None
        or args.prod_auth is not None
        or list(args.backend_auth or [])
        or list(args.backend_local_auth or [])
        or list(args.backend_prod_auth or [])
    ) and not has_backend:
        parser.error("auth option is only valid when backend target is selected")

    default_local_auth = _normalize_auth_choice(args.auth)
    default_prod_auth = _normalize_auth_choice(args.auth)
    if args.local_auth is not None or args.prod_auth is not None:
        default_local_auth = _normalize_auth_choice(args.local_auth)
        default_prod_auth = _normalize_auth_choice(args.prod_auth)

    legacy_backend_auth_map: dict[str, str | None] = {}
    for token in list(args.backend_auth or []):
        try:
            backend_name, backend_auth = _parse_mapping_option(
                token=token,
                option_name="--backend-auth",
                allowed_values=AUTH_PROVIDER_CHOICES,
            )
        except ValueError as exc:
            parser.error(str(exc))
        if backend_name not in backend_names:
            parser.error(
                f"--backend-auth references unknown backend project: {backend_name}"
            )
        legacy_backend_auth_map[backend_name] = _normalize_auth_choice(backend_auth)

    backend_local_auth_map: dict[str, str | None] = {}
    for token in list(args.backend_local_auth or []):
        try:
            backend_name, backend_auth = _parse_mapping_option(
                token=token,
                option_name="--backend-local-auth",
                allowed_values=AUTH_PROVIDER_CHOICES,
            )
        except ValueError as exc:
            parser.error(str(exc))
        if backend_name not in backend_names:
            parser.error(
                f"--backend-local-auth references unknown backend project: {backend_name}"
            )
        backend_local_auth_map[backend_name] = _normalize_auth_choice(backend_auth)

    backend_prod_auth_map: dict[str, str | None] = {}
    for token in list(args.backend_prod_auth or []):
        try:
            backend_name, backend_auth = _parse_mapping_option(
                token=token,
                option_name="--backend-prod-auth",
                allowed_values=AUTH_PROVIDER_CHOICES,
            )
        except ValueError as exc:
            parser.error(str(exc))
        if backend_name not in backend_names:
            parser.error(
                f"--backend-prod-auth references unknown backend project: {backend_name}"
            )
        backend_prod_auth_map[backend_name] = _normalize_auth_choice(backend_auth)

    resolved: dict[str, tuple[str | None, str | None]] = {}
    for backend_name in sorted(backend_names):
        local_auth = backend_local_auth_map.get(backend_name)
        prod_auth = backend_prod_auth_map.get(backend_name)
        legacy_auth = legacy_backend_auth_map.get(backend_name)

        if local_auth is None and backend_name not in backend_local_auth_map:
            if legacy_auth is not None or backend_name in legacy_backend_auth_map:
                local_auth = legacy_auth
            else:
                local_auth = default_local_auth
        if prod_auth is None and backend_name not in backend_prod_auth_map:
            if legacy_auth is not None or backend_name in legacy_backend_auth_map:
                prod_auth = legacy_auth
            else:
                prod_auth = default_prod_auth

        has_explicit_split = (
            backend_name in backend_local_auth_map
            or backend_name in backend_prod_auth_map
            or args.local_auth is not None
            or args.prod_auth is not None
        )
        if has_explicit_split and (
            (local_auth is None) != (prod_auth is None)
            or (
                backend_name not in backend_local_auth_map
                and backend_name not in backend_prod_auth_map
                and args.local_auth is not None
                and args.prod_auth is None
            )
            or (
                backend_name not in backend_local_auth_map
                and backend_name not in backend_prod_auth_map
                and args.local_auth is None
                and args.prod_auth is not None
            )
        ):
            parser.error(
                "both local and prod auth providers must be set when using split auth configuration"
            )

        if (
            local_auth is None
            and prod_auth is None
            and args.auth is None
            and args.local_auth is None
            and args.prod_auth is None
            and backend_name not in legacy_backend_auth_map
            and backend_name not in backend_local_auth_map
            and backend_name not in backend_prod_auth_map
        ):
            parser.error(
                "auth option is required when backend target is selected; use --auth or the local/prod auth options"
            )

        if not _auth_matrix_is_supported(local_auth=local_auth, prod_auth=prod_auth):
            parser.error(
                "unsupported backend auth combination "
                f"for '{backend_name}': {local_auth or 'none'}/{prod_auth or 'none'}; "
                f"supported combinations: {_format_supported_auth_matrix()}"
            )

        resolved[backend_name] = (local_auth, prod_auth)

    return resolved


def _rebase_paths(
    paths: tuple[str, ...], *, old_prefix: str, new_prefix: str
) -> tuple[str, ...]:
    rebased: list[str] = []
    for path in paths:
        if path == f"{old_prefix}/":
            rebased.append(f"{new_prefix}/")
            continue
        if path.startswith(f"{old_prefix}/"):
            suffix = path[len(old_prefix) + 1 :]
            rebased.append(f"{new_prefix}/{suffix}")
            continue
        rebased.append(path)
    return tuple(rebased)


def _project_paths(project: ProjectSpec) -> tuple[str, ...]:
    relative_root = project_relative_root(project)
    if project.kind == "python":
        return _rebase_paths(
            PYTHON_PATHS, old_prefix="apps/python", new_prefix=relative_root
        )
    if project.kind == "web":
        return (
            f"{relative_root}/package.json",
            *_rebase_paths(
                WEB_FRAMEWORK_PATHS, old_prefix="apps/web", new_prefix=relative_root
            ),
        )
    if project.kind == "backend":
        return (
            f"{relative_root}/package.json",
            *_rebase_paths(
                BACKEND_FRAMEWORK_PATHS,
                old_prefix="apps/backend",
                new_prefix=relative_root,
            ),
        )
    if project.kind == "desktop":
        return (
            f"{relative_root}/package.json",
            *_rebase_paths(
                DESKTOP_FRAMEWORK_PATHS,
                old_prefix="apps/desktop",
                new_prefix=relative_root,
            ),
        )
    if project.kind == "mobile":
        return (
            f"{relative_root}/package.json",
            *_rebase_paths(
                MOBILE_FRAMEWORK_PATHS,
                old_prefix="apps/mobile",
                new_prefix=relative_root,
            ),
        )
    if project.kind == "tv":
        return (
            f"{relative_root}/package.json",
            *_rebase_paths(
                TV_FRAMEWORK_PATHS, old_prefix="apps/tv", new_prefix=relative_root
            ),
        )
    if project.kind == "typescript-cli":
        return (
            f"{relative_root}/package.json",
            *_rebase_paths(
                TYPESCRIPT_CLI_FRAMEWORK_PATHS,
                old_prefix="apps/typescript-cli",
                new_prefix=relative_root,
            ),
        )
    if project.kind == "python-lib":
        return _rebase_paths(
            PYTHON_LIBRARY_PATHS,
            old_prefix="packages/python",
            new_prefix=relative_root,
        )
    if project.kind == "typescript-lib":
        return _rebase_paths(
            TYPESCRIPT_LIBRARY_PATHS,
            old_prefix="packages/typescript",
            new_prefix=relative_root,
        )
    raise ValueError(f"Unsupported project kind: {project.kind}")


def _dedupe_preserve_order(paths: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        ordered.append(path)
    return tuple(ordered)


def validate_args(
    parser: argparse.ArgumentParser, args: argparse.Namespace
) -> tuple[tuple[ProjectSpec, ...], tuple[str | None, str | None] | None]:
    raw_targets = list(args.target or [])
    raw_projects = list(args.project or [])

    if not raw_targets and not raw_projects:
        parser.error("at least one --target or --project selection is required")

    duplicate_targets: list[str] = []
    seen: set[str] = set()
    for target in raw_targets:
        if target in seen and target not in duplicate_targets:
            duplicate_targets.append(target)
        seen.add(target)
    if duplicate_targets:
        parser.error(
            "duplicate target selections are not allowed: "
            + ", ".join(duplicate_targets)
        )

    selected_targets = normalize_targets(raw_targets)

    if "foundation" in selected_targets and (len(selected_targets) > 1 or raw_projects):
        parser.error("foundation target cannot be combined with other targets")

    projects: list[ProjectSpec] = []
    for target in selected_targets:
        if target == "foundation":
            continue
        projects.append(ProjectSpec(kind=target, name=default_project_name(target)))

    for token in raw_projects:
        try:
            projects.append(_parse_project_token(token))
        except ValueError as exc:
            parser.error(str(exc))

    duplicate_projects: list[str] = []
    project_keys: set[tuple[str, str]] = set()
    for project in projects:
        key = (project.kind, project.name)
        if key in project_keys:
            duplicate_projects.append(f"{project.kind}:{project.name}")
            continue
        project_keys.add(key)
    if duplicate_projects:
        parser.error(
            "duplicate project selections are not allowed: "
            + ", ".join(duplicate_projects)
        )

    backend_names = {project.name for project in projects if project.kind == "backend"}
    backend_auth_matrix = _build_backend_auth_matrix(
        parser=parser, args=args, backend_names=backend_names
    )
    resolved_projects: list[ProjectSpec] = []
    for project in projects:
        if project.kind != "backend":
            resolved_projects.append(project)
            continue
        local_auth, prod_auth = backend_auth_matrix[project.name]
        resolved_projects.append(
            ProjectSpec(
                kind=project.kind,
                name=project.name,
                auth=prod_auth if local_auth == prod_auth else None,
                local_auth=local_auth,
                prod_auth=prod_auth,
            )
        )

    backend_projects = tuple(
        project for project in resolved_projects if project.kind == "backend"
    )
    web_projects = tuple(
        project for project in resolved_projects if project.kind == "web"
    )

    web_backend_map: dict[str, str] = {}
    for token in list(args.web_backend or []):
        try:
            web_name, backend_name = _parse_mapping_option(
                token=token,
                option_name="--web-backend",
            )
        except ValueError as exc:
            parser.error(str(exc))
        if web_name not in {project.name for project in web_projects}:
            parser.error(f"--web-backend references unknown web project: {web_name}")
        if backend_name not in {project.name for project in backend_projects}:
            parser.error(
                f"--web-backend references unknown backend project: {backend_name}"
            )
        web_backend_map[web_name] = backend_name

    if web_projects and len(backend_projects) > 1:
        missing_bindings = [
            project.name
            for project in web_projects
            if project.name not in web_backend_map
        ]
        if missing_bindings:
            parser.error(
                "web-backend binding is required when multiple backend projects exist: "
                + ", ".join(missing_bindings)
            )

    if web_projects and len(backend_projects) == 1:
        backend_name = backend_projects[0].name
        for project in web_projects:
            web_backend_map.setdefault(project.name, backend_name)

    final_projects: list[ProjectSpec] = []
    for project in resolved_projects:
        if project.kind == "web":
            final_projects.append(
                ProjectSpec(
                    kind=project.kind,
                    name=project.name,
                    backend_binding=web_backend_map.get(project.name),
                )
            )
            continue
        final_projects.append(project)

    default_auth_summary: tuple[str | None, str | None] | None = None
    if backend_projects:
        local_auth_values = {
            project.local_auth_provider for project in backend_projects
        }
        prod_auth_values = {project.prod_auth_provider for project in backend_projects}
        if len(local_auth_values) == 1 and len(prod_auth_values) == 1:
            default_auth_summary = (
                next(iter(local_auth_values)),
                next(iter(prod_auth_values)),
            )
    return tuple(final_projects), default_auth_summary


def resolve_paths(*, projects: tuple[ProjectSpec, ...]) -> tuple[str, ...]:
    paths: list[str] = list(FOUNDATION_PATHS)
    paths.extend(GENERATED_BTCA_PATHS)
    paths.extend(SHARED_INFRA_PACKAGE_PATHS)

    has_python_workspace = any(
        project.kind in {"python", "python-lib"} for project in projects
    )
    if has_python_workspace:
        paths.append("pyproject.toml")

    for project in projects:
        paths.extend(_project_paths(project))
        if project.kind in TARGET_ENV_EXAMPLE_PATHS:
            paths.append(f"{project_relative_root(project)}/.env.example")

    has_shared_workspace = any(
        project.kind in {"web", "backend", "desktop"} for project in projects
    )
    if has_shared_workspace:
        paths.extend(SHARED_WORKSPACE_PATHS)

    has_design_tokens_workspace = any(
        project.kind in {"web", "desktop"} for project in projects
    )
    if has_design_tokens_workspace:
        paths.extend(DESIGN_TOKENS_WORKSPACE_PATHS)

    has_ui_workspace = any(project.kind == "web" for project in projects)
    if has_ui_workspace:
        paths.extend(UI_WORKSPACE_PATHS)

    backend_by_name = {
        project.name: project for project in projects if project.kind == "backend"
    }
    for backend in backend_by_name.values():
        if backend.auth_matrix_enabled:
            paths.append(f"{project_relative_root(backend)}/convex/auth.config.ts")

    for web_project in (project for project in projects if project.kind == "web"):
        backend = backend_by_name.get(web_project.backend_binding or "")
        if backend is None or not backend.auth_matrix_enabled:
            continue
        web_src_root = f"{project_relative_root(web_project)}/src"
        paths.append(f"{web_src_root}/app-auth.ts")
        paths.append(f"{web_src_root}/auth-runtime.ts")
        if backend.uses_clerk_auth:
            paths.append(f"{web_src_root}/auth-provider.ts")
        if backend.uses_better_auth:
            paths.append(f"{web_src_root}/auth-client.ts")

    if backend_by_name and any(project.kind == "web" for project in projects):
        paths.append("compose.yaml")
        paths.append("compose.override.yaml")

    return _dedupe_preserve_order(paths)


def resolve_plan(*, projects: tuple[ProjectSpec, ...], output: Path) -> ScaffoldPlan:
    return ScaffoldPlan(
        projects=projects, output=output, paths=resolve_paths(projects=projects)
    )


def render_plan(plan: ScaffoldPlan) -> str:
    project_types = ", ".join(project.kind for project in plan.projects)
    backend_auth_values = {
        (
            f"{project.local_auth_provider or 'none'}/{project.prod_auth_provider or 'none'}"
        )
        for project in plan.projects
        if project.kind == "backend"
    }
    auth_summary = (
        "none"
        if not backend_auth_values
        else next(iter(backend_auth_values))
        if len(backend_auth_values) == 1
        else "mixed"
    )
    lines = [
        "Resolved scaffold plan:",
        f"- project types: {project_types if project_types != '' else 'foundation'}",
        f"- output: {plan.output}",
        f"- auth: {auth_summary}",
        "- projects:",
    ]
    if not plan.projects:
        lines.append("  - foundation")
    for project in plan.projects:
        details = [f"{project.kind}:{project.name}"]
        if project.kind == "backend":
            details.append(
                "local_auth="
                f"{project.local_auth_provider if project.local_auth_provider is not None else 'none'}"
            )
            details.append(
                "prod_auth="
                f"{project.prod_auth_provider if project.prod_auth_provider is not None else 'none'}"
            )
        if project.kind == "web" and project.backend_binding is not None:
            details.append(f"backend={project.backend_binding}")
        lines.append(f"  - {'; '.join(details)}")
    lines.extend(
        [
            "- root layout:",
        ]
    )
    lines.extend(f"  - {path}" for path in plan.paths)
    return "\n".join(lines)


def write_root_gitignore(*, output_root: Path) -> None:
    (output_root / ".gitignore").write_text(ROOT_GITIGNORE, encoding="utf-8")


def write_python_lane_python_version(*, lane_root: Path) -> None:
    (lane_root / ".python-version").write_text(
        PYTHON_LANE_PYTHON_VERSION,
        encoding="utf-8",
    )


def write_python_workspace_activate_shim(
    *, output_root: Path, member_root: Path
) -> None:
    activate_dir = member_root / ".venv" / "bin"
    activate_dir.mkdir(parents=True, exist_ok=True)
    activate_path = activate_dir / "activate"
    root_activate = output_root / ".venv" / "bin" / "activate"
    relative_target = Path(os.path.relpath(root_activate, activate_dir)).as_posix()

    if activate_path.exists() or activate_path.is_symlink():
        activate_path.unlink()

    try:
        activate_path.symlink_to(relative_target)
    except OSError:
        activate_script = "\n".join(
            (
                "# Auto-generated workspace activation shim.",
                f'_ROOT_ACTIVATE="{relative_target}"',
                'if [ ! -f "${_ROOT_ACTIVATE}" ]; then',
                '  printf "Workspace virtual environment not found at %s\\n" "${_ROOT_ACTIVATE}" >&2',
                "  return 1 2>/dev/null || exit 1",
                "fi",
                "# shellcheck source=/dev/null",
                '. "${_ROOT_ACTIVATE}"',
                "",
            )
        )
        activate_path.write_text(activate_script, encoding="utf-8")


def write_root_eslint_config(*, output_root: Path) -> None:
    (output_root / "eslint.config.mjs").write_text(
        ROOT_ESLINT_CONFIG,
        encoding="utf-8",
    )


def write_root_package_json(*, output_root: Path) -> None:
    (output_root / "package.json").write_text(ROOT_PACKAGE_JSON, encoding="utf-8")


def write_root_turbo_json(*, output_root: Path) -> None:
    (output_root / "turbo.json").write_text(ROOT_TURBO_JSON, encoding="utf-8")


def _python_workspace_members(*, projects: tuple[ProjectSpec, ...]) -> tuple[str, ...]:
    members: list[str] = []
    if any(project.kind == "python" for project in projects):
        members.append("apps/python/*")
    if any(project.kind == "python-lib" for project in projects):
        members.append("packages/python/*")
    return tuple(members)


def render_root_python_workspace_pyproject(
    *, projects: tuple[ProjectSpec, ...], workspace_project_name: str
) -> str:
    members = _python_workspace_members(projects=projects)
    member_lines = "\n".join(f'  "{member}",' for member in members)
    return ROOT_PYTHON_WORKSPACE_PYPROJECT.replace(
        "{{WORKSPACE_PROJECT_NAME}}", workspace_project_name
    ).replace("{{WORKSPACE_MEMBERS}}", member_lines)


def render_python_lane_pyproject(
    *, project: ProjectSpec, library_project: ProjectSpec | None
) -> str:
    project_name = python_distribution_name(project)
    module_name = python_module_name(project)
    cli_name = python_cli_script_name(project)
    tui_name = python_tui_script_name(project)
    rendered = PYTHON_LANE_PYPROJECT.replace(
        "{{PYTHON_LIB_DEPENDENCY}}",
        (
            f'  "{python_distribution_name(library_project)}>=0.1.0",'
            if library_project is not None
            else ""
        ),
    )
    source_block = ""
    if library_project is not None:
        source_block = (
            "[tool.uv.sources]\n"
            f"{python_distribution_name(library_project)} = {{ workspace = true }}\n"
        )
    rendered = rendered.replace("{{PYTHON_LIB_SOURCE_BLOCK}}", source_block)
    rendered = rendered.replace('name = "python-app"', f'name = "{project_name}"')
    rendered = rendered.replace(
        'python-app = "python_app.entry_points:run_cli"',
        f'{cli_name} = "{module_name}.entry_points:run_cli"',
    )
    rendered = rendered.replace(
        'python-app-tui = "python_app.entry_points:run_tui"',
        f'{tui_name} = "{module_name}.entry_points:run_tui"',
    )
    return rendered


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

    for executable_relative in ("scripts/synthetic-quotas.sh",):
        (output_root / executable_relative).chmod(0o755)


def write_generated_btca_assets(
    *, output_root: Path, projects: tuple[ProjectSpec, ...]
) -> None:
    generated_files = generate_scaffold_btca_files(
        project_contexts_from_projects(projects)
    )

    (output_root / BTCA_CONFIG_RELATIVE_PATH).write_text(
        generated_files.config_text,
        encoding="utf-8",
    )
    sidecar_path = output_root / BTCA_SIDECAR_RELATIVE_PATH
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    sidecar_path.write_text(
        generated_files.sidecar_text,
        encoding="utf-8",
    )
    docs_path = output_root / BTCA_DOCS_RELATIVE_PATH
    docs_path.parent.mkdir(parents=True, exist_ok=True)
    docs_path.write_text(generated_files.docs_text, encoding="utf-8")


def scaffold_foundation_core(
    *, output_root: Path, projects: tuple[ProjectSpec, ...]
) -> None:
    output_root.mkdir(parents=True, exist_ok=False)
    (output_root / "apps").mkdir()
    (output_root / "packages").mkdir()
    write_root_gitignore(output_root=output_root)
    write_root_eslint_config(output_root=output_root)
    write_root_package_json(output_root=output_root)
    write_root_turbo_json(output_root=output_root)
    write_foundation_governance_assets(output_root=output_root)
    write_generated_btca_assets(output_root=output_root, projects=projects)


def scaffold_python_workspace_root(
    *, output_root: Path, projects: tuple[ProjectSpec, ...]
) -> None:
    if not any(project.kind in {"python", "python-lib"} for project in projects):
        return

    (output_root / "pyproject.toml").write_text(
        render_root_python_workspace_pyproject(
            projects=projects,
            workspace_project_name=f"{normalize_project_name(output_root.name)}-workspace",
        ),
        encoding="utf-8",
    )


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


def _dump_json(data: dict[str, object]) -> str:
    return json.dumps(data, indent=2) + "\n"


def _render_package_manifest(template_text: str, *, package_name: str) -> str:
    data = json.loads(template_text)
    assert isinstance(data, dict)
    data["name"] = package_name
    return _dump_json(data)


def render_typescript_cli_package_manifest(project: ProjectSpec) -> str:
    data = json.loads(
        load_template_text("workspace_packages/typescript_cli_package.json")
    )
    assert isinstance(data, dict)
    data["name"] = npm_package_name(project)
    data["bin"] = {typescript_cli_bin_name(project): "./src/cli.ts"}
    return _dump_json(data)


def render_typescript_lib_package_manifest(project: ProjectSpec) -> str:
    data = json.loads(
        load_template_text("workspace_packages/typescript_lib_package.json")
    )
    assert isinstance(data, dict)
    data["name"] = npm_package_name(project)
    return _dump_json(data)


def render_workspace_package_manifest(
    project: ProjectSpec, *, template_text: str
) -> str:
    return _render_package_manifest(
        template_text, package_name=npm_package_name(project)
    )


def render_python_lane_readme(project: ProjectSpec) -> str:
    readme = PYTHON_LANE_README
    readme = readme.replace("python-app-tui", python_tui_script_name(project))
    readme = readme.replace("python-app", python_cli_script_name(project))
    readme = readme.replace(
        "apps/python/tests", f"{project_relative_root(project)}/tests"
    )
    readme = readme.replace("apps/python/src", f"{project_relative_root(project)}/src")
    readme = readme.replace("apps/python", project_relative_root(project))
    return readme


def render_python_lane_module_text(text: str, *, project: ProjectSpec) -> str:
    rendered = text.replace("python_app", python_module_name(project))
    rendered = rendered.replace("python-app-tui", python_tui_script_name(project))
    rendered = rendered.replace("python-app", python_cli_script_name(project))
    return rendered


def render_python_lane_core(
    *, project: ProjectSpec, library_project: ProjectSpec | None
) -> str:
    template = (
        PYTHON_LANE_CORE_WITH_LIBRARY
        if library_project is not None
        else PYTHON_LANE_CORE
    )
    rendered = render_python_lane_module_text(template, project=project)
    rendered = rendered.replace(
        "apps/python/tests", f"{project_relative_root(project)}/tests"
    )
    if library_project is not None:
        rendered = rendered.replace("python_lib", python_module_name(library_project))
        rendered = rendered.replace(
            "python-lib", python_distribution_name(library_project)
        )
    return rendered


def render_python_library_pyproject(project: ProjectSpec) -> str:
    rendered = PYTHON_LIBRARY_PYPROJECT.replace(
        'name = "python-lib"', f'name = "{python_distribution_name(project)}"'
    )
    return rendered.replace(
        'packages = ["src/python_lib"]',
        f'packages = ["src/{python_module_name(project)}"]',
    )


def render_python_library_readme(project: ProjectSpec) -> str:
    readme = PYTHON_LIBRARY_README.replace(
        "python-lib", python_distribution_name(project)
    )
    readme = readme.replace(
        "packages/python/tests", f"{project_relative_root(project)}/tests"
    )
    readme = readme.replace(
        "packages/python/src", f"{project_relative_root(project)}/src"
    )
    readme = readme.replace("packages/python", project_relative_root(project))
    return readme


def render_python_library_module_text(text: str, *, project: ProjectSpec) -> str:
    rendered = text.replace("python_lib", python_module_name(project))
    return rendered.replace("python-lib", python_distribution_name(project))


def render_typescript_cli_readme(project: ProjectSpec) -> str:
    return TYPESCRIPT_CLI_README_TEMPLATE.replace(
        "apps/typescript-cli", project_relative_root(project)
    )


def render_typescript_lib_readme(project: ProjectSpec) -> str:
    return TYPESCRIPT_LIBRARY_README_TEMPLATE.replace(
        "packages/typescript", project_relative_root(project)
    )


def _format_auth_provider(value: str | None) -> str:
    return value if value is not None else "none"


def render_backend_readme(project: ProjectSpec) -> str:
    readme = BACKEND_README_TEMPLATE
    readme = readme.replace(
        "{{LOCAL_AUTH_PROVIDER}}", _format_auth_provider(project.local_auth_provider)
    )
    readme = readme.replace(
        "{{PROD_AUTH_PROVIDER}}", _format_auth_provider(project.prod_auth_provider)
    )
    return readme.replace("apps/backend", project_relative_root(project))


def render_backend_auth_config(project: ProjectSpec) -> str:
    return BACKEND_AUTH_CONFIG_TEMPLATE.replace(
        "{{LOCAL_AUTH_PROVIDER}}", _format_auth_provider(project.local_auth_provider)
    ).replace(
        "{{PROD_AUTH_PROVIDER}}", _format_auth_provider(project.prod_auth_provider)
    )


def render_web_app_auth(project: ProjectSpec) -> str:
    return WEB_APP_AUTH_TEMPLATE.replace(
        "{{LOCAL_AUTH_PROVIDER}}", _format_auth_provider(project.local_auth_provider)
    ).replace(
        "{{PROD_AUTH_PROVIDER}}", _format_auth_provider(project.prod_auth_provider)
    )


def render_web_auth_runtime(project: ProjectSpec) -> str:
    return WEB_AUTH_RUNTIME_TEMPLATE.replace(
        "{{DEFAULT_RUNTIME}}",
        "local" if project.local_auth_provider is not None else "prod",
    )


def render_web_env_example(*, backend_project: ProjectSpec) -> str:
    lines = [
        "# Web app environment",
        "VITE_APP_ENV=development",
        "NURT_RUNTIME_ENV=local",
        f"AUTH_PROVIDER_LOCAL={_format_auth_provider(backend_project.local_auth_provider)}",
        f"AUTH_PROVIDER_PROD={_format_auth_provider(backend_project.prod_auth_provider)}",
        "VITE_CONVEX_URL=http://127.0.0.1:3210",
    ]
    if backend_project.uses_better_auth:
        lines.extend(
            [
                "VITE_CONVEX_SITE_URL=http://127.0.0.1:3211",
                "VITE_SITE_URL=http://localhost:3000",
            ]
        )
    if backend_project.uses_clerk_auth:
        lines.extend(
            [
                "VITE_CLERK_PUBLISHABLE_KEY_LOCAL=",
                "VITE_CLERK_PUBLISHABLE_KEY_PROD=",
            ]
        )
    return "\n".join(lines) + "\n"


def render_backend_env_example(project: ProjectSpec) -> str:
    lines = [
        "# Backend environment",
        "BACKEND_APP_ENV=development",
        "NURT_RUNTIME_ENV=local",
        f"AUTH_PROVIDER_LOCAL={_format_auth_provider(project.local_auth_provider)}",
        f"AUTH_PROVIDER_PROD={_format_auth_provider(project.prod_auth_provider)}",
        "CONVEX_SELF_HOSTED_URL=http://127.0.0.1:3210",
        "CONVEX_SELF_HOSTED_ADMIN_KEY=",
        "CONVEX_SELF_HOSTED_SITE_URL=http://127.0.0.1:3211",
        "CONVEX_DEPLOYMENT=",
    ]
    if project.uses_better_auth:
        lines.append("SITE_URL=http://localhost:3000")
    if project.uses_clerk_auth:
        lines.extend(
            [
                "CLERK_JWT_ISSUER_DOMAIN_LOCAL=",
                "CLERK_JWT_ISSUER_DOMAIN_PROD=",
            ]
        )
    return "\n".join(lines) + "\n"


def render_target_env_example(project: ProjectSpec) -> str:
    if project.kind == "backend":
        return render_backend_env_example(project)
    return load_template_text(TARGET_ENV_TEMPLATE_FILES[project.kind])


def render_compose_yaml(*, web_project: ProjectSpec) -> str:
    return COMPOSE_TEMPLATE.replace("{{WEB_ROOT}}", project_relative_root(web_project))


def render_compose_override_yaml(*, web_project: ProjectSpec) -> str:
    return COMPOSE_OVERRIDE_TEMPLATE.replace(
        "{{WEB_ROOT}}", project_relative_root(web_project)
    )


def scaffold_python_lane(
    *, output_root: Path, project: ProjectSpec, library_project: ProjectSpec | None
) -> None:
    if os.environ.get(SIMULATE_FAILURE_ENV) == "python-after-root":
        raise RuntimeError("simulated scaffold failure after root generation")

    lane_root = output_root / Path(project_relative_root(project))
    package_root = lane_root / "src" / python_module_name(project)
    tests_root = lane_root / "tests"
    package_root.mkdir(parents=True)
    tests_root.mkdir()
    write_python_lane_python_version(lane_root=lane_root)
    write_python_workspace_activate_shim(output_root=output_root, member_root=lane_root)
    (lane_root / "pyproject.toml").write_text(
        render_python_lane_pyproject(project=project, library_project=library_project),
        encoding="utf-8",
    )
    (lane_root / "README.md").write_text(
        render_python_lane_readme(project), encoding="utf-8"
    )
    (package_root / "__init__.py").write_text(PYTHON_LANE_INIT, encoding="utf-8")
    (package_root / "core.py").write_text(
        render_python_lane_core(project=project, library_project=library_project),
        encoding="utf-8",
    )
    (package_root / "cli.py").write_text(
        render_python_lane_module_text(PYTHON_LANE_CLI, project=project),
        encoding="utf-8",
    )
    (package_root / "tui.py").write_text(
        render_python_lane_module_text(PYTHON_LANE_TUI, project=project),
        encoding="utf-8",
    )
    (package_root / "entry_points.py").write_text(
        render_python_lane_module_text(PYTHON_LANE_ENTRY_POINTS, project=project),
        encoding="utf-8",
    )
    (package_root / "app.tcss").write_text(PYTHON_LANE_APP_CSS, encoding="utf-8")
    (tests_root / "test_smoke.py").write_text(
        render_python_lane_module_text(PYTHON_LANE_TEST, project=project),
        encoding="utf-8",
    )
    (tests_root / "test_core.py").write_text(
        render_python_lane_module_text(PYTHON_LANE_TEST_CORE, project=project),
        encoding="utf-8",
    )
    (lane_root / ".env.example").write_text(
        render_target_env_example(project), encoding="utf-8"
    )


def scaffold_typescript_cli_project(*, output_root: Path, project: ProjectSpec) -> None:
    cli_root = output_root / Path(project_relative_root(project))
    cli_src = cli_root / "src"
    cli_root.mkdir(parents=True, exist_ok=True)
    cli_src.mkdir(parents=True, exist_ok=True)

    (cli_root / "package.json").write_text(
        render_typescript_cli_package_manifest(project),
        encoding="utf-8",
    )
    (cli_root / "README.md").write_text(
        render_typescript_cli_readme(project), encoding="utf-8"
    )
    (cli_root / "tsconfig.json").write_text(
        TYPESCRIPT_CLI_TSCONFIG_TEMPLATE, encoding="utf-8"
    )
    (cli_src / "cli.ts").write_text(TYPESCRIPT_CLI_CLI_TEMPLATE, encoding="utf-8")
    (cli_src / "index.ts").write_text(TYPESCRIPT_CLI_INDEX_TEMPLATE, encoding="utf-8")
    (cli_root / "smoke.test.ts").write_text(
        TYPESCRIPT_CLI_SMOKE_TEST_TEMPLATE,
        encoding="utf-8",
    )
    (cli_root / ".env.example").write_text(
        render_target_env_example(project), encoding="utf-8"
    )


def scaffold_python_library(*, output_root: Path, project: ProjectSpec) -> None:
    library_root = output_root / Path(project_relative_root(project))
    package_root = library_root / "src" / python_module_name(project)
    tests_root = library_root / "tests"
    package_root.mkdir(parents=True, exist_ok=True)
    tests_root.mkdir(parents=True, exist_ok=True)
    write_python_lane_python_version(lane_root=library_root)
    write_python_workspace_activate_shim(
        output_root=output_root,
        member_root=library_root,
    )

    (library_root / "pyproject.toml").write_text(
        render_python_library_pyproject(project),
        encoding="utf-8",
    )
    (library_root / "README.md").write_text(
        render_python_library_readme(project), encoding="utf-8"
    )
    (package_root / "__init__.py").write_text(
        render_python_library_module_text(PYTHON_LIBRARY_INIT, project=project),
        encoding="utf-8",
    )
    (package_root / "core.py").write_text(
        render_python_library_module_text(PYTHON_LIBRARY_CORE, project=project),
        encoding="utf-8",
    )
    (tests_root / "test_core.py").write_text(
        render_python_library_module_text(PYTHON_LIBRARY_TEST, project=project),
        encoding="utf-8",
    )


def scaffold_typescript_library(*, output_root: Path, project: ProjectSpec) -> None:
    library_root = output_root / Path(project_relative_root(project))
    src_root = library_root / "src"
    tests_root = library_root / "tests"
    library_root.mkdir(parents=True, exist_ok=True)
    src_root.mkdir(parents=True, exist_ok=True)
    tests_root.mkdir(parents=True, exist_ok=True)

    (library_root / "package.json").write_text(
        render_typescript_lib_package_manifest(project),
        encoding="utf-8",
    )
    (library_root / "tsconfig.json").write_text(
        TYPESCRIPT_LIBRARY_TSCONFIG_TEMPLATE, encoding="utf-8"
    )
    (library_root / "README.md").write_text(
        render_typescript_lib_readme(project), encoding="utf-8"
    )
    (src_root / "index.ts").write_text(
        TYPESCRIPT_LIBRARY_INDEX_TEMPLATE, encoding="utf-8"
    )
    (tests_root / "typescript_lib.test.ts").write_text(
        TYPESCRIPT_LIBRARY_TEST_TEMPLATE,
        encoding="utf-8",
    )


def scaffold_web_project(*, output_root: Path, project: ProjectSpec) -> None:
    web_root = output_root / Path(project_relative_root(project))
    web_src = web_root / "src"
    routes_dir = web_src / "routes"
    routes_dir.mkdir(parents=True, exist_ok=True)

    (web_root / "package.json").write_text(
        render_workspace_package_manifest(
            project,
            template_text=load_template_text("workspace_packages/web_package.json"),
        ),
        encoding="utf-8",
    )
    (web_root / "vite.config.ts").write_text(WEB_VITE_CONFIG_TEMPLATE, encoding="utf-8")
    (web_root / "tsconfig.json").write_text(WEB_TSCONFIG_TEMPLATE, encoding="utf-8")
    (web_root / "components.json").write_text(
        WEB_COMPONENTS_JSON_TEMPLATE, encoding="utf-8"
    )
    (web_src / "client.tsx").write_text(WEB_CLIENT_TEMPLATE, encoding="utf-8")
    (web_src / "router.tsx").write_text(WEB_ROUTER_TEMPLATE, encoding="utf-8")
    (web_src / "routeTree.gen.ts").write_text(WEB_ROUTE_TREE_TEMPLATE, encoding="utf-8")
    (web_src / "styles.css").write_text(WEB_STYLES_TEMPLATE, encoding="utf-8")
    (routes_dir / "__root.tsx").write_text(WEB_ROOT_ROUTE_TEMPLATE, encoding="utf-8")
    (routes_dir / "index.tsx").write_text(WEB_INDEX_ROUTE_TEMPLATE, encoding="utf-8")
    (web_root / ".env.example").write_text(
        render_target_env_example(project), encoding="utf-8"
    )


def scaffold_backend_project(*, output_root: Path, project: ProjectSpec) -> None:
    backend_root = output_root / Path(project_relative_root(project))
    convex_dir = backend_root / "convex"
    convex_dir.mkdir(parents=True, exist_ok=True)

    (backend_root / "package.json").write_text(
        render_workspace_package_manifest(
            project,
            template_text=load_template_text("workspace_packages/backend_package.json"),
        ),
        encoding="utf-8",
    )
    (convex_dir / "http.ts").write_text(BACKEND_HTTP_TEMPLATE, encoding="utf-8")
    (convex_dir / "schema.ts").write_text(BACKEND_SCHEMA_TEMPLATE, encoding="utf-8")
    (backend_root / "tsconfig.json").write_text(
        BACKEND_TSCONFIG_TEMPLATE, encoding="utf-8"
    )
    (backend_root / "README.md").write_text(
        render_backend_readme(project), encoding="utf-8"
    )
    (backend_root / ".env.example").write_text(
        render_target_env_example(project), encoding="utf-8"
    )
    if project.auth_matrix_enabled:
        (convex_dir / "auth.config.ts").write_text(
            render_backend_auth_config(project),
            encoding="utf-8",
        )


def scaffold_desktop_project(
    *, output_root: Path, project: ProjectSpec, has_web: bool
) -> None:
    desktop_root = output_root / Path(project_relative_root(project))
    desktop_src = desktop_root / "src"
    desktop_src.mkdir(parents=True, exist_ok=True)

    template_text = (
        DESKTOP_PACKAGE_WITH_SHARED_TEMPLATE
        if has_web
        else load_template_text("workspace_packages/desktop_package.json")
    )
    (desktop_root / "package.json").write_text(
        render_workspace_package_manifest(project, template_text=template_text),
        encoding="utf-8",
    )
    (desktop_root / "README.md").write_text(DESKTOP_README_TEMPLATE, encoding="utf-8")
    (desktop_root / "forge.config.ts").write_text(
        DESKTOP_FORGE_CONFIG_TEMPLATE, encoding="utf-8"
    )
    (desktop_root / "tsconfig.json").write_text(
        DESKTOP_TSCONFIG_TEMPLATE, encoding="utf-8"
    )
    (desktop_root / "vite.main.config.ts").write_text(
        DESKTOP_VITE_MAIN_CONFIG_TEMPLATE,
        encoding="utf-8",
    )
    (desktop_root / "vite.preload.config.ts").write_text(
        DESKTOP_VITE_PRELOAD_CONFIG_TEMPLATE,
        encoding="utf-8",
    )
    (desktop_root / "vite.renderer.config.ts").write_text(
        DESKTOP_VITE_RENDERER_CONFIG_TEMPLATE,
        encoding="utf-8",
    )
    (desktop_root / "index.html").write_text(
        DESKTOP_INDEX_HTML_TEMPLATE, encoding="utf-8"
    )
    (desktop_src / "app.ts").write_text(DESKTOP_APP_TEMPLATE, encoding="utf-8")
    (desktop_src / "main.ts").write_text(DESKTOP_MAIN_TEMPLATE, encoding="utf-8")
    (desktop_src / "preload.ts").write_text(DESKTOP_PRELOAD_TEMPLATE, encoding="utf-8")
    (desktop_src / "router.ts").write_text(DESKTOP_ROUTER_TEMPLATE, encoding="utf-8")
    (desktop_src / "renderer.ts").write_text(
        DESKTOP_RENDERER_WITH_SHARED_TEMPLATE if has_web else DESKTOP_RENDERER_TEMPLATE,
        encoding="utf-8",
    )
    (desktop_root / ".env.example").write_text(
        render_target_env_example(project), encoding="utf-8"
    )


def scaffold_shared_workspace_package(
    *, output_root: Path, projects: tuple[ProjectSpec, ...]
) -> None:
    if not any(project.kind in {"web", "backend", "desktop"} for project in projects):
        return
    shared_src_dir = output_root / "packages" / "shared" / "src"
    shared_src_dir.mkdir(parents=True, exist_ok=True)
    (output_root / "packages" / "shared" / "package.json").write_text(
        SHARED_PACKAGE_TEMPLATE,
        encoding="utf-8",
    )
    (shared_src_dir / "index.ts").write_text(SHARED_INDEX_TEMPLATE, encoding="utf-8")


def scaffold_design_tokens_workspace_package(
    *, output_root: Path, projects: tuple[ProjectSpec, ...]
) -> None:
    if not any(project.kind in {"web", "desktop"} for project in projects):
        return
    tokens_src_dir = output_root / "packages" / "design-tokens" / "src"
    tokens_src_dir.mkdir(parents=True, exist_ok=True)
    (output_root / "packages" / "design-tokens" / "package.json").write_text(
        DESIGN_TOKENS_PACKAGE_TEMPLATE,
        encoding="utf-8",
    )
    (tokens_src_dir / "index.ts").write_text(
        DESIGN_TOKENS_INDEX_TEMPLATE,
        encoding="utf-8",
    )


def scaffold_ui_workspace_package(
    *, output_root: Path, projects: tuple[ProjectSpec, ...]
) -> None:
    if not any(project.kind == "web" for project in projects):
        return
    ui_root = output_root / "packages" / "ui"
    ui_components_dir = ui_root / "src" / "components"
    ui_lib_dir = ui_root / "src" / "lib"
    ui_styles_dir = ui_root / "src" / "styles"
    ui_components_dir.mkdir(parents=True, exist_ok=True)
    ui_lib_dir.mkdir(parents=True, exist_ok=True)
    ui_styles_dir.mkdir(parents=True, exist_ok=True)
    (ui_root / "package.json").write_text(UI_PACKAGE_TEMPLATE, encoding="utf-8")
    (ui_root / "src" / "index.ts").write_text(UI_INDEX_TEMPLATE, encoding="utf-8")
    (ui_components_dir / "button.tsx").write_text(UI_BUTTON_TEMPLATE, encoding="utf-8")
    (ui_lib_dir / "utils.ts").write_text(UI_UTILS_TEMPLATE, encoding="utf-8")
    (ui_styles_dir / "globals.css").write_text(UI_GLOBALS_TEMPLATE, encoding="utf-8")


def scaffold_mobile_project(*, output_root: Path, project: ProjectSpec) -> None:
    mobile_root = output_root / Path(project_relative_root(project))
    mobile_root.mkdir(parents=True, exist_ok=True)
    (mobile_root / "package.json").write_text(
        render_workspace_package_manifest(
            project,
            template_text=load_template_text("workspace_packages/mobile_package.json"),
        ),
        encoding="utf-8",
    )
    (mobile_root / "README.md").write_text(MOBILE_README_TEMPLATE, encoding="utf-8")
    (mobile_root / "app.json").write_text(MOBILE_APP_JSON_TEMPLATE, encoding="utf-8")
    (mobile_root / "eas.json").write_text(MOBILE_EAS_JSON_TEMPLATE, encoding="utf-8")
    (mobile_root / "babel.config.js").write_text(
        MOBILE_BABEL_CONFIG_TEMPLATE, encoding="utf-8"
    )
    (mobile_root / "index.js").write_text(MOBILE_INDEX_TEMPLATE, encoding="utf-8")
    (mobile_root / "App.tsx").write_text(MOBILE_APP_TEMPLATE, encoding="utf-8")
    (mobile_root / "smoke.test.js").write_text(
        MOBILE_SMOKE_TEST_TEMPLATE, encoding="utf-8"
    )
    (mobile_root / "tsconfig.json").write_text(
        MOBILE_TSCONFIG_TEMPLATE, encoding="utf-8"
    )
    (mobile_root / ".env.example").write_text(
        render_target_env_example(project), encoding="utf-8"
    )


def scaffold_tv_project(*, output_root: Path, project: ProjectSpec) -> None:
    tv_root = output_root / Path(project_relative_root(project))
    tv_scripts_dir = tv_root / "scripts"
    tv_root.mkdir(parents=True, exist_ok=True)
    tv_scripts_dir.mkdir(parents=True, exist_ok=True)
    (tv_root / "package.json").write_text(
        render_workspace_package_manifest(
            project,
            template_text=load_template_text("workspace_packages/tv_package.json"),
        ),
        encoding="utf-8",
    )
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
        TV_INPUT_CHECKLIST_TEMPLATE, encoding="utf-8"
    )
    (tv_root / "TV_VALIDATION_LOG.md").write_text(
        TV_VALIDATION_LOG_TEMPLATE, encoding="utf-8"
    )
    (tv_root / ".env.example").write_text(
        render_target_env_example(project), encoding="utf-8"
    )


def scaffold_web_backend_env_examples(
    *, output_root: Path, projects: tuple[ProjectSpec, ...]
) -> None:
    backend_by_name = {
        project.name: project for project in projects if project.kind == "backend"
    }
    for web_project in (project for project in projects if project.kind == "web"):
        backend = backend_by_name.get(web_project.backend_binding or "")
        if backend is None or not backend.auth_matrix_enabled:
            continue
        (
            output_root / Path(project_relative_root(web_project)) / ".env.example"
        ).write_text(
            render_web_env_example(backend_project=backend),
            encoding="utf-8",
        )
        (
            output_root / Path(project_relative_root(backend)) / ".env.example"
        ).write_text(
            render_backend_env_example(backend),
            encoding="utf-8",
        )


def scaffold_web_backend_auth_wiring(
    *, output_root: Path, projects: tuple[ProjectSpec, ...]
) -> None:
    backend_by_name = {
        project.name: project for project in projects if project.kind == "backend"
    }
    for web_project in (project for project in projects if project.kind == "web"):
        backend = backend_by_name.get(web_project.backend_binding or "")
        if backend is None or not backend.auth_matrix_enabled:
            continue
        web_src_dir = output_root / Path(project_relative_root(web_project)) / "src"
        web_src_dir.mkdir(parents=True, exist_ok=True)
        (web_src_dir / "app-auth.ts").write_text(
            render_web_app_auth(backend), encoding="utf-8"
        )
        (web_src_dir / "auth-runtime.ts").write_text(
            render_web_auth_runtime(backend), encoding="utf-8"
        )
        if backend.uses_clerk_auth:
            (web_src_dir / "auth-provider.ts").write_text(
                WEB_AUTH_PROVIDER_CLERK_TEMPLATE,
                encoding="utf-8",
            )
        if backend.uses_better_auth:
            (web_src_dir / "auth-client.ts").write_text(
                WEB_AUTH_CLIENT_BETTER_AUTH_TEMPLATE,
                encoding="utf-8",
            )


def scaffold_fullstack_compose_assets(
    *, output_root: Path, projects: tuple[ProjectSpec, ...]
) -> None:
    web_projects = tuple(project for project in projects if project.kind == "web")
    backend_projects = tuple(
        project for project in projects if project.kind == "backend"
    )
    if not web_projects or not backend_projects:
        return
    primary_web = web_projects[0]
    (output_root / "compose.yaml").write_text(
        render_compose_yaml(web_project=primary_web), encoding="utf-8"
    )
    (output_root / "compose.override.yaml").write_text(
        render_compose_override_yaml(web_project=primary_web), encoding="utf-8"
    )


def execute_scaffold_direct(plan: ScaffoldPlan) -> None:
    scaffold_foundation_core(output_root=plan.output, projects=plan.projects)
    scaffold_shared_infra_packages(output_root=plan.output)
    scaffold_python_workspace_root(output_root=plan.output, projects=plan.projects)
    scaffold_shared_workspace_package(output_root=plan.output, projects=plan.projects)
    scaffold_design_tokens_workspace_package(
        output_root=plan.output, projects=plan.projects
    )
    scaffold_ui_workspace_package(output_root=plan.output, projects=plan.projects)

    has_web = any(project.kind == "web" for project in plan.projects)
    python_libraries = [
        project for project in plan.projects if project.kind == "python-lib"
    ]
    shared_python_library = python_libraries[0] if len(python_libraries) == 1 else None

    for project in plan.projects:
        if project.kind == "python":
            scaffold_python_lane(
                output_root=plan.output,
                project=project,
                library_project=shared_python_library,
            )
        elif project.kind == "python-lib":
            scaffold_python_library(output_root=plan.output, project=project)
        elif project.kind == "typescript-cli":
            scaffold_typescript_cli_project(output_root=plan.output, project=project)
        elif project.kind == "typescript-lib":
            scaffold_typescript_library(output_root=plan.output, project=project)
        elif project.kind == "web":
            scaffold_web_project(output_root=plan.output, project=project)
        elif project.kind == "backend":
            scaffold_backend_project(output_root=plan.output, project=project)
        elif project.kind == "desktop":
            scaffold_desktop_project(
                output_root=plan.output,
                project=project,
                has_web=has_web,
            )
        elif project.kind == "mobile":
            scaffold_mobile_project(output_root=plan.output, project=project)
        elif project.kind == "tv":
            scaffold_tv_project(output_root=plan.output, project=project)

    scaffold_web_backend_env_examples(output_root=plan.output, projects=plan.projects)
    scaffold_web_backend_auth_wiring(output_root=plan.output, projects=plan.projects)
    scaffold_fullstack_compose_assets(output_root=plan.output, projects=plan.projects)


def execute_scaffold(plan: ScaffoldPlan) -> None:
    if plan.output.exists():
        raise FileExistsError(f"Output path already exists: {plan.output}")

    plan.output.parent.mkdir(parents=True, exist_ok=True)
    stage_container = Path(
        tempfile.mkdtemp(prefix=f".{plan.output.name}.staging-", dir=plan.output.parent)
    )
    stage_output = stage_container / plan.output.name
    staged_plan = ScaffoldPlan(
        projects=plan.projects,
        output=stage_output,
        paths=plan.paths,
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
    selected_projects, _resolved_auth = validate_args(parser, args)

    if not args.no_interactive:
        parser.error("interactive mode is not implemented yet; use --no-interactive")

    plan = resolve_plan(projects=selected_projects, output=args.output)

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
