from __future__ import annotations

import os
import re
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from platform import system

from new_repo_template.version_baseline import (
    VersionDiff,
    apply_tool_versions_to_baseline,
)


SIMULATE_TOOLS_SYNC_FAILURE_ENV = "NURT_TOOLS_SYNC_SIMULATE_FAILURE"

ANSI_RESET = "\033[0m"
ANSI_RED = "\033[0;31m"
ANSI_BOLD_RED = "\033[1;31m"
ANSI_GREEN = "\033[0;32m"
ANSI_YELLOW = "\033[1;33m"
ANSI_BLUE = "\033[0;34m"
ANSI_CYAN = "\033[0;36m"
ANSI_DULL_YELLOW = "\033[2;33m"
ANSI_BOLD = "\033[1m"

ANSI_PATTERN = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")

LogCallback = Callable[[str], None]
UpdateCallback = Callable[["ToolSyncUpdate"], None]
TaskRunner = Callable[[LogCallback], "ToolSyncResult"]


@dataclass(frozen=True)
class ToolSyncResult:
    tool: str
    status: str
    detail: str


@dataclass(frozen=True)
class ToolSyncUpdate:
    tool: str
    status: str
    detail: str


@dataclass(frozen=True)
class ToolSyncTask:
    tool: str
    label: str
    dry_run_detail: str
    runner: TaskRunner


@dataclass(frozen=True)
class ToolSyncSummary:
    results: tuple[ToolSyncResult, ...]
    baseline_diffs: tuple[VersionDiff, ...] = ()

    @property
    def succeeded(self) -> bool:
        return not any(
            result.status in {"FAILED", "UNSUPPORTED"} for result in self.results
        )


@dataclass(frozen=True)
class _StreamedCommandResult:
    returncode: int
    output: str


SYNC_TOOLS_BASELINE_FILENAME = "version-baseline.json"
SYNC_TOOLS_BASELINE_MANAGED_TOOLS: tuple[str, ...] = ("bun", "turbo")


def _style(text: str, *styles: str) -> str:
    return f"{''.join(styles)}{text}{ANSI_RESET}"


def _plain_text(text: str) -> str:
    return ANSI_PATTERN.sub("", text)


def _log_header(log: LogCallback) -> None:
    log(_style("OpenCode Installation/Update Script", ANSI_CYAN, ANSI_BOLD))
    log(_style("=====================================", ANSI_CYAN))


def _log_separator(log: LogCallback) -> None:
    log("")
    log(
        _style(
            "-------------------------------------------------------------------------------",
            ANSI_DULL_YELLOW,
        )
    )


def _log_checking(log: LogCallback, label: str) -> None:
    log("")
    log(_style(f"Checking {label}...", ANSI_CYAN, ANSI_BOLD))


def _log_installed_version(
    log: LogCallback, tool_name: str, version: str | None
) -> None:
    if version:
        log(
            f"{ANSI_BLUE}{tool_name} is already installed {ANSI_RESET}"
            f"(Version: {ANSI_BOLD}{version}{ANSI_RESET})"
        )
        return
    log(_style(f"{tool_name} is already installed", ANSI_BLUE))


def _log_not_found(log: LogCallback, tool_name: str) -> None:
    log(_style(f"{tool_name} not found. Installing...", ANSI_YELLOW))


def _log_updating(log: LogCallback, tool_name: str) -> None:
    log(_style(f"Updating {tool_name}...", ANSI_YELLOW))


def _log_platform_action(log: LogCallback, action: str) -> None:
    log(_style(action, ANSI_YELLOW))


def _log_result(
    log: LogCallback,
    *,
    tool_name: str,
    before: str | None,
    after: str | None,
) -> None:
    if before is None:
        if after is not None:
            log(
                f"{ANSI_GREEN}{ANSI_BOLD}{tool_name} installed successfully!{ANSI_RESET} "
                f"(Version: {ANSI_BOLD}{after}{ANSI_RESET})"
            )
        else:
            log(_style(f"{tool_name} installed successfully!", ANSI_GREEN, ANSI_BOLD))
        return

    if after is not None and before == after:
        log(
            f"{ANSI_GREEN}{tool_name} is already up to date {ANSI_RESET}"
            f"(Version: {ANSI_BOLD}{after}{ANSI_RESET})"
        )
        return

    if after is not None:
        log(_style(f"{tool_name} updated successfully!", ANSI_GREEN, ANSI_BOLD))
        log(f"{ANSI_BLUE}Previous version: {ANSI_RESET}{before}")
        log(f"{ANSI_BLUE}Current version: {ANSI_RESET}{ANSI_BOLD}{after}{ANSI_RESET}")
        return

    log(
        _style(
            f"{tool_name} install/update completed successfully!", ANSI_GREEN, ANSI_BOLD
        )
    )


