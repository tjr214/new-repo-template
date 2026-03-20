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


def test_typescript_cli_scaffold_writes_bun_native_cli_baseline(tmp_path: Path) -> None:
    """TypeScript CLI target should scaffold a runnable Bun-native CLI app."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "typescript-cli"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "typescript-cli",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected typescript-cli scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    cli_root = output_dir / "apps" / "typescript-cli" / "typescript-cli"
    expected_paths = (
        cli_root / "package.json",
        cli_root / "README.md",
        cli_root / "tsconfig.json",
        cli_root / ".env.example",
        cli_root / "src" / "cli.ts",
        cli_root / "src" / "index.ts",
        cli_root / "smoke.test.ts",
    )
    for path in expected_paths:
        assert path.exists(), f"Expected scaffolded TypeScript CLI file: {path}"

    manifest = json.loads((cli_root / "package.json").read_text(encoding="utf-8"))
    assert manifest.get("name") == "@generated/typescript-cli"
    assert manifest.get("type") == "module"
    assert manifest.get("bin") == {"typescript-cli": "./src/cli.ts"}

    scripts = manifest.get("scripts")
    assert isinstance(scripts, dict)
    for script_name in ("dev", "start", "build", "test", "lint", "typecheck"):
        script_value = scripts.get(script_name)
        assert isinstance(script_value, str) and script_value != ""

    dev_dependencies = manifest.get("devDependencies")
    assert isinstance(dev_dependencies, dict)
    assert dev_dependencies.get("@generated/typescript-config") == "workspace:*"
    assert "typescript" in dev_dependencies

    tsconfig_text = (cli_root / "tsconfig.json").read_text(encoding="utf-8")
    assert '"@generated/typescript-config/node.json"' in tsconfig_text

    cli_text = (cli_root / "src" / "cli.ts").read_text(encoding="utf-8")
    assert cli_text.startswith("#!/usr/bin/env bun\n")
    assert "process.argv.slice(2)" in cli_text
    assert "Usage:" in cli_text

    readme_text = (cli_root / "README.md").read_text(encoding="utf-8")
    assert "bun install --frozen-lockfile" in readme_text
    assert "bun run dev -- --help" in readme_text
    assert "bun run build" in readme_text
    assert "bun run typecheck" in readme_text


def test_typescript_cli_dry_run_lists_cli_scaffold_paths(tmp_path: Path) -> None:
    """TypeScript CLI dry-run should list the new CLI scaffold files."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "typescript-cli-dry-run"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "typescript-cli",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected typescript-cli dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "apps/typescript-cli/typescript-cli/package.json" in combined_output
    assert "apps/typescript-cli/typescript-cli/README.md" in combined_output
    assert "apps/typescript-cli/typescript-cli/tsconfig.json" in combined_output
    assert "apps/typescript-cli/typescript-cli/src/cli.ts" in combined_output
    assert "apps/typescript-cli/typescript-cli/src/index.ts" in combined_output
    assert "apps/typescript-cli/typescript-cli/smoke.test.ts" in combined_output
    assert "apps/typescript-cli/typescript-cli/.env.example" in combined_output
