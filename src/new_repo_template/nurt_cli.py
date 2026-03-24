from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from rich.console import Console

from new_repo_template import add_mode
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
from new_repo_template.interactive_tui import (
    run_interactive_add_wizard,
    run_interactive_wizard,
)
from new_repo_template.project_naming import normalize_project_name
from new_repo_template.repo_identity import validate_nurt_repo_root
from new_repo_template.snapshot_builder import build_snapshot_assets
from new_repo_template.sync_ops import run_template_assets_sync, run_tools_sync
from new_repo_template.version_baseline import (
    run_versions_check,
    run_versions_update,
)


AUTH_CHOICES: tuple[str, str, str] = ("clerk", "better-auth", "none")

SELF_UPDATE_PACKAGE_NAME = "nurt-ai"
SELF_UPDATE_COMMAND_NAME = "nurt"
SELF_UPDATE_INSTALL_SPEC = "git+https://github.com/tjr214/new-repo-template.git"

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
                f"Update available for nurt: {simulated_version}. Run `nurt upgrade`.",
                file=sys.stderr,
            )
        return

    try:
        check_result = subprocess.run(
            ["uv", "tool", "list", "--outdated"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except FileNotFoundError, subprocess.TimeoutExpired:
        return

    if check_result.returncode != 0:
        return

    if _outdated_tools_include_nurt(check_result.stdout):
        print("Update available for nurt. Run `nurt upgrade`.", file=sys.stderr)


def _outdated_tools_include_nurt(output: str) -> bool:
    package_names = {SELF_UPDATE_PACKAGE_NAME, SELF_UPDATE_COMMAND_NAME}
    for raw_line in output.splitlines():
        line = raw_line.strip().lower()
        if line == "" or line.startswith("-"):
            continue
        package_name = line.split(maxsplit=1)[0]
        if package_name in package_names:
            return True
    return False


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


def prompt_add_targets(*, ui_config: InteractiveUIConfig) -> list[str]:
    print("nurt add interactive mode")
    print("Select targets to add (comma-separated):")
    for index, target in enumerate(add_mode.ADDABLE_TARGET_CHOICES, start=1):
        print(f"  {index}) {target}")

    while True:
        try:
            user_input = ask_user_input(
                config=ui_config,
                prompt="Targets to add: ",
                default="",
            )
        except EOFError as exc:
            raise RuntimeError(INTERACTIVE_TARGETS_REMEDIATION) from exc

        choices: list[str] = []
        invalid_tokens: list[str] = []
        for token in [piece.strip().lower() for piece in user_input.split(",")]:
            if token == "":
                continue
            if token.isdigit():
                index = int(token)
                if 1 <= index <= len(add_mode.ADDABLE_TARGET_CHOICES):
                    token = add_mode.ADDABLE_TARGET_CHOICES[index - 1]
                else:
                    invalid_tokens.append(token)
                    continue

            if token not in add_mode.ADDABLE_TARGET_CHOICES:
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
            print("At least one add target must be selected.", file=sys.stderr)
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


def prompt_project_names_for_target(
    *, ui_config: InteractiveUIConfig, target: str
) -> list[str]:
    default_name = scaffold.default_project_name(target)

    while True:
        try:
            user_input = ask_user_input(
                config=ui_config,
                prompt=f"Names for {target} projects [{default_name}]: ",
                default=default_name,
            )
        except EOFError as exc:
            raise RuntimeError(INTERACTIVE_TARGETS_REMEDIATION) from exc

        raw_value = user_input or default_name
        names: list[str] = []
        try:
            for token in [piece.strip() for piece in raw_value.split(",")]:
                if token == "":
                    continue
                normalized = resolve_project_name(token)
                if normalized not in names:
                    names.append(normalized)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            continue

        if names:
            return names
        print("At least one project name is required.", file=sys.stderr)


def prompt_backend_auth_for_project(
    *, ui_config: InteractiveUIConfig, backend_name: str
) -> str:
    render_auth_menu(config=ui_config)
    while True:
        try:
            user_input = ask_user_input(
                config=ui_config,
                prompt=f"Auth for backend '{backend_name}' [none]: ",
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


def prompt_web_backend_binding(
    *, ui_config: InteractiveUIConfig, web_name: str, backend_names: tuple[str, ...]
) -> str:
    while True:
        try:
            user_input = ask_user_input(
                config=ui_config,
                prompt=(
                    f"Backend for web '{web_name}' "
                    f"[{backend_names[0]}] ({', '.join(backend_names)}): "
                ),
                default=backend_names[0],
            )
        except EOFError as exc:
            raise RuntimeError(INTERACTIVE_AUTH_REMEDIATION) from exc

        candidate = resolve_project_name(user_input or backend_names[0])
        if candidate in backend_names:
            return candidate
        print(
            "Invalid backend choice. Use one of: " + ", ".join(backend_names),
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
    new_parser.add_argument("--project", action="append")
    new_parser.add_argument("--backend-auth", action="append")
    new_parser.add_argument("--web-backend", action="append")
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

    add_parser = subparsers.add_parser("add", help="Add projects to an existing repo")
    add_parser.add_argument(
        "--target", action="append", choices=add_mode.ADDABLE_TARGET_CHOICES
    )
    add_parser.add_argument("--project", action="append")
    add_parser.add_argument("--backend-auth", action="append")
    add_parser.add_argument("--web-backend", action="append")
    add_parser.add_argument("--auth", choices=AUTH_CHOICES)
    add_parser.add_argument("--no-interactive", action="store_true")
    add_parser.add_argument("--dry-run", action="store_true")
    add_parser.set_defaults(handler=handle_add)

    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade nurt")
    upgrade_parser.add_argument("--dry-run", action="store_true")
    upgrade_parser.set_defaults(handler=handle_upgrade)

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
    selected_projects: list[str] = list(getattr(args, "project", None) or [])
    selected_backend_auths: list[str] = list(getattr(args, "backend_auth", None) or [])
    selected_web_backends: list[str] = list(getattr(args, "web_backend", None) or [])
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
            selected_projects = list(getattr(wizard_result, "projects", ()))
            selected_backend_auths = list(getattr(wizard_result, "backend_auths", ()))
            selected_web_backends = list(getattr(wizard_result, "web_backends", ()))
            selected_auth = wizard_result.auth
            install_core_tools = wizard_result.install_core_tools
            install_bmad = wizard_result.install_bmad
        else:
            if project_name is None:
                project_name = prompt_project_name(ui_config=ui_config)

            if args.target:
                selected_targets = list(args.target)
            elif selected_projects:
                selected_targets = []
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
                selected_projects = list(getattr(wizard_result, "projects", ()))
                selected_backend_auths = list(
                    getattr(wizard_result, "backend_auths", ())
                )
                selected_web_backends = list(getattr(wizard_result, "web_backends", ()))
                selected_auth = wizard_result.auth
                install_core_tools = wizard_result.install_core_tools
                install_bmad = wizard_result.install_bmad
            else:
                selected_targets = prompt_targets(ui_config=ui_config)

        if not selected_projects:
            for target in selected_targets:
                if target == "foundation":
                    continue
                if args.no_interactive or args.target:
                    names = [scaffold.default_project_name(target)]
                else:
                    names = prompt_project_names_for_target(
                        ui_config=ui_config,
                        target=target,
                    )
                selected_projects.extend(f"{target}:{name}" for name in names)

        output_path = (Path.cwd() / project_name).resolve()
        backend_names = tuple(
            resolve_project_name(project.split(":", 1)[1])
            for project in selected_projects
            if project.split(":", 1)[0] == "backend"
        )
        web_names = tuple(
            resolve_project_name(project.split(":", 1)[1])
            for project in selected_projects
            if project.split(":", 1)[0] == "web"
        )

        if backend_names and not selected_backend_auths:
            if selected_auth is not None:
                selected_backend_auths.extend(
                    f"{backend_name}:{selected_auth}" for backend_name in backend_names
                )
            elif not args.no_interactive:
                for backend_name in backend_names:
                    backend_auth = prompt_backend_auth_for_project(
                        ui_config=ui_config,
                        backend_name=backend_name,
                    )
                    selected_backend_auths.append(f"{backend_name}:{backend_auth}")

        if web_names and len(backend_names) == 1 and not selected_web_backends:
            selected_web_backends.extend(
                f"{web_name}:{backend_names[0]}" for web_name in web_names
            )
        elif (
            web_names
            and len(backend_names) > 1
            and not selected_web_backends
            and not args.no_interactive
        ):
            for web_name in web_names:
                backend_binding = prompt_web_backend_binding(
                    ui_config=ui_config,
                    web_name=web_name,
                    backend_names=backend_names,
                )
                selected_web_backends.append(f"{web_name}:{backend_binding}")

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
    if selected_projects:
        for project in selected_projects:
            scaffold_args.extend(["--project", project])
    else:
        for target in selected_targets:
            scaffold_args.extend(["--target", target])

    if selected_auth is not None:
        scaffold_args.extend(["--auth", selected_auth])
    for backend_auth in selected_backend_auths:
        scaffold_args.extend(["--backend-auth", backend_auth])
    for web_backend in selected_web_backends:
        scaffold_args.extend(["--web-backend", web_backend])

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

    return 0


def handle_add(args: argparse.Namespace) -> int:
    ui_config = resolve_ui_config()
    if ui_config.warning is not None:
        print(f"Warning: {ui_config.warning}", file=sys.stderr)

    try:
        repo_root = validate_nurt_repo_root(cwd=Path.cwd().resolve())
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    existing_state = add_mode.inventory_existing_repo(repo_root=repo_root)

    selected_targets: list[str] = list(getattr(args, "target", None) or [])
    selected_projects: list[str] = list(getattr(args, "project", None) or [])
    selected_backend_auths: list[str] = list(getattr(args, "backend_auth", None) or [])
    selected_web_backends: list[str] = list(getattr(args, "web_backend", None) or [])
    selected_auth = args.auth

    try:
        if not selected_targets and not selected_projects and not args.no_interactive:
            if ui_config.use_rich:
                wizard_result = run_interactive_add_wizard(
                    repo_root=repo_root,
                    existing_backend_names=existing_state.backend_names,
                    existing_project_keys=tuple(
                        (project.kind, project.name)
                        for project in existing_state.projects
                    ),
                )
                if wizard_result is None:
                    print(INTERACTIVE_WIZARD_CANCELLED, file=sys.stderr)
                    return 1
                selected_projects = list(wizard_result.projects)
                selected_backend_auths = list(wizard_result.backend_auths)
                selected_web_backends = list(wizard_result.web_backends)
            else:
                selected_targets = prompt_add_targets(ui_config=ui_config)

        if not selected_projects:
            for target in selected_targets:
                if args.no_interactive or args.target:
                    names = [scaffold.default_project_name(target)]
                else:
                    names = prompt_project_names_for_target(
                        ui_config=ui_config,
                        target=target,
                    )
                selected_projects.extend(f"{target}:{name}" for name in names)

        requested_backend_names = tuple(
            resolve_project_name(project.split(":", 1)[1])
            for project in selected_projects
            if project.split(":", 1)[0] == "backend"
        )
        requested_web_names = tuple(
            resolve_project_name(project.split(":", 1)[1])
            for project in selected_projects
            if project.split(":", 1)[0] == "web"
        )
        combined_backend_names = tuple(
            dict.fromkeys((*existing_state.backend_names, *requested_backend_names))
        )

        if requested_backend_names and not selected_backend_auths:
            if selected_auth is not None:
                selected_backend_auths.extend(
                    f"{backend_name}:{selected_auth}"
                    for backend_name in requested_backend_names
                )
            elif not args.no_interactive:
                for backend_name in requested_backend_names:
                    backend_auth = prompt_backend_auth_for_project(
                        ui_config=ui_config,
                        backend_name=backend_name,
                    )
                    selected_backend_auths.append(f"{backend_name}:{backend_auth}")

        if (
            requested_web_names
            and len(combined_backend_names) == 1
            and not selected_web_backends
        ):
            selected_web_backends.extend(
                f"{web_name}:{combined_backend_names[0]}"
                for web_name in requested_web_names
            )
        elif (
            requested_web_names
            and len(combined_backend_names) > 1
            and not selected_web_backends
            and not args.no_interactive
        ):
            for web_name in requested_web_names:
                backend_binding = prompt_web_backend_binding(
                    ui_config=ui_config,
                    web_name=web_name,
                    backend_names=combined_backend_names,
                )
                selected_web_backends.append(f"{web_name}:{backend_binding}")
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    validation_parser = argparse.ArgumentParser(prog="nurt add")
    try:
        requested_projects = add_mode.resolve_add_projects(
            parser=validation_parser,
            args=argparse.Namespace(
                target=None if selected_projects else selected_targets or None,
                project=selected_projects or None,
                backend_auth=selected_backend_auths or None,
                web_backend=selected_web_backends or None,
                auth=selected_auth,
            ),
            existing_state=existing_state,
        )
    except SystemExit as exc:
        code = exc.code
        return 1 if isinstance(code, int) and code != 0 else 0 if code == 0 else 1

    try:
        plan = add_mode.build_add_plan(
            repo_root=repo_root,
            existing_state=existing_state,
            requested_projects=requested_projects,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(add_mode.render_add_plan(plan))
    if args.dry_run:
        return 0

    try:
        summary = add_mode.execute_add(plan)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(add_mode.render_add_completion(repo_root=repo_root, summary=summary))
    return 0


def handle_upgrade(args: argparse.Namespace) -> int:
    command = ["uv", "tool", "upgrade", SELF_UPDATE_PACKAGE_NAME]
    if args.dry_run:
        print(
            "DRY RUN: would execute "
            f"`uv tool upgrade {SELF_UPDATE_PACKAGE_NAME}` "
            f"to refresh the installed `{SELF_UPDATE_COMMAND_NAME}` tool"
        )
        return 0

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        print(
            "Error: uv is required to upgrade nurt. Install uv and rerun `nurt upgrade`.",
            file=sys.stderr,
        )
        return 1

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    if result.returncode != 0:
        print(
            "Error: `uv tool upgrade nurt-ai` failed. "
            "If the current install is no longer upgradeable through uv, reinstall with "
            f"`uv tool install {SELF_UPDATE_INSTALL_SPEC}`.",
            file=sys.stderr,
        )
        return result.returncode

    print(
        "If you want to refresh bundled managed files in a generated repo, "
        "run `nurt sync template-assets` separately."
    )
    return 0


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
        print("DRY RUN: runtime manifest would be refreshed at manifest.json")
        return 0

    print("Template-assets validate completed:")
    for relative_path in result.copied_files:
        print(f"  - validated bundled template: {relative_path}")
    if result.manifest_path is not None:
        print(f"  - runtime manifest refreshed: {result.manifest_path}")
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
