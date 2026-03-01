from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScaffoldPlan:
    target: str
    output: Path
    paths: tuple[str, ...]
    include_python_workspace: bool


FOUNDATION_PATHS: tuple[str, ...] = ("apps/", "packages/", "pyproject.toml")
PYTHON_PATHS: tuple[str, ...] = (
    *FOUNDATION_PATHS,
    "apps/python/",
    "apps/python/pyproject.toml",
    "apps/python/src/python_app/",
    "apps/python/tests/",
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="new-repo-template")
    parser.add_argument("--target", required=True, choices=("foundation", "python"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--no-interactive", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def resolve_plan(target: str, output: Path) -> ScaffoldPlan:
    if target == "foundation":
        return ScaffoldPlan(
            target=target,
            output=output,
            paths=FOUNDATION_PATHS,
            include_python_workspace=False,
        )
    if target == "python":
        return ScaffoldPlan(
            target=target,
            output=output,
            paths=PYTHON_PATHS,
            include_python_workspace=True,
        )
    raise ValueError(f"Unsupported target: {target}")


def render_plan(plan: ScaffoldPlan) -> str:
    lines = [
        "Resolved scaffold plan:",
        f"- target: {plan.target}",
        f"- output: {plan.output}",
        "- root layout:",
    ]
    lines.extend(f"  - {path}" for path in plan.paths)
    return "\n".join(lines)


def write_root_pyproject(*, output_root: Path, include_python_workspace: bool) -> None:
    root_content = ROOT_PYPROJECT_BASE
    if include_python_workspace:
        root_content += PYTHON_WORKSPACE_SECTION
    (output_root / "pyproject.toml").write_text(root_content, encoding="utf-8")


def scaffold_foundation(plan: ScaffoldPlan) -> None:
    plan.output.mkdir(parents=True, exist_ok=False)
    (plan.output / "apps").mkdir()
    (plan.output / "packages").mkdir()
    write_root_pyproject(
        output_root=plan.output,
        include_python_workspace=plan.include_python_workspace,
    )


def scaffold_python_lane(plan: ScaffoldPlan) -> None:
    scaffold_foundation(plan)
    lane_root = plan.output / "apps" / "python"
    (lane_root / "src" / "python_app").mkdir(parents=True)
    (lane_root / "tests").mkdir()
    (lane_root / "pyproject.toml").write_text(PYTHON_LANE_PYPROJECT, encoding="utf-8")
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


def execute_scaffold(plan: ScaffoldPlan) -> None:
    if plan.target == "foundation":
        scaffold_foundation(plan)
        return
    if plan.target == "python":
        scaffold_python_lane(plan)
        return
    raise ValueError(f"Unsupported target: {plan.target}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.no_interactive:
        parser.error("interactive mode is not implemented yet; use --no-interactive")

    plan = resolve_plan(target=args.target, output=args.output)

    if args.dry_run:
        print(render_plan(plan))
        return 0

    execute_scaffold(plan)
    print(render_plan(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
