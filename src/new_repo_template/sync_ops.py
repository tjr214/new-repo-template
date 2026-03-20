from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from platform import system

from new_repo_template.foundation_manifest import (
    get_foundation_sync_template_file_pairs,
)
from new_repo_template.repo_identity import validate_nurt_repo_root
from new_repo_template.snapshot_assets_loader import load_template_text
from new_repo_template.tool_sync_runner import run_tool_sync
from new_repo_template.tool_sync_tui import run_tool_sync_tui

SIMULATE_TOOLS_SYNC_FAILURE_ENV = "NURT_TOOLS_SYNC_SIMULATE_FAILURE"


@dataclass(frozen=True)
class ToolSyncResult:
    tool: str
    status: str
    detail: str


def _run_command(
    command: list[str], *, cwd: Path | None = None, timeout: int | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )


def _is_truthy_env(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() not in {"", "0", "false", "no", "none"}


def _run_shell_pipeline(command: str) -> subprocess.CompletedProcess[str]:
    return _run_command(["bash", "-lc", command])


def _command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def _capture_version(command: list[str]) -> str | None:
    try:
        result = _run_command(command, timeout=10)
    except subprocess.TimeoutExpired:
        return None
    if result.returncode != 0:
        return None

    output = result.stdout.strip() or result.stderr.strip()
    return output if output else None


def _capture_first_version_token(command: list[str]) -> str | None:
    raw = _capture_version(command)
    if raw is None:
        return None

    first_line = raw.splitlines()[0].strip()
    if first_line == "":
        return None
    parts = first_line.split()
    if len(parts) < 2:
        return first_line
    return parts[1]


def _stderr_or_stdout(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stderr.strip() or result.stdout.strip() or "command failed").replace(
        "\n", " | "
    )


def _result_from_versions(
    *, tool: str, before: str | None, after: str | None
) -> ToolSyncResult:
    if before is None and after is not None:
        return ToolSyncResult(tool=tool, status="INSTALLED", detail=after)
    if before is not None and after is not None:
        if before == after:
            return ToolSyncResult(tool=tool, status="UP-TO-DATE", detail=after)
        return ToolSyncResult(
            tool=tool, status="UPDATED", detail=f"{before} -> {after}"
        )
    if after is not None:
        return ToolSyncResult(tool=tool, status="COMPLETED", detail=after)
    return ToolSyncResult(tool=tool, status="COMPLETED", detail="version unavailable")


def _resolve_bun_executable() -> str | None:
    bun_from_path = shutil.which("bun")
    if bun_from_path is not None:
        return bun_from_path

    bun_home = Path(os.environ.get("BUN_INSTALL", Path.home() / ".bun"))
    fallback = bun_home / "bin" / "bun"
    if fallback.exists() and fallback.is_file():
        return str(fallback)
    return None


def _sync_uv() -> ToolSyncResult:
    before = _capture_version(["uv", "--version"]) if _command_exists("uv") else None

    try:
        result = _run_shell_pipeline("curl -LsSf https://astral.sh/uv/install.sh | sh")
    except subprocess.TimeoutExpired:
        return ToolSyncResult(
            tool="uv", status="FAILED", detail="install/update timed out"
        )

    if result.returncode != 0:
        return ToolSyncResult(
            tool="uv", status="FAILED", detail=_stderr_or_stdout(result)
        )

    after = _capture_version(["uv", "--version"]) or before
    return _result_from_versions(tool="uv", before=before, after=after)


def _sync_bun() -> ToolSyncResult:
    bun_executable = _resolve_bun_executable()
    before = (
        _capture_version([bun_executable, "--version"])
        if bun_executable is not None
        else None
    )

    try:
        if bun_executable is None:
            result = _run_shell_pipeline("curl -fsSL https://bun.sh/install | bash")
        else:
            result = _run_command([bun_executable, "upgrade"], timeout=300)
    except subprocess.TimeoutExpired:
        return ToolSyncResult(
            tool="bun", status="FAILED", detail="install/update timed out"
        )

    if result.returncode != 0:
        return ToolSyncResult(
            tool="bun", status="FAILED", detail=_stderr_or_stdout(result)
        )

    refreshed_bun = _resolve_bun_executable()
    after = (
        _capture_version([refreshed_bun, "--version"])
        if refreshed_bun is not None
        else before
    )
    return _result_from_versions(tool="bun", before=before, after=after)


def _sync_turbo() -> ToolSyncResult:
    bun_executable = _resolve_bun_executable()
    if bun_executable is None:
        return ToolSyncResult(tool="turbo", status="FAILED", detail="bun is required")

    before = (
        _capture_version(["turbo", "--version"]) if _command_exists("turbo") else None
    )
    try:
        result = _run_command([bun_executable, "add", "--global", "turbo"], timeout=300)
    except subprocess.TimeoutExpired:
        return ToolSyncResult(
            tool="turbo", status="FAILED", detail="install/update timed out"
        )

    if result.returncode != 0:
        return ToolSyncResult(
            tool="turbo", status="FAILED", detail=_stderr_or_stdout(result)
        )

    after = _capture_version(["turbo", "--version"]) or before
    return _result_from_versions(tool="turbo", before=before, after=after)


def _sync_opencode() -> ToolSyncResult:
    before = (
        _capture_version(["opencode", "--version"])
        if _command_exists("opencode")
        else None
    )
    try:
        result = _run_shell_pipeline("curl -fsSL https://opencode.ai/install | bash")
    except subprocess.TimeoutExpired:
        return ToolSyncResult(
            tool="opencode", status="FAILED", detail="install/update timed out"
        )

    if result.returncode != 0:
        return ToolSyncResult(
            tool="opencode", status="FAILED", detail=_stderr_or_stdout(result)
        )

    after = _capture_version(["opencode", "--version"]) or before
    return _result_from_versions(tool="opencode", before=before, after=after)


def _sync_btca() -> ToolSyncResult:
    bun_executable = _resolve_bun_executable()
    if bun_executable is None:
        return ToolSyncResult(tool="btca", status="FAILED", detail="bun is required")

    before = (
        _capture_version(["btca", "--version"]) if _command_exists("btca") else None
    )
    try:
        result = _run_command([bun_executable, "add", "--global", "btca"], timeout=300)
    except subprocess.TimeoutExpired:
        return ToolSyncResult(
            tool="btca", status="FAILED", detail="install/update timed out"
        )

    if result.returncode != 0:
        return ToolSyncResult(
            tool="btca", status="FAILED", detail=_stderr_or_stdout(result)
        )

    after = _capture_version(["btca", "--version"]) or before
    return _result_from_versions(tool="btca", before=before, after=after)


def _linux_distro_id() -> str:
    os_release = Path("/etc/os-release")
    if not os_release.exists() or not os_release.is_file():
        return "unknown"

    for line in os_release.read_text(encoding="utf-8").splitlines():
        if line.startswith("ID="):
            value = line.split("=", maxsplit=1)[1].strip().strip('"')
            return value.lower() if value else "unknown"
    return "unknown"


def _sync_ripgrep() -> ToolSyncResult:
    current = _capture_first_version_token(["rg", "--version"])
    if current is not None:
        return ToolSyncResult(tool="ripgrep", status="UP-TO-DATE", detail=current)

    os_name = system()
    install_command: list[str] | None = None

    if os_name == "Darwin":
        if _command_exists("brew"):
            install_command = ["brew", "install", "ripgrep"]
        else:
            return ToolSyncResult(
                tool="ripgrep",
                status="FAILED",
                detail="homebrew not found",
            )
    elif os_name == "Linux":
        distro = _linux_distro_id()
        if distro in {"ubuntu", "debian"}:
            install_command = ["sudo", "apt", "install", "-y", "ripgrep"]
        elif distro in {"fedora", "rhel", "centos"}:
            install_command = ["sudo", "dnf", "install", "-y", "ripgrep"]
        elif distro in {"arch", "manjaro"}:
            install_command = ["sudo", "pacman", "-Sy", "--noconfirm", "ripgrep"]
        elif distro.startswith("opensuse") or distro == "suse":
            install_command = ["sudo", "zypper", "install", "-y", "ripgrep"]
        else:
            return ToolSyncResult(tool="ripgrep", status="UNSUPPORTED", detail=distro)
    elif os_name == "Windows":
        if _command_exists("winget"):
            install_command = [
                "winget",
                "install",
                "BurntSushi.ripgrep.MSVC",
                "--silent",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ]
        else:
            return ToolSyncResult(
                tool="ripgrep", status="UNSUPPORTED", detail="winget not found"
            )
    else:
        return ToolSyncResult(tool="ripgrep", status="UNSUPPORTED", detail=os_name)

    try:
        result = _run_command(install_command, timeout=600)
    except subprocess.TimeoutExpired:
        return ToolSyncResult(
            tool="ripgrep", status="FAILED", detail="install timed out"
        )

    if result.returncode != 0:
        return ToolSyncResult(
            tool="ripgrep", status="FAILED", detail=_stderr_or_stdout(result)
        )

    updated = _capture_first_version_token(["rg", "--version"])
    if updated is not None:
        return ToolSyncResult(tool="ripgrep", status="INSTALLED", detail=updated)
    return ToolSyncResult(
        tool="ripgrep", status="COMPLETED", detail="installed, version unavailable"
    )


def run_tools_sync(
    *, dry_run: bool, cwd: Path | None = None, use_tui: bool = False
) -> int:
    if dry_run:
        print("DRY RUN: sync tools plan (native Python implementation)")
        summary = run_tool_sync(dry_run=True, cwd=cwd)
        for result in summary.results:
            print(f"- {result.tool}: {result.status} ({result.detail})")
        return 0

    if use_tui:
        return run_tool_sync_tui(cwd=cwd)

    print("Running nurt sync tools (native Python implementation)...")
    summary = run_tool_sync(dry_run=False, cwd=cwd)
    for result in summary.results:
        print(f"- {result.tool}: {result.status} ({result.detail})")
    return 0 if summary.succeeded else 1


def _validate_template_sync_root(project_root: Path) -> None:
    try:
        validate_nurt_repo_root(cwd=project_root.resolve())
    except ValueError as exc:
        detail = str(exc).replace(
            "nurt add",
            "nurt sync template-assets",
        )
        raise RuntimeError(detail) from exc


def _ensure_git_clean(project_root: Path) -> None:
    result = _run_command(["git", "status", "--porcelain"], cwd=project_root)
    if result.returncode != 0:
        raise RuntimeError("git status failed while validating clean working tree")
    if result.stdout.strip() != "":
        raise RuntimeError(
            "repository has uncommitted changes; commit or stash before sync template-assets"
        )


def _write_template_text(template_relative_path: str, destination: Path) -> None:
    template_text = load_template_text(template_relative_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(template_text, encoding="utf-8")


def _apply_template_sync(project_root: Path) -> tuple[str, ...]:
    copied_files: list[str] = []
    for (
        destination_relative,
        template_relative,
    ) in get_foundation_sync_template_file_pairs():
        _write_template_text(template_relative, project_root / destination_relative)
        copied_files.append(destination_relative)
    return tuple(copied_files)


def run_template_assets_sync(*, dry_run: bool, project_root: Path) -> int:
    try:
        sync_pairs = get_foundation_sync_template_file_pairs()
    except ValueError as exc:
        print(f"Error: sync template-assets failed: {exc}")
        return 1

    if dry_run:
        print("DRY RUN: sync template-assets (manifest-derived native implementation)")
        print(
            "DRY RUN: bundled snapshot assets shipped with the installed nurt version"
        )
        print(
            "DRY RUN: real runs validate `.nurt/repo.json` at the repo root and require a clean git working tree"
        )
        print("DRY RUN: manifest-derived sync plan:")
        for destination_relative, _template_relative in sync_pairs:
            print(f"  - {destination_relative}")
        return 0

    try:
        _validate_template_sync_root(project_root)
        _ensure_git_clean(project_root)
    except RuntimeError as exc:
        print(f"Error: {exc}")
        return 1

    try:
        copied_files = _apply_template_sync(project_root)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: sync template-assets failed: {exc}")
        return 1

    print(
        "Sync template-assets completed "
        f"({len(copied_files)} managed files refreshed from bundled snapshot assets)."
    )
    return 0
