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
    include_python_workspace: bool
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

FOUNDATION_PATHS: tuple[str, ...] = (
    "apps/",
    "packages/",
    "pyproject.toml",
    ".gitignore",
    "package.json",
    "turbo.json",
)

APP_TARGET_DIRS: dict[str, str] = {
    "web": "apps/web/",
    "backend": "apps/backend/",
    "desktop": "apps/desktop/",
    "mobile": "apps/mobile/",
    "tv": "apps/tv/",
}

PYTHON_PATHS: tuple[str, ...] = (
    "apps/python/",
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

ROOT_PYPROJECT_BASE = load_template_text("root_pyproject_base.toml")

PYTHON_WORKSPACE_SECTION = load_template_text("python_workspace_section.toml")

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
ROOT_GITIGNORE = load_template_text("root_gitignore.txt")
ROOT_PACKAGE_JSON = load_template_text("root_package.json")
ROOT_TURBO_JSON = load_template_text("root_turbo.json")

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
    parser.add_argument("--auth", choices=("clerk", "better-auth"))
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
) -> tuple[str, ...]:
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

    has_web_backend = "web" in selected_targets and "backend" in selected_targets
    if has_web_backend and args.auth is None:
        parser.error(
            "auth option is required when both web and backend targets are selected"
        )

    if args.auth is not None and not has_web_backend:
        parser.error(
            "auth option is only valid when both web and backend targets are selected"
        )

    return selected_targets


def resolve_paths(*, targets: tuple[str, ...], auth: str | None) -> tuple[str, ...]:
    paths: list[str] = list(FOUNDATION_PATHS)

    for target in targets:
        if target in APP_TARGET_DIRS:
            paths.append(APP_TARGET_DIRS[target])
        if target == "python":
            paths.extend(PYTHON_PATHS)
        if target in TARGET_ENV_EXAMPLE_PATHS:
            paths.append(TARGET_ENV_EXAMPLE_PATHS[target])

    has_web_backend = "web" in targets and "backend" in targets
    if has_web_backend and auth is not None:
        if auth == "clerk":
            paths.extend(CLERK_WIRING_PATHS)
        if auth == "better-auth":
            paths.extend(BETTER_AUTH_WIRING_PATHS)

    return tuple(paths)


def resolve_plan(
    *, targets: tuple[str, ...], output: Path, auth: str | None
) -> ScaffoldPlan:
    return ScaffoldPlan(
        targets=targets,
        output=output,
        paths=resolve_paths(targets=targets, auth=auth),
        include_python_workspace="python" in targets,
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


def write_root_pyproject(*, output_root: Path, include_python_workspace: bool) -> None:
    root_content = ROOT_PYPROJECT_BASE
    if include_python_workspace:
        root_content += PYTHON_WORKSPACE_SECTION
    (output_root / "pyproject.toml").write_text(root_content, encoding="utf-8")


def write_root_gitignore(*, output_root: Path) -> None:
    (output_root / ".gitignore").write_text(ROOT_GITIGNORE, encoding="utf-8")


def write_root_package_json(*, output_root: Path) -> None:
    (output_root / "package.json").write_text(ROOT_PACKAGE_JSON, encoding="utf-8")


def write_root_turbo_json(*, output_root: Path) -> None:
    (output_root / "turbo.json").write_text(ROOT_TURBO_JSON, encoding="utf-8")


def scaffold_foundation_core(
    *, output_root: Path, include_python_workspace: bool
) -> None:
    output_root.mkdir(parents=True, exist_ok=False)
    (output_root / "apps").mkdir()
    (output_root / "packages").mkdir()
    write_root_pyproject(
        output_root=output_root,
        include_python_workspace=include_python_workspace,
    )
    write_root_gitignore(output_root=output_root)
    write_root_package_json(output_root=output_root)
    write_root_turbo_json(output_root=output_root)


def scaffold_python_lane(*, output_root: Path) -> None:
    if os.environ.get(SIMULATE_FAILURE_ENV) == "python-after-root":
        raise RuntimeError("simulated scaffold failure after root generation")

    lane_root = output_root / "apps" / "python"
    (lane_root / "src" / "python_app").mkdir(parents=True)
    (lane_root / "tests").mkdir()
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
    has_web_backend = "web" in targets and "backend" in targets
    if not has_web_backend or auth is None:
        return

    backend_convex_dir = output_root / "apps" / "backend" / "convex"
    backend_convex_dir.mkdir(parents=True, exist_ok=True)

    web_src_dir = output_root / "apps" / "web" / "src"
    web_src_dir.mkdir(parents=True, exist_ok=True)

    backend_auth_config = BACKEND_AUTH_CONFIG_TEMPLATE.replace(
        "{{AUTH_PROVIDER}}", auth
    )
    (backend_convex_dir / "auth.config.ts").write_text(
        backend_auth_config,
        encoding="utf-8",
    )

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
    scaffold_foundation_core(
        output_root=plan.output,
        include_python_workspace=plan.include_python_workspace,
    )
    scaffold_app_targets(output_root=plan.output, targets=plan.targets)

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
        include_python_workspace=plan.include_python_workspace,
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
    selected_targets = validate_args(parser, args)

    if not args.no_interactive:
        parser.error("interactive mode is not implemented yet; use --no-interactive")

    plan = resolve_plan(targets=selected_targets, output=args.output, auth=args.auth)

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
