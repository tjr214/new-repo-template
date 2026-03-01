from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from new_repo_template import scaffold
from new_repo_template.snapshot_builder import build_snapshot_assets
from new_repo_template.sync_ops import run_template_assets_sync, run_tools_sync


AUTH_CHOICES: tuple[str, str] = ("clerk", "better-auth")

INTERACTIVE_TARGETS_REMEDIATION = (
    "interactive input unavailable while selecting targets; rerun with "
    "--no-interactive and provide one or more --target options"
)

INTERACTIVE_AUTH_REMEDIATION = (
    "interactive input unavailable while selecting auth; rerun with "
    "--no-interactive and provide --auth"
)


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


def prompt_targets() -> list[str]:
    print("nurt new interactive mode")
    print("Select targets (comma-separated):")
    for index, target in enumerate(scaffold.TARGET_CHOICES, start=1):
        print(f"  {index}) {target}")

    while True:
        try:
            user_input = input("Targets [foundation]: ").strip()
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


def prompt_auth() -> str:
    print("Select auth provider for web+backend:")
    print("  1) clerk")
    print("  2) better-auth")

    while True:
        try:
            user_input = input("Auth [clerk]: ").strip().lower()
        except EOFError as exc:
            raise RuntimeError(INTERACTIVE_AUTH_REMEDIATION) from exc
        if user_input in {"", "1", "clerk"}:
            return "clerk"
        if user_input in {"2", "better-auth"}:
            return "better-auth"
        print("Invalid auth choice. Use 1, 2, clerk, or better-auth.", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nurt")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="Create a new project")
    new_parser.add_argument("project_name")
    new_parser.add_argument(
        "--target", action="append", choices=scaffold.TARGET_CHOICES
    )
    new_parser.add_argument("--auth", choices=AUTH_CHOICES)
    new_parser.add_argument("--no-interactive", action="store_true")
    new_parser.add_argument("--dry-run", action="store_true")
    new_parser.set_defaults(handler=handle_new)

    update_parser = subparsers.add_parser("update", help="Upgrade nurt")
    update_parser.add_argument("--dry-run", action="store_true")
    update_parser.set_defaults(handler=handle_update)

    tools_parser = subparsers.add_parser("tools", help="Sync developer tools")
    tools_subparsers = tools_parser.add_subparsers(dest="tools_command", required=True)
    tools_sync_parser = tools_subparsers.add_parser(
        "sync", help="Sync toolchain dependencies"
    )
    tools_sync_parser.add_argument("--dry-run", action="store_true")
    tools_sync_parser.set_defaults(handler=handle_tools_sync)

    template_assets_parser = subparsers.add_parser(
        "template-assets", help="Template asset operations"
    )
    template_assets_subparsers = template_assets_parser.add_subparsers(
        dest="template_assets_command", required=True
    )
    template_assets_sync_parser = template_assets_subparsers.add_parser(
        "sync", help="Sync template assets from template repository"
    )
    template_assets_sync_parser.add_argument("--dry-run", action="store_true")
    template_assets_sync_parser.set_defaults(handler=handle_template_assets_sync)

    template_assets_snapshot_parser = template_assets_subparsers.add_parser(
        "snapshot", help="Generate bundled snapshot assets from source manifest"
    )
    template_assets_snapshot_parser.add_argument("--dry-run", action="store_true")
    template_assets_snapshot_parser.add_argument(
        "--source-root", type=Path, default=Path.cwd()
    )
    template_assets_snapshot_parser.add_argument("--output-root", type=Path)
    template_assets_snapshot_parser.set_defaults(
        handler=handle_template_assets_snapshot
    )

    return parser


def handle_new(args: argparse.Namespace) -> int:
    output_path = (Path.cwd() / args.project_name).resolve()

    selected_targets: list[str]
    selected_auth = args.auth
    try:
        if args.target:
            selected_targets = list(args.target)
        elif args.no_interactive:
            selected_targets = ["foundation"]
        else:
            selected_targets = prompt_targets()

        has_web_backend = "web" in selected_targets and "backend" in selected_targets
        if has_web_backend and selected_auth is None and not args.no_interactive:
            selected_auth = prompt_auth()
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
        return int(scaffold.main(scaffold_args))
    except SystemExit as exc:
        code = exc.code
        return int(code) if isinstance(code, int) else 1


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
    return run_tools_sync(dry_run=args.dry_run)


def handle_template_assets_sync(args: argparse.Namespace) -> int:
    return run_template_assets_sync(dry_run=args.dry_run, project_root=Path.cwd())


def handle_template_assets_snapshot(args: argparse.Namespace) -> int:
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
        print("DRY RUN: template-assets snapshot")
        for relative_path in result.copied_files:
            print(f"  - would copy: {relative_path}")
        print("DRY RUN: metadata would be written to metadata.json")
        return 0

    print("Snapshot generation completed:")
    for relative_path in result.copied_files:
        print(f"  - copied: {relative_path}")
    if result.metadata_path is not None:
        print(f"  - metadata: {result.metadata_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    perform_startup_update_check()
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
