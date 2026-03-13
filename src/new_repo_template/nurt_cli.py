from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from rich.console import Console

from new_repo_template.bmad_runner import run_bmad_sync
from new_repo_template.post_create import (
    render_completion_overview,
    render_post_create_plan,
    run_post_create_pipeline,
)
from new_repo_template import scaffold
from new_repo_template.interactive_ui import (
    InteractiveUIConfig,
    ask_user_input,
    render_project_name_prompt,
    render_auth_menu,
    render_target_menu,
    render_yes_no_menu,
    resolve_ui_config,
)
from new_repo_template.interactive_tui import run_interactive_wizard
from new_repo_template.project_naming import normalize_project_name
from new_repo_template.snapshot_builder import build_snapshot_assets
from new_repo_template.sync_ops import run_template_assets_sync, run_tools_sync
from new_repo_template.version_baseline import (
    run_versions_check,
    run_versions_update,
)


AUTH_CHOICES: tuple[str, str, str] = ("clerk", "better-auth", "none")

INTERACTIVE_WIZARD_CANCELLED = "Interactive wizzard cancelled. Maybe next time!"

INTERACTIVE_PROJECT_NAME_REMEDIATION = (
    "interactive input unavailable while selecting project name; rerun with "
    "`nurt new <project-name>` or provide a project name before --no-interactive"
)

INTERACTIVE_TARGETS_REMEDIATION = (
    "interactive input unavailable while selecting targets; rerun with "
    "--no-interactive and provide one or more --target options"
)

INTERACTIVE_AUTH_REMEDIATION = (
    "interactive input unavailable while selecting auth; rerun with "
    "--no-interactive and provide --auth clerk, --auth better-auth, or --auth none"
)

INTERACTIVE_CORE_TOOLS_REMEDIATION = (
    "interactive input unavailable while selecting the core-tools updater; rerun with "
    "--no-interactive and provide --install-core-tools or --no-install-core-tools"
)

INTERACTIVE_BMAD_REMEDIATION = (
    "interactive input unavailable while selecting BMAD Method installation; rerun with "
    "--no-interactive and provide --install-bmad or --no-install-bmad"
)


def resolve_project_name(raw_project_name: str) -> str:
    return normalize_project_name(raw_project_name)


def prompt_project_name(*, ui_config: InteractiveUIConfig) -> str:
    render_project_name_prompt(config=ui_config)

    while True:
        try:
            user_input = ask_user_input(
                config=ui_config,
                prompt="Project name: ",
                default="",
            )
        except EOFError as exc:
            raise RuntimeError(INTERACTIVE_PROJECT_NAME_REMEDIATION) from exc

        try:
            return resolve_project_name(user_input)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)


