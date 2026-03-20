from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_scaffold_command(
    *, repo_root: Path, args: list[str]
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")
    return subprocess.run(
        [sys.executable, "-m", "new_repo_template.scaffold", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_typescript_lib_scaffold_writes_publishable_library_baseline(
    tmp_path: Path,
) -> None:
    """TypeScript library target should scaffold a reusable package under packages/typescript."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "typescript-lib"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "typescript-lib",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected typescript-lib scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    library_root = output_dir / "packages" / "typescript" / "typescript-lib"
    expected_paths = (
        library_root / "package.json",
        library_root / "README.md",
        library_root / "tsconfig.json",
        library_root / "src" / "index.ts",
        library_root / "tests" / "typescript_lib.test.ts",
    )
    for path in expected_paths:
        assert path.exists(), f"Expected scaffolded TypeScript library file: {path}"

    manifest = json.loads((library_root / "package.json").read_text(encoding="utf-8"))
    assert manifest.get("name") == "@generated/typescript-lib"
    assert manifest.get("type") == "module"
    assert manifest.get("exports") == {".": "./dist/index.js"}
    assert manifest.get("types") == "./dist/index.d.ts"
    assert manifest.get("files") == ["dist"]
    assert manifest.get("private") is not True

    scripts = manifest.get("scripts")
    assert isinstance(scripts, dict)
    for script_name in ("build", "test", "lint", "typecheck"):
        assert isinstance(scripts.get(script_name), str) and scripts[script_name] != ""

    dev_dependencies = manifest.get("devDependencies")
    assert isinstance(dev_dependencies, dict)
    assert dev_dependencies.get("@generated/typescript-config") == "workspace:*"
    assert "typescript" in dev_dependencies

    tsconfig_text = (library_root / "tsconfig.json").read_text(encoding="utf-8")
    assert '"@generated/typescript-config/node.json"' in tsconfig_text
    assert '"outDir": "./dist"' in tsconfig_text


def test_typescript_lib_dry_run_lists_library_scaffold_paths(tmp_path: Path) -> None:
    """TypeScript library dry-run should list the new library scaffold files."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "typescript-lib-dry-run"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "typescript-lib",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected typescript-lib dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "packages/typescript/typescript-lib/package.json" in combined_output
    assert "packages/typescript/typescript-lib/README.md" in combined_output
    assert "packages/typescript/typescript-lib/tsconfig.json" in combined_output
    assert "packages/typescript/typescript-lib/src/index.ts" in combined_output
    assert (
        "packages/typescript/typescript-lib/tests/typescript_lib.test.ts"
        in combined_output
    )