def _log_error(log: LogCallback, message: str) -> None:
    log(_style(f"Error: {message}", ANSI_RED, ANSI_BOLD))


def _log_warning(log: LogCallback, message: str) -> None:
    log(_style(message, ANSI_YELLOW))


def _is_truthy_env(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() not in {"", "0", "false", "no", "none"}


def _command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def _capture_version(command: list[str]) -> str | None:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except FileNotFoundError, subprocess.TimeoutExpired:
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


def _capture_gh_version() -> str | None:
    raw = _capture_version(["gh", "--version"])
    if raw is None:
        return None

    first_line = raw.splitlines()[0].strip()
    parts = first_line.split()
    if len(parts) < 3:
        return first_line or None
    return parts[2]


def _resolve_bun_executable() -> str | None:
    bun_from_path = shutil.which("bun")
    if bun_from_path is not None:
        return bun_from_path

    bun_home = Path(os.environ.get("BUN_INSTALL", Path.home() / ".bun"))
    fallback = bun_home / "bin" / "bun"
    if fallback.exists() and fallback.is_file():
        return str(fallback)
    return None


def _linux_distro_id() -> str:
    os_release = Path("/etc/os-release")
    if not os_release.exists() or not os_release.is_file():
        return "unknown"

    for line in os_release.read_text(encoding="utf-8").splitlines():
        if line.startswith("ID="):
            value = line.split("=", maxsplit=1)[1].strip().strip('"')
            return value.lower() if value else "unknown"
    return "unknown"


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


def _shell_command_args(command: str) -> list[str] | None:
    shell_path = shutil.which("bash")
    if shell_path is not None:
        return [shell_path, "-lc", command]

    shell_path = shutil.which("sh")
    if shell_path is not None:
        return [shell_path, "-c", command]

    return None


def _run_streamed_command(
    command: list[str],
    *,
    log: LogCallback,
    cwd: Path | None = None,
) -> _StreamedCommandResult:
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
    except FileNotFoundError:
        return _StreamedCommandResult(
            returncode=127,
            output=f"required command not found: {command[0]}",
        )

    lines: list[str] = []
    assert process.stdout is not None
    for raw_line in process.stdout:
        line = raw_line.rstrip("\n")
        if line != "":
            log(line)
        lines.append(line)

    return _StreamedCommandResult(
        returncode=process.wait(),
        output="\n".join(lines).strip(),
    )


def _run_streamed_shell(
    command: str,
    *,
    log: LogCallback,
    cwd: Path | None = None,
) -> _StreamedCommandResult:
    shell_command = _shell_command_args(command)
    if shell_command is None:
        return _StreamedCommandResult(returncode=127, output="no shell available")
    return _run_streamed_command(shell_command, log=log, cwd=cwd)


def _failed(tool: str, detail: str) -> ToolSyncResult:
    return ToolSyncResult(tool=tool, status="FAILED", detail=detail)


def _extract_updated_tool_versions(
    *, results: tuple[ToolSyncResult, ...], tools: tuple[str, ...]
) -> dict[str, str]:
    extracted: dict[str, str] = {}
    for result in results:
        if result.tool not in tools:
            continue
        if result.status == "INSTALLED":
            version = result.detail.strip()
        elif result.status == "UPDATED":
            _, separator, after = result.detail.partition(" -> ")
            version = after.strip() if separator else ""
        else:
            continue

        if version:
            extracted[result.tool] = version
    return extracted


def _refresh_version_baseline_from_results(
    *, results: tuple[ToolSyncResult, ...], cwd: Path | None, log: LogCallback
) -> tuple[VersionDiff, ...]:
    project_root = cwd.resolve() if cwd is not None else Path.cwd().resolve()
    baseline_path = project_root / SYNC_TOOLS_BASELINE_FILENAME
    if not baseline_path.exists() or not baseline_path.is_file():
        return ()

    tool_versions = _extract_updated_tool_versions(
        results=results,
        tools=SYNC_TOOLS_BASELINE_MANAGED_TOOLS,
    )
    if not tool_versions:
        return ()

    try:
        diffs = apply_tool_versions_to_baseline(
            baseline_path=baseline_path,
            tool_versions=tool_versions,
        )
    except ValueError as exc:
        log("")
        _log_warning(log, f"Unable to refresh version baseline metadata: {exc}")
        return ()

    if diffs:
        log("")
        log(
            _style(
                "Updated version baseline metadata from sync tools:",
                ANSI_CYAN,
                ANSI_BOLD,
            )
        )
        for diff in diffs:
            log(f"- {diff.tool}: {diff.current} -> {diff.latest}")

    return diffs


def _sync_uv(*, cwd: Path | None) -> TaskRunner:
    def runner(log: LogCallback) -> ToolSyncResult:
        tool_name = "uv"
        before = (
            _capture_version(["uv", "--version"]) if _command_exists("uv") else None
        )
        if before is not None:
            _log_installed_version(log, tool_name, before)
            _log_updating(log, tool_name)
        else:
            _log_not_found(log, tool_name)
        result = _run_streamed_shell(
            "curl -LsSf https://astral.sh/uv/install.sh | sh",
            log=log,
            cwd=cwd,
        )
        if result.returncode != 0:
            _log_error(log, "uv installation/update failed")
            return _failed("uv", result.output or "install/update failed")
        after = _capture_version(["uv", "--version"]) or before
        _log_result(log, tool_name=tool_name, before=before, after=after)
        return _result_from_versions(tool="uv", before=before, after=after)

    return runner


def _sync_bun(*, cwd: Path | None) -> TaskRunner:
    def runner(log: LogCallback) -> ToolSyncResult:
        tool_name = "bun"
        bun_executable = _resolve_bun_executable()
        before = (
            _capture_version([bun_executable, "--version"])
            if bun_executable is not None
            else None
        )
        if before is not None:
            _log_installed_version(log, tool_name, before)
            _log_updating(log, tool_name)
        else:
            _log_not_found(log, tool_name)

        if bun_executable is None:
            result = _run_streamed_shell(
                "curl -fsSL https://bun.sh/install | bash",
                log=log,
                cwd=cwd,
            )
        else:
            result = _run_streamed_command(
                [bun_executable, "upgrade"],
                log=log,
                cwd=cwd,
            )

        if result.returncode != 0:
            _log_error(log, "bun installation/update failed")
            return _failed("bun", result.output or "install/update failed")

        refreshed_bun = _resolve_bun_executable()
        after = (
            _capture_version([refreshed_bun, "--version"])
            if refreshed_bun is not None
            else before
        )
        _log_result(log, tool_name=tool_name, before=before, after=after)
        if bun_executable is None and after is None:
            _log_warning(
                log,
                "bun installed, but it is not yet available in PATH for this shell.",
            )
        return _result_from_versions(tool="bun", before=before, after=after)

    return runner


def _sync_turbo(*, cwd: Path | None) -> TaskRunner:
    def runner(log: LogCallback) -> ToolSyncResult:
        tool_name = "turborepo"
        bun_executable = _resolve_bun_executable()
        if bun_executable is None:
            _log_error(log, "bun is required to install/update turborepo.")
            return _failed("turbo", "bun is required")

        before = (
            _capture_version(["turbo", "--version"])
            if _command_exists("turbo")
            else None
        )
        if before is not None:
            _log_installed_version(log, tool_name, before)
            _log_updating(log, tool_name)
        else:
            _log_not_found(log, tool_name)
        result = _run_streamed_command(
            [bun_executable, "add", "--global", "turbo"],
            log=log,
            cwd=cwd,
        )
        if result.returncode != 0:
            _log_error(log, "turborepo installation/update failed")
            return _failed("turbo", result.output or "install/update failed")
        after = _capture_version(["turbo", "--version"]) or before
        _log_result(log, tool_name=tool_name, before=before, after=after)
        return _result_from_versions(tool="turbo", before=before, after=after)

    return runner


def _sync_opencode(*, cwd: Path | None) -> TaskRunner:
    def runner(log: LogCallback) -> ToolSyncResult:
        tool_name = "OpenCode"
        cache_path = (
            Path.home()
            / ".cache"
            / "opencode"
            / "node_modules"
            / "opencode-antigravity-auth"
        )
        shutil.rmtree(cache_path, ignore_errors=True)

        before = (
            _capture_version(["opencode", "--version"])
            if _command_exists("opencode")
            else None
        )
        if before is not None:
            _log_installed_version(log, tool_name, before)
            _log_updating(log, tool_name)
        else:
            _log_not_found(log, tool_name)
        if before is not None:
            result = _run_streamed_command(["opencode", "upgrade"], log=log, cwd=cwd)
        else:
            result = _run_streamed_shell(
                "curl -fsSL https://opencode.ai/install | bash",
                log=log,
                cwd=cwd,
            )

        if result.returncode != 0:
            _log_error(log, "OpenCode installation/update failed")
            return _failed("opencode", result.output or "install/update failed")

        after = _capture_version(["opencode", "--version"]) or before
        _log_result(log, tool_name=tool_name, before=before, after=after)
        return _result_from_versions(tool="opencode", before=before, after=after)

    return runner


def _sync_btca(*, cwd: Path | None) -> TaskRunner:
    def runner(log: LogCallback) -> ToolSyncResult:
        tool_name = "btca"
        bun_executable = _resolve_bun_executable()
        if bun_executable is None:
            _log_error(log, "bun is required to install/update btca.")
            return _failed("btca", "bun is required")

        before = (
            _capture_version(["btca", "--version"]) if _command_exists("btca") else None
        )
        if before is not None:
            _log_installed_version(log, tool_name, before)
            _log_updating(log, tool_name)
        else:
            _log_not_found(log, tool_name)
        result = _run_streamed_command(
            [bun_executable, "add", "--global", "btca"],
            log=log,
            cwd=cwd,
        )
        if result.returncode != 0:
            _log_error(log, "btca installation/update failed")
            return _failed("btca", result.output or "install/update failed")
        after = _capture_version(["btca", "--version"]) or before
        _log_result(log, tool_name=tool_name, before=before, after=after)
        return _result_from_versions(tool="btca", before=before, after=after)

    return runner


def _sync_gh(*, cwd: Path | None) -> TaskRunner:
    def runner(log: LogCallback) -> ToolSyncResult:
        tool_name = "gh"
        before = _capture_gh_version() if _command_exists("gh") else None
        os_name = system()

        if before is not None:
            _log_installed_version(log, tool_name, before)
            _log_platform_action(log, "Checking for updates...")
        else:
            _log_not_found(log, tool_name)

        if os_name == "Darwin":
            if not _command_exists("brew"):
                _log_error(
                    log,
                    "Homebrew not found. Please install Homebrew first: https://brew.sh",
                )
                return _failed("gh", "homebrew not found")
            commands = [["brew", "install", "gh"]]
            if before is not None:
                commands.insert(0, ["brew", "upgrade", "gh"])
        elif os_name == "Linux":
            distro = _linux_distro_id()
            if distro in {"ubuntu", "debian"}:
                commands = [
                    _shell_command_args("sudo apt update && sudo apt install -y gh")
                ]
            elif distro in {"fedora", "rhel", "centos"}:
                commands = [["sudo", "dnf", "install", "-y", "gh"]]
            elif distro in {"arch", "manjaro"}:
                commands = [["sudo", "pacman", "-Sy", "--noconfirm", "github-cli"]]
            elif distro.startswith("opensuse") or distro == "suse":
                commands = [["sudo", "zypper", "install", "-y", "gh"]]
            else:
                _log_warning(log, f"Unsupported Linux distribution: {distro}")
                _log_warning(
                    log, "Please install gh manually from: https://cli.github.com/"
                )
                return ToolSyncResult(tool="gh", status="UNSUPPORTED", detail=distro)
        elif os_name == "Windows":
            if not _command_exists("winget"):
                _log_warning(log, "Unsupported environment: winget not found")
                return ToolSyncResult(
                    tool="gh", status="UNSUPPORTED", detail="winget not found"
                )
            commands = [
                [
                    "winget",
                    "install",
                    "GitHub.cli",
                    "--silent",
                    "--accept-package-agreements",
                    "--accept-source-agreements",
                ]
            ]
        else:
            _log_warning(log, f"Unsupported operating system: {os_name}")
            return ToolSyncResult(tool="gh", status="UNSUPPORTED", detail=os_name)

        if any(command is None for command in commands):
            _log_error(log, "No shell available to install or update gh")
            return _failed("gh", "no shell available")
        final_result: _StreamedCommandResult | None = None
        for index, command in enumerate(commands):
            assert command is not None
            final_result = _run_streamed_command(command, log=log, cwd=cwd)
            if final_result.returncode == 0:
                break
            if index == len(commands) - 1:
                _log_error(log, "gh installation/update failed")
                return _failed("gh", final_result.output or "install/update failed")

        after = _capture_gh_version() or before
        _log_result(log, tool_name=tool_name, before=before, after=after)
        return _result_from_versions(tool="gh", before=before, after=after)

    return runner


def _sync_ripgrep(*, cwd: Path | None) -> TaskRunner:
    def runner(log: LogCallback) -> ToolSyncResult:
        tool_name = "ripgrep"
        before = _capture_first_version_token(["rg", "--version"])
        os_name = system()

        if before is not None:
            _log_installed_version(log, tool_name, before)
            _log_platform_action(log, "Checking for updates...")
        else:
            _log_not_found(log, tool_name)

        if os_name == "Darwin":
            if not _command_exists("brew"):
                _log_error(
                    log,
                    "Homebrew not found. Please install Homebrew first: https://brew.sh",
                )
                return _failed("ripgrep", "homebrew not found")
            commands = [["brew", "install", "ripgrep"]]
            if before is not None:
                commands.insert(0, ["brew", "upgrade", "ripgrep"])
        elif os_name == "Linux":
            distro = _linux_distro_id()
            if distro in {"ubuntu", "debian"}:
                commands = [
                    _shell_command_args(
                        "sudo apt update && sudo apt install -y ripgrep"
                    )
                ]
            elif distro in {"fedora", "rhel", "centos"}:
                commands = [["sudo", "dnf", "install", "-y", "ripgrep"]]
            elif distro in {"arch", "manjaro"}:
                commands = [["sudo", "pacman", "-Sy", "--noconfirm", "ripgrep"]]
            elif distro.startswith("opensuse") or distro == "suse":
                commands = [["sudo", "zypper", "install", "-y", "ripgrep"]]
            else:
                _log_warning(log, f"Unsupported Linux distribution: {distro}")
                _log_warning(
                    log,
                    "Please install ripgrep manually from: https://github.com/BurntSushi/ripgrep",
                )
                return ToolSyncResult(
                    tool="ripgrep", status="UNSUPPORTED", detail=distro
                )
        elif os_name == "Windows":
            if not _command_exists("winget"):
                _log_warning(log, "Unsupported environment: winget not found")
                return ToolSyncResult(
                    tool="ripgrep", status="UNSUPPORTED", detail="winget not found"
                )
            commands = [
                [
                    "winget",
                    "install",
                    "BurntSushi.ripgrep.MSVC",
                    "--silent",
                    "--accept-package-agreements",
                    "--accept-source-agreements",
                ]
            ]
        else:
            _log_warning(log, f"Unsupported operating system: {os_name}")
            return ToolSyncResult(tool="ripgrep", status="UNSUPPORTED", detail=os_name)

        if any(command is None for command in commands):
            _log_error(log, "No shell available to install or update ripgrep")
            return _failed("ripgrep", "no shell available")
        final_result: _StreamedCommandResult | None = None
        for index, command in enumerate(commands):
            assert command is not None
            final_result = _run_streamed_command(command, log=log, cwd=cwd)
            if final_result.returncode == 0:
                break
            if index == len(commands) - 1:
                _log_error(log, "ripgrep installation/update failed")
                return _failed(
                    "ripgrep", final_result.output or "install/update failed"
                )

        after = _capture_first_version_token(["rg", "--version"]) or before
        _log_result(log, tool_name=tool_name, before=before, after=after)
        return _result_from_versions(tool="ripgrep", before=before, after=after)

    return runner


def default_tool_tasks(*, cwd: Path | None = None) -> tuple[ToolSyncTask, ...]:
    return (
        ToolSyncTask(
            tool="uv",
            label="uv",
            dry_run_detail="would install/update via astral installer",
            runner=_sync_uv(cwd=cwd),
        ),
        ToolSyncTask(
            tool="bun",
            label="bun",
            dry_run_detail="would install/update via bun installer",
            runner=_sync_bun(cwd=cwd),
        ),
        ToolSyncTask(
            tool="turbo",
            label="turborepo",
            dry_run_detail="would install/update via bun add --global turbo",
            runner=_sync_turbo(cwd=cwd),
        ),
        ToolSyncTask(
            tool="opencode",
            label="OpenCode",
            dry_run_detail="would install via curl or upgrade via opencode upgrade",
            runner=_sync_opencode(cwd=cwd),
        ),
        ToolSyncTask(
            tool="btca",
            label="btca",
            dry_run_detail="would install/update via bun add --global btca",
            runner=_sync_btca(cwd=cwd),
        ),
        ToolSyncTask(
            tool="gh",
            label="GitHub CLI (gh)",
            dry_run_detail="would install/update via platform package manager",
            runner=_sync_gh(cwd=cwd),
        ),
        ToolSyncTask(
            tool="ripgrep",
            label="ripgrep",
            dry_run_detail="would install/update via platform package manager",
            runner=_sync_ripgrep(cwd=cwd),
        ),
    )


def run_tool_sync(
    *,
    dry_run: bool,
    tasks: tuple[ToolSyncTask, ...] | None = None,
    on_update: UpdateCallback | None = None,
    on_log: LogCallback | None = None,
    cwd: Path | None = None,
) -> ToolSyncSummary:
    resolved_tasks = tasks or default_tool_tasks(cwd=cwd)

    def emit_update(update: ToolSyncUpdate) -> None:
        if on_update is not None:
            on_update(update)

    def emit_log(line: str) -> None:
        if on_log is not None:
            on_log(line)

    if dry_run:
        dry_run_results = tuple(
            ToolSyncResult(
                tool=task.tool,
                status="DRY-RUN",
                detail=task.dry_run_detail,
            )
            for task in resolved_tasks
        )
        for result in dry_run_results:
            emit_update(
                ToolSyncUpdate(
                    tool=result.tool,
                    status=result.status,
                    detail=result.detail,
                )
            )
        return ToolSyncSummary(results=dry_run_results)

    if _is_truthy_env(os.environ.get(SIMULATE_TOOLS_SYNC_FAILURE_ENV)):
        simulated_results = tuple(
            ToolSyncResult(tool=task.tool, status="FAILED", detail="simulated failure")
            for task in resolved_tasks
        )
        for result in simulated_results:
            emit_update(
                ToolSyncUpdate(
                    tool=result.tool,
                    status=result.status,
                    detail=result.detail,
                )
            )
        return ToolSyncSummary(results=simulated_results)

    results: list[ToolSyncResult] = []
    _log_header(emit_log)
    for index, task in enumerate(resolved_tasks):
        if index:
            _log_separator(emit_log)
        _log_checking(emit_log, task.label)
        emit_update(ToolSyncUpdate(tool=task.tool, status="RUNNING", detail=task.label))
        result = task.runner(emit_log)
        results.append(result)
        emit_update(
            ToolSyncUpdate(
                tool=result.tool,
                status=result.status,
                detail=result.detail,
            )
        )

    result_tuple = tuple(results)
    baseline_diffs = _refresh_version_baseline_from_results(
        results=result_tuple,
        cwd=cwd,
        log=emit_log,
    )
    summary = ToolSyncSummary(
        results=result_tuple,
        baseline_diffs=baseline_diffs,
    )
    emit_log("")
    if summary.succeeded:
        emit_log(_style("Done.", ANSI_GREEN))
    else:
        failed_tools = ", ".join(
            result.tool
            for result in summary.results
            if result.status in {"FAILED", "UNSUPPORTED"}
        )
        emit_log(_style("Done with errors.", ANSI_YELLOW, ANSI_BOLD))
        if failed_tools:
            emit_log(
                f"{ANSI_YELLOW}Failed components: {ANSI_BOLD}{failed_tools}{ANSI_RESET}"
            )

    return summary
