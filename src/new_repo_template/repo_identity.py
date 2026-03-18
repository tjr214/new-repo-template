from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_MARKER_RELATIVE_PATH = Path(".nurt") / "repo.json"
REPO_MARKER_SCHEMA_VERSION = 1
REPO_MARKER_TOOL = "nurt"


def render_repo_marker() -> str:
    return (
        json.dumps(
            {
                "schema_version": REPO_MARKER_SCHEMA_VERSION,
                "tool": REPO_MARKER_TOOL,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def write_repo_marker(*, output_root: Path) -> None:
    marker_path = output_root / REPO_MARKER_RELATIVE_PATH
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(render_repo_marker(), encoding="utf-8")


def _detect_git_toplevel(cwd: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except FileNotFoundError, subprocess.TimeoutExpired:
        return None

    if result.returncode != 0:
        return None

    resolved = result.stdout.strip()
    if resolved == "":
        return None
    return Path(resolved).resolve()


def validate_nurt_repo_root(*, cwd: Path) -> Path:
    repo_root = cwd.resolve()
    git_toplevel = _detect_git_toplevel(repo_root)

    if git_toplevel is not None and git_toplevel != repo_root:
        raise ValueError(
            "nurt add must run from the root of a nurt-generated repository; "
            f"current directory is not the git repo root ({git_toplevel})"
        )

    marker_path = repo_root / REPO_MARKER_RELATIVE_PATH
    if not marker_path.exists() or not marker_path.is_file():
        raise ValueError(
            "nurt add must run from the root of a nurt-generated repository; "
            f"expected marker `{REPO_MARKER_RELATIVE_PATH.as_posix()}` at {repo_root}"
        )

    try:
        payload = json.loads(marker_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid nurt repo marker at `{REPO_MARKER_RELATIVE_PATH.as_posix()}`"
        ) from exc

    if not isinstance(payload, dict):
        raise ValueError(
            f"invalid nurt repo marker at `{REPO_MARKER_RELATIVE_PATH.as_posix()}`"
        )

    if payload.get("tool") != REPO_MARKER_TOOL:
        raise ValueError(
            f"unsupported nurt repo marker at `{REPO_MARKER_RELATIVE_PATH.as_posix()}`"
        )

    if payload.get("schema_version") != REPO_MARKER_SCHEMA_VERSION:
        raise ValueError(
            "unsupported nurt repo marker schema_version at "
            f"`{REPO_MARKER_RELATIVE_PATH.as_posix()}`"
        )

    return repo_root