def perform_startup_update_check() -> None:
    simulated_version = os.environ.get("NURT_UPDATE_CHECK_SIMULATE")
    if simulated_version is not None:
        normalized = simulated_version.strip().lower()
        if normalized not in {"", "none", "0", "false", "no"}:
            print(
                f"Update available for nurt: {simulated_version}. Run `nurt update`.",
                file=sys.stderr,
            )
        return

    try:
        check_result = subprocess.run(
            ["uv", "tool", "upgrade", "--dry-run", "nurt"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except FileNotFoundError, subprocess.TimeoutExpired:
        return

    combined_output = f"{check_result.stdout}\n{check_result.stderr}".lower()
    if (
        check_result.returncode == 0
        and "upgrade" in combined_output
        and "nurt" in combined_output
        and "would" in combined_output
    ):
        print("Update available for nurt. Run `nurt update`.", file=sys.stderr)


def prompt_targets(*, ui_config: InteractiveUIConfig) -> list[str]:
    render_target_menu(config=ui_config, targets=scaffold.TARGET_CHOICES)

    while True:
        try:
            user_input = ask_user_input(
                config=ui_config,
                prompt="Targets [foundation]: ",
                default="foundation",
            )
        except EOFError as exc:
            raise RuntimeError(INTERACTIVE_TARGETS_REMEDIATION) from exc
        if user_input == "":
            return ["foundation"]

        choices: list[str] = []
        invalid_tokens: list[str] = []
        for token in [piece.strip().lower() for piece in user_input.split(",")]:
            if token == "":
                continue
            if token.isdigit():
                index = int(token)
                if 1 <= index <= len(scaffold.TARGET_CHOICES):
                    token = scaffold.TARGET_CHOICES[index - 1]
                else:
                    invalid_tokens.append(token)
                    continue

            if token not in scaffold.TARGET_CHOICES:
                invalid_tokens.append(token)
                continue

            if token not in choices:
                choices.append(token)

        if invalid_tokens:
            print(
                "Invalid target selection:", ", ".join(invalid_tokens), file=sys.stderr
            )
            continue
        if not choices:
            print("At least one target must be selected.", file=sys.stderr)
            continue
        return choices


def prompt_auth(*, ui_config: InteractiveUIConfig) -> str:
    render_auth_menu(config=ui_config)

    while True:
        try:
            user_input = ask_user_input(
                config=ui_config,
                prompt="Auth [none]: ",
                default="none",
            ).lower()
        except EOFError as exc:
            raise RuntimeError(INTERACTIVE_AUTH_REMEDIATION) from exc
        if user_input in {"1", "clerk"}:
            return "clerk"
        if user_input in {"2", "better-auth"}:
            return "better-auth"
        if user_input in {"", "3", "none"}:
            return "none"
        print(
            "Invalid auth choice. Use 1, 2, 3, clerk, better-auth, or none.",
            file=sys.stderr,
        )


def prompt_yes_no_choice(
    *,
    ui_config: InteractiveUIConfig,
    title: str,
    question: str,
    remediation: str,
    default_yes: bool = False,
) -> bool:
    render_yes_no_menu(
        config=ui_config,
        title=title,
        question=question,
        default_yes=default_yes,
    )

    default_value = "y" if default_yes else "n"
    prompt_hint = "[Y/n]" if default_yes else "[y/N]"

    while True:
        try:
            user_input = ask_user_input(
                config=ui_config,
                prompt=f"{question} {prompt_hint}: ",
                default=default_value,
            ).lower()
        except EOFError as exc:
            raise RuntimeError(remediation) from exc

        if user_input == "":
            return default_yes
        if user_input in {"n", "no"}:
            return False
        if user_input in {"y", "yes"}:
            return True
        print("Invalid choice. Use y, yes, n, or no.", file=sys.stderr)


def prompt_install_core_tools(*, ui_config: InteractiveUIConfig) -> bool:
    return prompt_yes_no_choice(
        ui_config=ui_config,
        title="Core tools updater",
        question="Do you want to install/update the core set of tools?",
        remediation=INTERACTIVE_CORE_TOOLS_REMEDIATION,
        default_yes=False,
    )


def prompt_install_bmad(*, ui_config: InteractiveUIConfig) -> bool:
    return prompt_yes_no_choice(
        ui_config=ui_config,
        title="BMAD Method",
        question="Do you want to install the BMAD Method?",
        remediation=INTERACTIVE_BMAD_REMEDIATION,
        default_yes=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nurt")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="Create a new project")
    new_parser.add_argument("project_name", nargs="?")
    new_parser.add_argument(
        "--target", action="append", choices=scaffold.TARGET_CHOICES
    )
    new_parser.add_argument("--auth", choices=AUTH_CHOICES)
    new_parser.add_argument(
        "--install-core-tools",
        action=argparse.BooleanOptionalAction,
        default=None,
    )
    new_parser.add_argument(
        "--install-bmad",
        action=argparse.BooleanOptionalAction,
        default=None,
    )
    new_parser.add_argument("--no-interactive", action="store_true")
    new_parser.add_argument("--dry-run", action="store_true")
    new_parser.set_defaults(handler=handle_new)

    update_parser = subparsers.add_parser("update", help="Upgrade nurt")
    update_parser.add_argument("--dry-run", action="store_true")
    update_parser.set_defaults(handler=handle_update)

    sync_parser = subparsers.add_parser("sync", help="Sync managed resources")
    sync_subparsers = sync_parser.add_subparsers(dest="sync_command", required=True)

    sync_tools_parser = sync_subparsers.add_parser("tools", help="Sync developer tools")
    sync_tools_parser.add_argument("--dry-run", action="store_true")
    sync_tools_parser.set_defaults(handler=handle_tools_sync)

    sync_bmad_parser = sync_subparsers.add_parser(
        "bmad", help="Install or update the BMAD Method"
    )
    sync_bmad_parser.add_argument("--dry-run", action="store_true")
    sync_bmad_parser.set_defaults(handler=handle_bmad_sync)

    sync_template_assets_parser = sync_subparsers.add_parser(
        "template-assets", help="Sync template assets from template repository"
    )
    sync_template_assets_parser.add_argument("--dry-run", action="store_true")
    sync_template_assets_parser.set_defaults(handler=handle_template_assets_sync)

    template_assets_parser = subparsers.add_parser(
        "template-assets", help="Template asset utilities"
    )
    template_assets_subparsers = template_assets_parser.add_subparsers(
        dest="template_assets_command", required=True
    )

    template_assets_validate_parser = template_assets_subparsers.add_parser(
        "validate",
        help="Validate bundled template entries and refresh metadata",
    )
    template_assets_validate_parser.add_argument("--dry-run", action="store_true")
    template_assets_validate_parser.add_argument(
        "--source-root", type=Path, default=Path.cwd()
    )
    template_assets_validate_parser.add_argument("--output-root", type=Path)
    template_assets_validate_parser.set_defaults(
        handler=handle_template_assets_validate
    )

    versions_parser = subparsers.add_parser(
        "versions", help="Manage version baseline metadata"
    )
    versions_subparsers = versions_parser.add_subparsers(
        dest="versions_command", required=True
    )

    versions_check_parser = versions_subparsers.add_parser(
        "check", help="Validate version baseline metadata"
    )
    versions_check_parser.add_argument(
        "--baseline-path", type=Path, default=Path("version-baseline.json")
    )
    versions_check_parser.add_argument("--check-latest", action="store_true")
    versions_check_parser.add_argument("--check-lockfiles", action="store_true")
    versions_check_parser.add_argument("--source-file", type=Path)
    versions_check_parser.set_defaults(handler=handle_versions_check)

    versions_update_parser = versions_subparsers.add_parser(
        "update", help="Refresh version baseline metadata"
    )
    versions_update_parser.add_argument(
        "--baseline-path", type=Path, default=Path("version-baseline.json")
    )
    versions_update_parser.add_argument("--source-file", type=Path)
    versions_update_parser.add_argument("--dry-run", action="store_true")
    versions_update_parser.add_argument("--skip-lockfiles", action="store_true")
    versions_update_parser.set_defaults(handler=handle_versions_update)

    return parser


def handle_new(args: argparse.Namespace) -> int:
    ui_config = resolve_ui_config()
    if ui_config.warning is not None:
        print(f"Warning: {ui_config.warning}", file=sys.stderr)

    project_name = None
    if args.project_name is not None:
        try:
            project_name = resolve_project_name(args.project_name)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    if project_name is None and args.no_interactive:
        print(
            "Error: project name is required when using --no-interactive.",
            file=sys.stderr,
        )
        return 1

    selected_targets: list[str]
    selected_auth = args.auth
    install_core_tools = args.install_core_tools
    install_bmad = args.install_bmad
    try:
        if project_name is None and not args.no_interactive and ui_config.use_rich:
            wizard_result = run_interactive_wizard(
                project_name=None,
                output_root=Path.cwd().resolve(),
                initial_targets=tuple(args.target) if args.target else None,
                initial_auth=selected_auth,
                initial_install_core_tools=install_core_tools,
                initial_install_bmad=install_bmad,
            )
            if wizard_result is None:
                print(INTERACTIVE_WIZARD_CANCELLED, file=sys.stderr)
                return 1
            project_name = wizard_result.project_name
            selected_targets = list(wizard_result.targets)
            selected_auth = wizard_result.auth
            install_core_tools = wizard_result.install_core_tools
            install_bmad = wizard_result.install_bmad
        else:
            if project_name is None:
                project_name = prompt_project_name(ui_config=ui_config)

            if args.target:
                selected_targets = list(args.target)
            elif args.no_interactive:
                selected_targets = ["foundation"]
            elif ui_config.use_rich:
                wizard_result = run_interactive_wizard(
                    project_name=project_name,
                    output_root=Path.cwd().resolve(),
                    initial_targets=tuple(args.target) if args.target else None,
                    initial_auth=selected_auth,
                    initial_install_core_tools=install_core_tools,
                    initial_install_bmad=install_bmad,
                )
                if wizard_result is None:
                    print(INTERACTIVE_WIZARD_CANCELLED, file=sys.stderr)
                    return 1
                project_name = wizard_result.project_name
                selected_targets = list(wizard_result.targets)
                selected_auth = wizard_result.auth
                install_core_tools = wizard_result.install_core_tools
                install_bmad = wizard_result.install_bmad
            else:
                selected_targets = prompt_targets(ui_config=ui_config)

        output_path = (Path.cwd() / project_name).resolve()
        has_backend = "backend" in selected_targets
        if has_backend and selected_auth is None and not args.no_interactive:
            selected_auth = prompt_auth(ui_config=ui_config)

        if install_core_tools is None:
            install_core_tools = (
                False
                if args.no_interactive
                else prompt_install_core_tools(ui_config=ui_config)
            )

        if install_bmad is None:
            install_bmad = (
                False
                if args.no_interactive
                else prompt_install_bmad(ui_config=ui_config)
            )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    scaffold_args: list[str] = []
    for target in selected_targets:
        scaffold_args.extend(["--target", target])

    if selected_auth is not None:
        scaffold_args.extend(["--auth", selected_auth])

    scaffold_args.extend(["--no-interactive", "--output", str(output_path)])
    if args.dry_run:
        scaffold_args.append("--dry-run")

    try:
        scaffold_status = int(scaffold.main(scaffold_args))
    except SystemExit as exc:
        code = exc.code
        scaffold_status = int(code) if isinstance(code, int) else 1

    if scaffold_status != 0:
        return scaffold_status

    if args.dry_run:
        print(
            render_post_create_plan(
                project_root=output_path,
                install_bmad=bool(install_bmad),
                install_core_tools=bool(install_core_tools),
            )
        )
        return 0

    pipeline_status = run_post_create_pipeline(
        project_root=output_path,
        install_bmad=bool(install_bmad),
        install_core_tools=bool(install_core_tools),
        use_tui=ui_config.use_rich,
    )
    if pipeline_status != 0:
        return pipeline_status

    Console().print(
        render_completion_overview(
            project_root=output_path,
            targets=tuple(selected_targets),
            auth=selected_auth,
            install_bmad=bool(install_bmad),
            install_core_tools=bool(install_core_tools),
        )
    )

    try:
        os.chdir(output_path)
    except OSError as exc:
        print(
            f"Error: unable to change into project directory `{output_path}`: {exc}",
            file=sys.stderr,
        )
        return 1

    return 0


def handle_update(args: argparse.Namespace) -> int:
    command = ["uv", "tool", "upgrade", "nurt"]
    if args.dry_run:
        print("DRY RUN: would execute `uv tool upgrade nurt`")
        return 0

    try:
        result = subprocess.run(command, check=False)
    except FileNotFoundError:
        print("Error: uv is required to update nurt.", file=sys.stderr)
        return 1

    return result.returncode


def handle_tools_sync(args: argparse.Namespace) -> int:
    ui_config = resolve_ui_config()
    if ui_config.warning is not None:
        print(f"Warning: {ui_config.warning}", file=sys.stderr)
    return run_tools_sync(
        dry_run=args.dry_run,
        cwd=Path.cwd().resolve(),
        use_tui=ui_config.use_rich and not args.dry_run,
    )


def handle_bmad_sync(args: argparse.Namespace) -> int:
    return run_bmad_sync(project_root=Path.cwd().resolve(), dry_run=args.dry_run)


def handle_template_assets_sync(args: argparse.Namespace) -> int:
    return run_template_assets_sync(dry_run=args.dry_run, project_root=Path.cwd())


def handle_template_assets_validate(args: argparse.Namespace) -> int:
    source_root = args.source_root.resolve()
    if args.output_root is None:
        output_root = source_root / "src" / "new_repo_template" / "snapshot_assets"
    else:
        output_root = args.output_root.resolve()

    result = build_snapshot_assets(
        source_root=source_root,
        output_root=output_root,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print("DRY RUN: template-assets validate")
        for relative_path in result.copied_files:
            print(f"  - would validate bundled template: {relative_path}")
        print("DRY RUN: metadata would be refreshed at metadata.json")
        return 0

    print("Template-assets validate completed:")
    for relative_path in result.copied_files:
        print(f"  - validated bundled template: {relative_path}")
    if result.metadata_path is not None:
        print(f"  - metadata refreshed: {result.metadata_path}")
    return 0


def handle_versions_check(args: argparse.Namespace) -> int:
    return run_versions_check(
        baseline_path=args.baseline_path.resolve(),
        check_latest=bool(args.check_latest),
        check_lockfiles=bool(args.check_lockfiles),
        project_root=Path.cwd().resolve(),
        source_file=args.source_file.resolve()
        if args.source_file is not None
        else None,
    )


def handle_versions_update(args: argparse.Namespace) -> int:
    return run_versions_update(
        baseline_path=args.baseline_path.resolve(),
        dry_run=bool(args.dry_run),
        project_root=Path.cwd().resolve(),
        regenerate_lockfiles=not bool(args.skip_lockfiles),
        source_file=args.source_file.resolve()
        if args.source_file is not None
        else None,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    perform_startup_update_check()
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
