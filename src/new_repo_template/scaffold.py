from __future__ import annotations

import argparse
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


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

FOUNDATION_PATHS: tuple[str, ...] = ("apps/", "packages/", "pyproject.toml")

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

WEB_BACKEND_ENV_PATHS: tuple[str, ...] = (
    "apps/web/.env.example",
    "apps/backend/.env.example",
)

ROOT_PYPROJECT_BASE = (
    "[build-system]\n"
    'requires = ["hatchling>=1.26.3"]\n'
    'build-backend = "hatchling.build"\n'
)

PYTHON_WORKSPACE_SECTION = '\n[tool.uv.workspace]\nmembers = ["apps/python"]\n'

PYTHON_LANE_PYPROJECT = (
    "[build-system]\n"
    'requires = ["hatchling>=1.26.3"]\n'
    'build-backend = "hatchling.build"\n'
    "\n"
    "[project]\n"
    'name = "python-app"\n'
    'version = "0.1.0"\n'
    'description = "Python lane application"\n'
    'requires-python = ">=3.14"\n'
    "dependencies = []\n"
    "\n"
    "[project.optional-dependencies]\n"
    "dev = [\n"
    '  "pytest>=9.0.2",\n'
    '  "ruff>=0.14.14",\n'
    '  "mypy>=1.19.1",\n'
    "]\n"
    "\n"
    "[tool.pytest.ini_options]\n"
    'testpaths = ["tests"]\n'
)

PYTHON_LANE_README = (
    "# Python Lane\n\n"
    "Baseline developer commands:\n\n"
    "- `uv sync --group dev`\n"
    "- `uv run pytest`\n"
    "- `uv run ruff check .`\n"
    "- `uv run mypy src`\n"
)

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

    has_web_backend = "web" in targets and "backend" in targets
    if has_web_backend and auth is not None:
        paths.extend(WEB_BACKEND_ENV_PATHS)

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


def scaffold_python_lane(*, output_root: Path) -> None:
    if os.environ.get(SIMULATE_FAILURE_ENV) == "python-after-root":
        raise RuntimeError("simulated scaffold failure after root generation")

    lane_root = output_root / "apps" / "python"
    (lane_root / "src" / "python_app").mkdir(parents=True)
    (lane_root / "tests").mkdir()
    (lane_root / "pyproject.toml").write_text(PYTHON_LANE_PYPROJECT, encoding="utf-8")
    (lane_root / "README.md").write_text(PYTHON_LANE_README, encoding="utf-8")
    (lane_root / "src" / "python_app" / "__init__.py").write_text(
        '"""Python lane package."""\n', encoding="utf-8"
    )
    (lane_root / "tests" / "test_smoke.py").write_text(
        "from python_app import __doc__\n\n"
        "\n"
        "def test_python_lane_import_smoke() -> None:\n"
        "    assert __doc__ is not None\n",
        encoding="utf-8",
    )


def scaffold_app_targets(*, output_root: Path, targets: tuple[str, ...]) -> None:
    for target in targets:
        if target in APP_TARGET_DIRS:
            (output_root / APP_TARGET_DIRS[target]).mkdir(parents=True, exist_ok=True)


def scaffold_web_backend_env_examples(
    *, output_root: Path, auth: str | None, targets: tuple[str, ...]
) -> None:
    has_web_backend = "web" in targets and "backend" in targets
    if not has_web_backend or auth is None:
        return

    web_env = ["# Web app environment", "VITE_CONVEX_URL="]
    if auth == "clerk":
        web_env.append("VITE_CLERK_PUBLISHABLE_KEY=")
        backend_env = [
            "# Backend environment",
            "CONVEX_DEPLOYMENT=",
            "CLERK_FRONTEND_API_URL=",
            "AUTH_PROVIDER=clerk",
        ]
    else:
        web_env.extend(
            [
                "VITE_CONVEX_SITE_URL=",
                "VITE_SITE_URL=http://localhost:3000",
            ]
        )
        backend_env = [
            "# Backend environment",
            "CONVEX_DEPLOYMENT=",
            "SITE_URL=http://localhost:3000",
            "AUTH_PROVIDER=better-auth",
        ]

    (output_root / "apps" / "web" / ".env.example").write_text(
        "\n".join(web_env) + "\n",
        encoding="utf-8",
    )
    (output_root / "apps" / "backend" / ".env.example").write_text(
        "\n".join(backend_env) + "\n",
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

    scaffold_web_backend_env_examples(
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
