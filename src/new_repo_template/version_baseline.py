from __future__ import annotations

import json
import re
import shlex
import subprocess
from hashlib import sha256
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SCHEMA_VERSION = 1
MANAGED_TOOL_ORDER: tuple[str, ...] = ("bun", "turbo", "typescript", "python")
NPM_PACKAGES: dict[str, str] = {
    "bun": "bun",
    "turbo": "turbo",
    "typescript": "typescript",
}
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


@dataclass(frozen=True)
class VersionDiff:
    tool: str
    current: str
    latest: str


@dataclass(frozen=True)
class LockfileTarget:
    lockfile_path: Path
    command: tuple[str, ...]
    working_directory: Path
    display_path: str


@dataclass(frozen=True)
class LockfileRunResult:
    lockfile_name: str
    status: str
    detail: str
    failed: bool


def _http_get_json(url: str) -> object:
    request = Request(url, headers={"User-Agent": "nurt-version-baseline/1.0"})
    with urlopen(request, timeout=15) as response:  # noqa: S310 - known static URLs
        return json.load(response)


def _is_valid_version(value: object) -> bool:
    return isinstance(value, str) and bool(VERSION_PATTERN.match(value))


def _version_key(version: str) -> tuple[int, int, int]:
    major, minor, patch = version.split(".")
    return int(major), int(minor), int(patch)


def _validate_latest_source(source: object) -> dict[str, str]:
    if not isinstance(source, dict):
        raise ValueError("latest-version source must be a JSON object")

    versions: dict[str, str] = {}
    missing: list[str] = []
    invalid: list[str] = []

    for tool in MANAGED_TOOL_ORDER:
        value = source.get(tool)
        if value is None:
            missing.append(tool)
            continue
        if not _is_valid_version(value):
            invalid.append(tool)
            continue
        versions[tool] = value

    if missing:
        raise ValueError(
            "latest-version source missing required tools: " + ", ".join(missing)
        )
    if invalid:
        raise ValueError(
            "latest-version source has invalid versions for: " + ", ".join(invalid)
        )
    return versions


def _load_latest_from_source_file(source_file: Path) -> dict[str, str]:
    try:
        payload = json.loads(source_file.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(
            f"latest-version source file not found: {source_file}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"latest-version source file is not valid JSON: {source_file}"
        ) from exc

    return _validate_latest_source(payload)


def _fetch_latest_npm_version(package: str) -> str:
    payload = _http_get_json(f"https://registry.npmjs.org/{package}/latest")
    if not isinstance(payload, dict) or not _is_valid_version(payload.get("version")):
        raise ValueError(f"invalid npm latest payload for package: {package}")
    version = payload["version"]
    assert isinstance(version, str)
    return version


def _fetch_latest_python_version() -> str:
    payload = _http_get_json("https://endoflife.date/api/python.json")
    if not isinstance(payload, list):
        raise ValueError("invalid python latest payload")

    candidates: list[str] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        latest = item.get("latest")
        if _is_valid_version(latest):
            assert isinstance(latest, str)
            candidates.append(latest)

    if not candidates:
        raise ValueError("no valid python release candidates available")

    return max(candidates, key=_version_key)


def resolve_latest_versions(*, source_file: Path | None) -> dict[str, str]:
    if source_file is not None:
        return _load_latest_from_source_file(source_file)

    return {
        "bun": _fetch_latest_npm_version(NPM_PACKAGES["bun"]),
        "turbo": _fetch_latest_npm_version(NPM_PACKAGES["turbo"]),
        "typescript": _fetch_latest_npm_version(NPM_PACKAGES["typescript"]),
        "python": _fetch_latest_python_version(),
    }


def load_baseline(path: Path) -> dict[str, object]:
    try:
        baseline = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"baseline metadata file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"baseline metadata is not valid JSON: {path}") from exc

    if not isinstance(baseline, dict):
        raise ValueError("baseline metadata root must be a JSON object")

    if baseline.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"baseline metadata schema_version must be {SCHEMA_VERSION}")

    managed_tools = baseline.get("managed_tools")
    if not isinstance(managed_tools, dict):
        raise ValueError("baseline metadata must include object field 'managed_tools'")

    missing: list[str] = []
    invalid: list[str] = []
    for tool in MANAGED_TOOL_ORDER:
        tool_data = managed_tools.get(tool)
        if not isinstance(tool_data, dict):
            missing.append(tool)
            continue
        version = tool_data.get("version")
        if not _is_valid_version(version):
            invalid.append(tool)

    if missing:
        raise ValueError("baseline metadata missing tools: " + ", ".join(missing))
    if invalid:
        raise ValueError(
            "baseline metadata contains invalid tool versions for: "
            + ", ".join(invalid)
        )

    return baseline


