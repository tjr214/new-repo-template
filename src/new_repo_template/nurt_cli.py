from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from new_repo_template import scaffold


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nurt")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="Create a new project")
    new_parser.add_argument("project_name")
    new_parser.add_argument(
        "--target", action="append", choices=scaffold.TARGET_CHOICES
    )
    new_parser.add_argument("--auth", choices=("clerk", "better-auth"))
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
        "template-assets", help="Sync template assets"
    )
    template_assets_subparsers = template_assets_parser.add_subparsers(
        dest="template_assets_command", required=True
    )
    template_assets_sync_parser = template_assets_subparsers.add_parser(
        "sync", help="Sync template assets from template repository"
    )
    template_assets_sync_parser.add_argument("--dry-run", action="store_true")
    template_assets_sync_parser.set_defaults(handler=handle_template_assets_sync)

    return parser


def handle_new(args: argparse.Namespace) -> int:
    output_path = (Path.cwd() / args.project_name).resolve()
    selected_targets = args.target if args.target else ["foundation"]

    scaffold_args: list[str] = []
    for target in selected_targets:
        scaffold_args.extend(["--target", target])

    if args.auth is not None:
        scaffold_args.extend(["--auth", args.auth])

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
    script_path = Path.cwd() / ".template_scripts" / "update-opencode.sh"
    if args.dry_run:
        print("DRY RUN: tools sync")
        print(
            "DRY RUN: would execute `sh .template_scripts/update-opencode.sh --dry-run`"
        )
        return 0

    if not script_path.exists():
        print(
            "Error: tools sync script not found at .template_scripts/update-opencode.sh",
            file=sys.stderr,
        )
        return 1

    result = subprocess.run(["sh", str(script_path)], check=False)
    return result.returncode


def handle_template_assets_sync(args: argparse.Namespace) -> int:
    script_path = Path.cwd() / ".template_scripts" / "update-template-from-git.sh"
    if args.dry_run:
        print("DRY RUN: template-assets sync")
        print(
            "DRY RUN: would execute `sh .template_scripts/update-template-from-git.sh`"
        )
        return 0

    if not script_path.exists():
        print(
            "Error: template-assets sync script not found at .template_scripts/update-template-from-git.sh",
            file=sys.stderr,
        )
        return 1

    result = subprocess.run(["sh", str(script_path)], check=False)
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    perform_startup_update_check()
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
