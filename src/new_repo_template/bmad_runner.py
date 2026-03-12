from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


BMAD_INSTALL_COMMAND: tuple[str, ...] = ("npx", "bmad-method@latest", "install")


def run_bmad_sync(*, project_root: Path, dry_run: bool) -> int:
    if dry_run:
        print(
            "DRY RUN: would execute `npx bmad-method@latest install` "
            f"in `{project_root}`"
        )
        return 0

    if shutil.which("npx") is None:
        print("Error: npx is required to install or update the BMAD Method.")
        return 1

    print(f"Launching BMAD Method installer in `{project_root}`...")
    try:
        result = subprocess.run(
            list(BMAD_INSTALL_COMMAND),
            cwd=project_root,
            check=False,
        )
    except FileNotFoundError:
        print("Error: npx is required to install or update the BMAD Method.")
        return 1

    if result.returncode != 0:
        print(
            f"Error: BMAD Method install/update failed with exit code {result.returncode}."
        )
        return result.returncode or 1

    print("BMAD Method install/update completed successfully.")
    return 0