def _baseline_versions(baseline: dict[str, object]) -> dict[str, str]:
    managed_tools = baseline["managed_tools"]
    assert isinstance(managed_tools, dict)
    versions: dict[str, str] = {}
    for tool in MANAGED_TOOL_ORDER:
        tool_data = managed_tools[tool]
        assert isinstance(tool_data, dict)
        version = tool_data["version"]
        assert isinstance(version, str)
        versions[tool] = version
    return versions


def _collect_diffs(
    *, current: dict[str, str], latest: dict[str, str]
) -> list[VersionDiff]:
    diffs: list[VersionDiff] = []
    for tool in MANAGED_TOOL_ORDER:
        current_version = current[tool]
        latest_version = latest[tool]
        if current_version == latest_version:
            continue
        diffs.append(
            VersionDiff(tool=tool, current=current_version, latest=latest_version)
        )
    return diffs


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _write_baseline(path: Path, baseline: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(baseline, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _resolve_lockfile_targets(*, project_root: Path) -> list[LockfileTarget]:
    targets: list[LockfileTarget] = []

    if (project_root / "pyproject.toml").exists():
        targets.append(
            LockfileTarget(
                lockfile_path=project_root / "uv.lock",
                command=("uv", "lock"),
                working_directory=project_root,
                display_path="uv.lock",
            )
        )

    python_lane_root = project_root / "apps" / "python"
    if (python_lane_root / "pyproject.toml").exists():
        targets.append(
            LockfileTarget(
                lockfile_path=python_lane_root / "uv.lock",
                command=("uv", "lock"),
                working_directory=python_lane_root,
                display_path="apps/python/uv.lock",
            )
        )

    if (project_root / "package.json").exists():
        targets.append(
            LockfileTarget(
                lockfile_path=project_root / "bun.lock",
                command=(
                    "bun",
                    "install",
                    "--save-text-lockfile",
                    "--frozen-lockfile",
                    "--lockfile-only",
                ),
                working_directory=project_root,
                display_path="bun.lock",
            )
        )

    return targets


def _digest_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None

    digest = sha256()
    with path.open("rb") as file_handle:
        while True:
            chunk = file_handle.read(65536)
            if chunk == b"":
                break
            digest.update(chunk)
    return digest.hexdigest()


def _display_command(command: tuple[str, ...]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def _execute_lockfile_target(
    *, target: LockfileTarget, dry_run: bool
) -> LockfileRunResult:
    lockfile_name = target.display_path
    command_display = _display_command(target.command)

    before_digest = _digest_file(target.lockfile_path)
    if dry_run:
        return LockfileRunResult(
            lockfile_name=lockfile_name,
            status="planned",
            detail=f"would run `{command_display}`",
            failed=False,
        )

    try:
        result = subprocess.run(
            list(target.command),
            cwd=target.working_directory,
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
    except FileNotFoundError:
        return LockfileRunResult(
            lockfile_name=lockfile_name,
            status="failed",
            detail=f"required command not found for `{command_display}`",
            failed=True,
        )
    except subprocess.TimeoutExpired:
        return LockfileRunResult(
            lockfile_name=lockfile_name,
            status="failed",
            detail=f"command timed out for `{command_display}`",
            failed=True,
        )

    if result.returncode != 0:
        output = result.stderr.strip() or result.stdout.strip() or "command failed"
        detail = output.replace("\n", " | ")
        return LockfileRunResult(
            lockfile_name=lockfile_name,
            status="failed",
            detail=f"{command_display}: {detail}",
            failed=True,
        )

    after_digest = _digest_file(target.lockfile_path)
    if after_digest is None:
        return LockfileRunResult(
            lockfile_name=lockfile_name,
            status="failed",
            detail=f"lockfile not generated by `{command_display}`",
            failed=True,
        )

    if before_digest is None:
        return LockfileRunResult(
            lockfile_name=lockfile_name,
            status="created",
            detail=f"generated via `{command_display}`",
            failed=False,
        )

    if before_digest != after_digest:
        return LockfileRunResult(
            lockfile_name=lockfile_name,
            status="updated",
            detail=f"regenerated via `{command_display}`",
            failed=False,
        )

    return LockfileRunResult(
        lockfile_name=lockfile_name,
        status="unchanged",
        detail=f"revalidated via `{command_display}`",
        failed=False,
    )


def _run_lockfile_regeneration(*, project_root: Path, dry_run: bool) -> int:
    targets = _resolve_lockfile_targets(project_root=project_root)
    if not targets:
        print("No lockfile targets detected for project root.")
        return 0

    if dry_run:
        print("DRY RUN: lockfile regeneration plan")
    else:
        print("Lockfile regeneration summary:")

    had_failures = False
    for target in targets:
        result = _execute_lockfile_target(
            target=target,
            dry_run=dry_run,
        )
        print(f"- {result.lockfile_name}: {result.status} ({result.detail})")
        if result.failed:
            had_failures = True

    return 1 if had_failures else 0


def _check_lockfiles(*, project_root: Path) -> int:
    targets = _resolve_lockfile_targets(project_root=project_root)
    if not targets:
        print("No lockfile targets detected for project root.")
        return 0

    missing = [
        target.display_path
        for target in targets
        if not target.lockfile_path.exists() or not target.lockfile_path.is_file()
    ]
    if missing:
        print("Missing required lockfiles:")
        for lockfile in missing:
            print(f"- {lockfile}")
        return 1

    print("Required lockfiles are present.")
    return 0


def run_versions_check(
    *,
    baseline_path: Path,
    check_latest: bool,
    source_file: Path | None,
    check_lockfiles: bool,
    project_root: Path,
) -> int:
    try:
        baseline = load_baseline(baseline_path)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    print("Version baseline metadata is valid.")

    status = 0

    if check_lockfiles:
        status = max(status, _check_lockfiles(project_root=project_root))

    if not check_latest:
        return status

    try:
        latest_versions = resolve_latest_versions(source_file=source_file)
    except (ValueError, HTTPError, URLError, TimeoutError) as exc:
        print(f"Error: unable to resolve latest versions: {exc}")
        return 1

    diffs = _collect_diffs(
        current=_baseline_versions(baseline),
        latest=latest_versions,
    )
    if not diffs:
        print("Version baseline is up to date.")
        return status

    print("Version baseline is out of date:")
    for diff in diffs:
        print(f"- {diff.tool}: current={diff.current} latest={diff.latest}")
    return 1


def run_versions_update(
    *,
    baseline_path: Path,
    dry_run: bool,
    source_file: Path | None,
    project_root: Path,
    regenerate_lockfiles: bool,
) -> int:
    try:
        baseline = load_baseline(baseline_path)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    try:
        latest_versions = resolve_latest_versions(source_file=source_file)
    except (ValueError, HTTPError, URLError, TimeoutError) as exc:
        print(f"Error: unable to resolve latest versions: {exc}")
        return 1

    current_versions = _baseline_versions(baseline)
    diffs = _collect_diffs(current=current_versions, latest=latest_versions)
    if dry_run:
        print("DRY RUN: version baseline update plan")
    elif diffs:
        print("Updated version baseline metadata:")
    else:
        print("Version baseline already up to date.")

    for diff in diffs:
        print(f"- {diff.tool}: {diff.current} -> {diff.latest}")

    if not dry_run and diffs:
        managed_tools = baseline["managed_tools"]
        assert isinstance(managed_tools, dict)
        for tool in MANAGED_TOOL_ORDER:
            tool_data = managed_tools[tool]
            assert isinstance(tool_data, dict)
            tool_data["version"] = latest_versions[tool]

        baseline["generated_at"] = _now_iso()
        _write_baseline(baseline_path, baseline)

    if not regenerate_lockfiles:
        return 0

    return _run_lockfile_regeneration(project_root=project_root, dry_run=dry_run)


def generate_project_lockfiles(*, project_root: Path) -> int:
    return _run_lockfile_regeneration(project_root=project_root, dry_run=False)
