from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from platform import system


TEMPLATE_REPO_HTTPS = "https://github.com/tjr214/new-repo-template.git"
TEMPLATE_REPO_SSH = "git@github.com:tjr214/new-repo-template.git"


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


def run_tools_sync(*, dry_run: bool) -> int:
    if dry_run:
        print("DRY RUN: tool sync plan (native Python implementation)")
        print("  - uv: install/update via astral installer")
        print("  - bun: install/update via bun installer")
        print("  - turbo: install/update via `bun add --global turbo`")
        print("  - opencode: install/update via opencode installer")
        print("  - btca: install/update via `bun add --global btca`")
        print("  - ripgrep: install/update via platform package manager")
        return 0

    print("Running tool sync (native Python implementation)...")
    results = [
        _sync_uv(),
        _sync_bun(),
        _sync_turbo(),
        _sync_opencode(),
        _sync_btca(),
        _sync_ripgrep(),
    ]

    for result in results:
        print(f"- {result.tool}: {result.status} ({result.detail})")

    has_failures = any(result.status in {"FAILED", "UNSUPPORTED"} for result in results)
    return 1 if has_failures else 0


def _validate_template_sync_root(project_root: Path) -> None:
    if (
        not (project_root / ".opencode").is_dir()
        or not (project_root / ".template_scripts").is_dir()
    ):
        raise RuntimeError(
            "template-assets sync must run from project root containing .opencode/ and .template_scripts/"
        )


def _ensure_git_clean(project_root: Path) -> None:
    result = _run_command(["git", "status", "--porcelain"], cwd=project_root)
    if result.returncode != 0:
        raise RuntimeError("git status failed while validating clean working tree")
    if result.stdout.strip() != "":
        raise RuntimeError(
            "repository has uncommitted changes; commit or stash before template-assets sync"
        )


def _clone_template_repo(project_root: Path, clone_dir: Path) -> None:
    https_result = _run_command(
        ["git", "clone", TEMPLATE_REPO_HTTPS, str(clone_dir)], cwd=project_root
    )
    if https_result.returncode == 0:
        return

    ssh_result = _run_command(
        ["git", "clone", TEMPLATE_REPO_SSH, str(clone_dir)], cwd=project_root
    )
    if ssh_result.returncode == 0:
        return

    details = (
        f"https clone failed: {_stderr_or_stdout(https_result)}; "
        f"ssh clone failed: {_stderr_or_stdout(ssh_result)}"
    )
    raise RuntimeError(details)


def _copy_file(source: Path, destination: Path) -> None:
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"missing template file: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _replace_directory(source: Path, destination: Path) -> None:
    if not source.exists() or not source.is_dir():
        raise FileNotFoundError(f"missing template directory: {source}")
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def _copy_globbed_files(source_root: Path, pattern: str, destination_root: Path) -> int:
    if not source_root.exists() or not source_root.is_dir():
        raise FileNotFoundError(f"missing template directory: {source_root}")

    copied = 0
    for file_path in sorted(source_root.glob(pattern)):
        if not file_path.is_file():
            continue
        _copy_file(file_path, destination_root / file_path.name)
        copied += 1
    return copied


def _copy_directory_contents(source_root: Path, destination_root: Path) -> int:
    if not source_root.exists() or not source_root.is_dir():
        raise FileNotFoundError(f"missing template directory: {source_root}")

    copied = 0
    for file_path in sorted(source_root.rglob("*")):
        if not file_path.is_file():
            continue
        relative = file_path.relative_to(source_root)
        _copy_file(file_path, destination_root / relative)
        copied += 1
    return copied


def _apply_template_sync(clone_root: Path, project_root: Path) -> None:
    _copy_file(
        clone_root / ".claude" / "settings.json",
        project_root / ".claude" / "settings.json",
    )
    _copy_file(
        clone_root / ".claude" / "statusline-script.sh",
        project_root / ".claude" / "statusline-script.sh",
    )
    _replace_directory(
        clone_root / ".claude" / "commands" / "repo",
        project_root / ".claude" / "commands" / "repo",
    )
    _copy_file(clone_root / "AGENTS.md", project_root / "AGENTS.md")
    _copy_file(clone_root / "CLAUDE.md", project_root / "CLAUDE.md")

    template_scripts_dir = clone_root / ".template_scripts"
    if not template_scripts_dir.exists() or not template_scripts_dir.is_dir():
        raise FileNotFoundError(f"missing template directory: {template_scripts_dir}")
    for script in sorted(template_scripts_dir.glob("*")):
        if script.is_file():
            _copy_file(script, project_root / ".template_scripts" / script.name)

    _copy_globbed_files(
        clone_root / ".opencode" / "command",
        "*.md",
        project_root / ".opencode" / "command",
    )
    _copy_globbed_files(
        clone_root / ".agent" / "workflows" / "project",
        "*.md",
        project_root / ".agent" / "workflows" / "project",
    )
    _copy_globbed_files(
        clone_root / ".agent" / "rules",
        "*.md",
        project_root / ".agent" / "rules",
    )

    (project_root / "docs" / "tasks").mkdir(parents=True, exist_ok=True)
    _copy_file(
        clone_root / "docs" / "tasks" / "task-template.yaml",
        project_root / "docs" / "tasks" / "task-template.yaml",
    )
    _copy_file(
        clone_root / "docs" / "tasks" / "task-template-example.yaml",
        project_root / "docs" / "tasks" / "task-template-example.yaml",
    )

    _copy_directory_contents(
        clone_root / "docs" / "workflows", project_root / "docs" / "workflows"
    )


def run_template_assets_sync(*, dry_run: bool, project_root: Path) -> int:
    if dry_run:
        print("DRY RUN: template-assets sync (native Python implementation)")
        print(f"DRY RUN: template source repo: {TEMPLATE_REPO_HTTPS}")
        print(f"DRY RUN: template source fallback: {TEMPLATE_REPO_SSH}")
        print("DRY RUN: would verify project root markers and clean git status")
        print("DRY RUN: would clone template repository and copy managed assets")
        return 0

    try:
        _validate_template_sync_root(project_root)
        _ensure_git_clean(project_root)
    except RuntimeError as exc:
        print(f"Error: {exc}")
        return 1

    with tempfile.TemporaryDirectory(prefix="nurt-template-sync-") as temp_dir:
        clone_dir = Path(temp_dir) / "nr"
        try:
            _clone_template_repo(project_root, clone_dir)
            _apply_template_sync(clone_dir, project_root)
        except (RuntimeError, FileNotFoundError) as exc:
            print(f"Error: template-assets sync failed: {exc}")
            return 1

    print("Template assets sync completed.")
    return 0
