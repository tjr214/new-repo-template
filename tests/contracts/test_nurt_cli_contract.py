from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from new_repo_template import nurt_cli
from new_repo_template.repo_identity import render_repo_marker
from new_repo_template.snapshot_assets_loader import load_source_manifest


def _combined_output(result: subprocess.CompletedProcess[str]) -> str:
    return f"{result.stdout}\n{result.stderr}"


def _assert_scaffold_plan(
    output: str,
    *,
    targets: tuple[str, ...],
    auth: str | None = None,
    output_path: Path | None = None,
) -> None:
    assert "Resolved scaffold plan:" in output
    assert f"- project types: {', '.join(targets)}" in output
    assert f"- auth: {auth if auth is not None else 'none'}" in output
    if output_path is not None:
        assert f"- output: {output_path}" in output


def _assert_project_entries(output: str, *, projects: tuple[str, ...]) -> None:
    for project in projects:
        assert f"  - {project}" in output


def _assert_post_create_plan(
    output: str, *, install_bmad: bool, install_core_tools: bool
) -> None:
    assert "Post-create automation plan:" in output
    assert f"- BMAD Method: {'yes' if install_bmad else 'no'}" in output
    assert f"- Core tools updater: {'yes' if install_core_tools else 'no'}" in output
    assert "- lifecycle:" in output


def run_nurt_command(
    *,
    cwd: Path,
    args: list[str],
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    command_env = os.environ.copy()
    repo_root = Path(__file__).resolve().parents[2]
    command_env["PYTHONPATH"] = str(repo_root / "src")
    command_env.setdefault("NURT_UPDATE_CHECK_SIMULATE", "none")
    if env is not None:
        command_env.update(env)

    return subprocess.run(
        [sys.executable, "-m", "new_repo_template.nurt_cli", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        input=input_text,
        env=command_env,
        check=False,
    )


def test_nurt_new_dry_run_generates_scaffold_plan_without_writing(
    tmp_path: Path,
) -> None:
    """RED: nurt new dry-run should route into scaffold plan generation."""

    output_dir = tmp_path / "demo-web-backend"
    result = run_nurt_command(
        cwd=tmp_path,
        args=[
            "new",
            output_dir.name,
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "clerk",
            "--dry-run",
            "--install-core-tools",
            "--install-bmad",
        ],
    )

    assert result.returncode == 0, (
        "Expected nurt new --dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    _assert_scaffold_plan(
        combined_output,
        targets=("web", "backend"),
        auth="clerk",
        output_path=output_dir,
    )
    _assert_post_create_plan(
        combined_output,
        install_bmad=True,
        install_core_tools=True,
    )
    assert not output_dir.exists(), "dry-run should not create project directory"


def test_nurt_new_defaults_to_foundation_when_targets_omitted(tmp_path: Path) -> None:
    """RED: nurt new should default to foundation in non-interactive mode."""

    output_dir = tmp_path / "demo-foundation"
    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", output_dir.name, "--dry-run", "--no-interactive"],
    )

    assert result.returncode == 0, (
        "Expected default nurt new dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    _assert_scaffold_plan(
        combined_output,
        targets=("foundation",),
        auth="none",
        output_path=output_dir,
    )
    assert not output_dir.exists(), "dry-run should not create project directory"


def test_nurt_new_dry_run_supports_typescript_cli_target(tmp_path: Path) -> None:
    """nurt new should route the new typescript-cli target through scaffold dry-run."""

    output_dir = tmp_path / "demo-typescript-cli"
    result = run_nurt_command(
        cwd=tmp_path,
        args=[
            "new",
            output_dir.name,
            "--target",
            "typescript-cli",
            "--dry-run",
            "--no-interactive",
        ],
    )

    assert result.returncode == 0, (
        "Expected typescript-cli nurt new dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    _assert_scaffold_plan(
        combined_output,
        targets=("typescript-cli",),
        auth="none",
        output_path=output_dir,
    )
    assert not output_dir.exists(), "dry-run should not create project directory"


def test_nurt_new_dry_run_supports_library_targets(tmp_path: Path) -> None:
    """nurt new should route the new library targets through scaffold dry-run."""

    output_dir = tmp_path / "demo-libraries"
    result = run_nurt_command(
        cwd=tmp_path,
        args=[
            "new",
            output_dir.name,
            "--target",
            "python-lib",
            "--target",
            "typescript-lib",
            "--dry-run",
            "--no-interactive",
        ],
    )

    assert result.returncode == 0, (
        "Expected library-target nurt new dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    _assert_scaffold_plan(
        combined_output,
        targets=("python-lib", "typescript-lib"),
        auth="none",
        output_path=output_dir,
    )
    assert not output_dir.exists(), "dry-run should not create project directory"


def test_nurt_new_dry_run_supports_named_project_specs(tmp_path: Path) -> None:
    """nurt new should route repeatable --project specs through scaffold dry-run."""

    output_dir = tmp_path / "demo-named-projects"
    result = run_nurt_command(
        cwd=tmp_path,
        args=[
            "new",
            output_dir.name,
            "--project",
            "python:api",
            "--project",
            "python:worker",
            "--project",
            "typescript-lib:sdk",
            "--dry-run",
            "--no-interactive",
        ],
    )

    assert result.returncode == 0, (
        "Expected named-project nurt new dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "- project types: python, python, typescript-lib" in combined_output
    _assert_project_entries(
        combined_output,
        projects=("python:api", "python:worker", "typescript-lib:sdk"),
    )
    assert not output_dir.exists(), "dry-run should not create project directory"


def test_nurt_new_plain_interactive_collects_multiple_names_per_type(
    tmp_path: Path,
) -> None:
    """Plain interactive mode should collect multiple named projects for a selected type."""

    output_dir = tmp_path / "demo-multi-name-input"
    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", output_dir.name, "--dry-run"],
        input_text="2,9\napi,worker\nsdk\n\n\n",
        env={"NURT_UI_MODE": "plain"},
    )

    assert result.returncode == 0, (
        "Expected plain interactive multi-name flow to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    _assert_project_entries(
        combined_output,
        projects=("python:api", "python:worker", "python-lib:sdk"),
    )
    assert not output_dir.exists(), "dry-run should not create project directory"


def test_nurt_new_interactive_wizard_resolves_web_backend_with_prompted_auth(
    tmp_path: Path,
) -> None:
    """Interactive wizard should resolve targets and auth without explicit flags."""

    output_dir = tmp_path / "demo-interactive"
    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", output_dir.name, "--dry-run"],
        input_text="3,4\n\n\n2\n\n\n",
    )

    assert result.returncode == 0, (
        "Expected interactive nurt new dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "nurt new interactive mode" in combined_output
    _assert_scaffold_plan(
        combined_output,
        targets=("web", "backend"),
        auth="better-auth",
        output_path=output_dir,
    )
    _assert_post_create_plan(
        combined_output,
        install_bmad=True,
        install_core_tools=False,
    )
    assert not output_dir.exists(), "dry-run should not create project directory"


def test_nurt_new_without_project_name_prompts_and_normalizes_directory(
    tmp_path: Path,
) -> None:
    """Interactive flow should collect and normalize the project name when omitted."""

    output_dir = tmp_path / "my-cool-app"
    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", "--dry-run"],
        input_text="My Cool App\n4\n\n3\n\n\n",
    )

    assert result.returncode == 0, (
        "Expected nurt new without a project name to succeed interactively.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    _assert_scaffold_plan(
        combined_output,
        targets=("backend",),
        auth="none",
        output_path=output_dir,
    )
    _assert_post_create_plan(
        combined_output,
        install_bmad=True,
        install_core_tools=False,
    )
    assert not output_dir.exists(), "dry-run should not create project directory"


def test_nurt_new_interactive_rich_mode_falls_back_when_unavailable(
    tmp_path: Path,
) -> None:
    """Rich/Textual mode should fall back cleanly when rich UI is unavailable."""

    output_dir = tmp_path / "demo-rich-fallback"
    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", output_dir.name, "--dry-run"],
        input_text="3,4\n\n\n2\n\n\n",
        env={
            "NURT_UI_MODE": "rich",
            "NURT_SIMULATE_RICH_UNAVAILABLE": "1",
        },
    )

    assert result.returncode == 0, (
        "Expected rich-mode fallback interactive command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "Rich/Textual UI unavailable" in combined_output
    assert "nurt new interactive mode" in combined_output
    _assert_scaffold_plan(
        combined_output,
        targets=("web", "backend"),
        auth="better-auth",
        output_path=output_dir,
    )


def test_nurt_new_interactive_rich_mode_falls_back_without_tty(tmp_path: Path) -> None:
    """Explicit rich mode should fall back cleanly when no interactive TTY exists."""

    output_dir = tmp_path / "demo-rich-no-tty"
    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", output_dir.name, "--dry-run"],
        input_text="3,4\n\n\n1\n\n\n",
        env={"NURT_UI_MODE": "rich"},
    )

    assert result.returncode == 0, (
        "Expected explicit rich-mode fallback to succeed without a TTY.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "requires an interactive terminal" in combined_output
    assert "nurt new interactive mode" in combined_output
    _assert_scaffold_plan(
        combined_output,
        targets=("web", "backend"),
        auth="clerk",
        output_path=output_dir,
    )


def test_nurt_new_interactive_plain_ui_mode_has_no_rich_warning(tmp_path: Path) -> None:
    """Plain UI mode should avoid rich fallback warnings and still work."""

    output_dir = tmp_path / "demo-plain-ui"
    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", output_dir.name, "--dry-run"],
        input_text="3,4\n\n\n1\n\n\n",
        env={"NURT_UI_MODE": "plain", "NURT_SIMULATE_RICH_UNAVAILABLE": "1"},
    )

    assert result.returncode == 0, (
        "Expected plain UI interactive command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "nurt new interactive mode" in combined_output
    assert "Rich/Textual UI unavailable" not in combined_output
    _assert_scaffold_plan(
        combined_output,
        targets=("web", "backend"),
        auth="clerk",
        output_path=output_dir,
    )


def test_nurt_new_interactive_without_stdin_fails_with_clear_remediation(
    tmp_path: Path,
) -> None:
    """Interactive mode should fail cleanly when stdin is unavailable."""

    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", "demo-no-stdin", "--dry-run"],
        input_text="",
    )

    assert result.returncode == 1, (
        "Expected interactive command to fail cleanly when stdin is unavailable.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "interactive input unavailable" in combined_output
    assert "--no-interactive" in combined_output
    assert "--target" in combined_output


def test_nurt_new_interactive_auth_prompt_without_stdin_fails_with_remediation(
    tmp_path: Path,
) -> None:
    """Auth prompt should fail cleanly when stdin closes before auth selection."""

    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", "demo-auth-no-stdin", "--dry-run"],
        input_text="4\n\n",
    )

    assert result.returncode == 1, (
        "Expected auth prompt to fail cleanly when stdin closes early.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "interactive input unavailable" in combined_output
    assert "--no-interactive" in combined_output
    assert "--auth" in combined_output


def test_handle_new_reports_friendly_cancel_message(
    monkeypatch, capsys, tmp_path: Path
) -> None:
    """Rich wizard cancellation should use the friendly cancellation copy."""

    monkeypatch.setattr(
        nurt_cli,
        "resolve_ui_config",
        lambda: nurt_cli.InteractiveUIConfig(mode="rich", use_rich=True, warning=None),
    )
    monkeypatch.setattr(nurt_cli, "run_interactive_wizard", lambda **_: None)

    exit_code = nurt_cli.handle_new(
        argparse.Namespace(
            project_name="demo-friendly-cancel",
            target=None,
            auth=None,
            install_core_tools=None,
            install_bmad=None,
            no_interactive=False,
            dry_run=True,
        )
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Interactive wizzard cancelled. Maybe next time!" in captured.err
    assert "Error:" not in captured.err


def test_handle_new_prints_completion_overview_with_cd_instruction(
    monkeypatch, capsys, tmp_path: Path
) -> None:
    """Successful nurt new runs should tell the user how to enter the new project."""

    project_root = tmp_path / "demo-ready"
    project_root.mkdir()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        nurt_cli,
        "resolve_ui_config",
        lambda: nurt_cli.InteractiveUIConfig(
            mode="plain", use_rich=False, warning=None
        ),
    )
    monkeypatch.setattr(nurt_cli.scaffold, "main", lambda _args: 0)
    monkeypatch.setattr(nurt_cli, "run_post_create_pipeline", lambda **_: 0)
    monkeypatch.setattr(
        nurt_cli,
        "render_completion_overview",
        lambda **_: (
            "Setup Complete\nNext step: change into the new project directory\ncd demo-ready"
        ),
    )

    exit_code = nurt_cli.handle_new(
        argparse.Namespace(
            project_name="demo-ready",
            target=None,
            auth=None,
            install_core_tools=None,
            install_bmad=None,
            no_interactive=True,
            dry_run=False,
        )
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Setup Complete" in captured.out
    assert "Next step: change into the new project directory" in captured.out
    assert "cd demo-ready" in captured.out


def test_nurt_add_dry_run_routes_through_add_planning(tmp_path: Path) -> None:
    """nurt add dry-run should report an add plan for an existing nurt repo."""

    repo_root = Path(__file__).resolve().parents[2]
    generated_repo = tmp_path / "generated-repo"
    scaffold_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "new_repo_template.scaffold",
            "--target",
            "foundation",
            "--no-interactive",
            "--output",
            str(generated_repo),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        check=False,
    )
    assert scaffold_result.returncode == 0, (
        "Expected foundation scaffold fixture to succeed for nurt add planning.\n"
        f"stdout:\n{scaffold_result.stdout}\n"
        f"stderr:\n{scaffold_result.stderr}"
    )

    result = run_nurt_command(
        cwd=generated_repo,
        args=["add", "--target", "desktop", "--dry-run", "--no-interactive"],
    )

    assert result.returncode == 0, (
        "Expected nurt add --dry-run to succeed in a generated repo.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "Resolved add plan:" in combined_output
    assert "- repo root:" in combined_output
    assert "- requested additions:" in combined_output
    assert "desktop:desktop" in combined_output
    assert "Lockfile regeneration summary:" not in combined_output


def test_nurt_add_rejects_foundation_target(tmp_path: Path) -> None:
    """nurt add should reject the non-addable foundation target."""

    repo_root = Path(__file__).resolve().parents[2]
    generated_repo = tmp_path / "generated-repo"
    scaffold_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "new_repo_template.scaffold",
            "--target",
            "foundation",
            "--no-interactive",
            "--output",
            str(generated_repo),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        check=False,
    )
    assert scaffold_result.returncode == 0

    result = run_nurt_command(
        cwd=generated_repo,
        args=["add", "--target", "foundation", "--dry-run", "--no-interactive"],
    )

    assert result.returncode != 0
    combined_output = _combined_output(result)
    assert "foundation" in combined_output
    assert "invalid choice" in combined_output or "not addable" in combined_output


def test_nurt_add_fails_outside_nurt_repo(tmp_path: Path) -> None:
    """nurt add should fail clearly when no nurt repo marker is present."""

    result = run_nurt_command(
        cwd=tmp_path,
        args=["add", "--target", "desktop", "--dry-run", "--no-interactive"],
    )

    assert result.returncode == 1
    combined_output = _combined_output(result)
    assert ".nurt/repo.json" in combined_output
    assert (
        "nurt add must run from the root of a nurt-generated repository"
        in combined_output
    )


def test_nurt_upgrade_dry_run_prints_upgrade_command(tmp_path: Path) -> None:
    """RED: nurt upgrade dry-run should be non-destructive and explicit."""

    result = run_nurt_command(cwd=tmp_path, args=["upgrade", "--dry-run"])

    assert result.returncode == 0, (
        "Expected nurt upgrade --dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "DRY RUN" in combined_output
    assert "uv tool upgrade" in combined_output
    assert "nurt-ai" in combined_output
    assert "nurt sync template-assets" not in combined_output


def test_nurt_update_is_no_longer_a_supported_command(tmp_path: Path) -> None:
    """Feature 7.0 removes the old `nurt update` command surface entirely."""

    result = run_nurt_command(cwd=tmp_path, args=["update", "--dry-run"])

    assert result.returncode != 0
    combined_output = _combined_output(result)
    assert "invalid choice" in combined_output
    assert "upgrade" in combined_output


def test_nurt_startup_update_check_notice_appears_when_update_available(
    tmp_path: Path,
) -> None:
    """RED: every nurt invocation should run update-check and notify when update exists."""

    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", "demo-update-notice", "--dry-run", "--no-interactive"],
        env={"NURT_UPDATE_CHECK_SIMULATE": "9.9.9"},
    )

    assert result.returncode == 0, (
        "Expected nurt command to succeed with simulated update notice.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert "Update available for nurt: 9.9.9" in result.stderr
    assert "Run `nurt upgrade`." in result.stderr


def test_perform_startup_update_check_uses_outdated_tool_listing(
    monkeypatch, capsys
) -> None:
    """Startup notices should use uv's non-mutating outdated-tool listing."""

    recorded_command: list[str] | None = None

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        nonlocal recorded_command
        recorded_command = command
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="nurt-ai v0.2.0\n- nurt\n",
            stderr="",
        )

    monkeypatch.delenv("NURT_UPDATE_CHECK_SIMULATE", raising=False)
    monkeypatch.setattr(nurt_cli.subprocess, "run", fake_run)

    nurt_cli.perform_startup_update_check()

    captured = capsys.readouterr()
    assert recorded_command == ["uv", "tool", "list", "--outdated"]
    assert "Run `nurt upgrade`." in captured.err


def test_handle_upgrade_runs_uv_tool_upgrade_for_distribution_name(
    monkeypatch, capsys
) -> None:
    """The CLI command should upgrade the installed uv tool by distribution name."""

    recorded_command: list[str] | None = None

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        nonlocal recorded_command
        recorded_command = command
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="Nothing to upgrade\n",
            stderr="",
        )

    monkeypatch.setattr(nurt_cli.subprocess, "run", fake_run)

    exit_code = nurt_cli.handle_upgrade(argparse.Namespace(dry_run=False))

    captured = capsys.readouterr()
    assert exit_code == 0
    assert recorded_command == ["uv", "tool", "upgrade", "nurt-ai"]
    assert "Nothing to upgrade" in captured.out


def test_handle_upgrade_reports_missing_uv(monkeypatch, capsys) -> None:
    """A missing uv executable should fail with clear remediation."""

    def missing_uv(
        *_args: object, **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError

    monkeypatch.setattr(nurt_cli.subprocess, "run", missing_uv)

    exit_code = nurt_cli.handle_upgrade(argparse.Namespace(dry_run=False))

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "uv is required to upgrade nurt" in captured.err


def test_nurt_ralph_command_routes_to_tui_when_no_subcommand(monkeypatch) -> None:
    """`nurt ralph` should open the fullscreen TUI entrypoint."""

    called: dict[str, bool] = {"tui": False}

    def fake_run_ralph_tui(*, project_root: Path) -> int:
        called["tui"] = True
        assert project_root == Path.cwd().resolve()
        return 0

    monkeypatch.setattr(nurt_cli, "run_ralph_tui", fake_run_ralph_tui)
    monkeypatch.setattr(nurt_cli, "perform_startup_update_check", lambda: None)

    exit_code = nurt_cli.main(["ralph"])

    assert exit_code == 0
    assert called["tui"] is True


def test_nurt_ralph_run_dry_run_reports_framework_agent_and_limits(
    tmp_path: Path,
) -> None:
    """The native Ralph run command should expose the resolved execution plan."""

    repo_root = tmp_path / "repo"
    docs_tasks = repo_root / "docs" / "tasks"
    docs_tasks.mkdir(parents=True)

    source_schema = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "tasks"
        / "task-template-schema.json"
    )
    (docs_tasks / "task-template-schema.json").write_text(
        source_schema.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (repo_root / "ralph.config.yaml").write_text(
        """default_model: openai/gpt-5.4\nmax_loops: 12\nmodels:\n  - id: openai/gpt-5.4\n    label: GPT-5.4\n""",
        encoding="utf-8",
    )
    task_path = docs_tasks / "standalone.yaml"
    task_path.write_text(
        """metadata:\n  version: \"1.1.0\"\n  created_date: \"2026-03-24\"\n  last_updated: \"2026-03-24\"\n  author: \"test\"\n  license: null\n  framework: \"standalone\"\ntask:\n  name: \"Standalone Task\"\n  description: \"Demo\"\n  status: \"pending\"\n  phases:\n    - id: \"phase-1\"\n      name: \"Phase\"\n      description: \"Demo\"\n      status: \"pending\"\n      steps:\n        - id: \"step-1.1\"\n          name: \"Step\"\n          description: \"Demo\"\n          status: \"pending\"\n          instructions:\n            - id: \"instr-1.1.1\"\n              content: \"Demo\"\n              status: \"pending\"\n""",
        encoding="utf-8",
    )

    result = run_nurt_command(
        cwd=repo_root,
        args=["ralph", "run", str(task_path), "--dry-run", "--no-interactive"],
    )

    assert result.returncode == 0, (
        "Expected nurt ralph run --dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "RALPH execution plan" in combined_output
    assert "Framework: standalone" in combined_output
    assert "Agent: build" in combined_output
    assert "BMAD Closeout: disabled" in combined_output
    assert "Max Loops: 12" in combined_output


def test_nurt_ralph_validate_and_visualize_use_native_commands(tmp_path: Path) -> None:
    """The native Ralph utility commands should replace the legacy scripts."""

    repo_root = tmp_path / "repo"
    docs_tasks = repo_root / "docs" / "tasks"
    docs_tasks.mkdir(parents=True)

    source_schema = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "tasks"
        / "task-template-schema.json"
    )
    (docs_tasks / "task-template-schema.json").write_text(
        source_schema.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    task_path = docs_tasks / "bmad.yaml"
    task_path.write_text(
        """metadata:\n  version: \"1.1.0\"\n  created_date: \"2026-03-24\"\n  last_updated: \"2026-03-24\"\n  author: \"test\"\n  license: null\n  framework: \"bmad\"\ntask:\n  name: \"BMAD Task\"\n  description: \"Demo\"\n  status: \"pending\"\n  phases:\n    - id: \"phase-1\"\n      name: \"Phase\"\n      description: \"Demo\"\n      status: \"pending\"\n      steps:\n        - id: \"step-1.1\"\n          name: \"Step\"\n          description: \"Demo\"\n          status: \"pending\"\n          instructions:\n            - id: \"instr-1.1.1\"\n              content: \"Demo\"\n              status: \"pending\"\n""",
        encoding="utf-8",
    )

    validate_result = run_nurt_command(
        cwd=repo_root,
        args=["ralph", "validate", str(task_path)],
    )
    assert validate_result.returncode == 0, (
        "Expected nurt ralph validate to succeed.\n"
        f"stdout:\n{validate_result.stdout}\n"
        f"stderr:\n{validate_result.stderr}"
    )
    assert "Template is VALID!" in _combined_output(validate_result)

    visualize_result = run_nurt_command(
        cwd=repo_root,
        args=["ralph", "visualize", str(task_path)],
    )
    assert visualize_result.returncode == 0, (
        "Expected nurt ralph visualize to succeed.\n"
        f"stdout:\n{visualize_result.stdout}\n"
        f"stderr:\n{visualize_result.stderr}"
    )
    combined_visualize = _combined_output(visualize_result)
    assert "TASK IMPLEMENTATION PLAN - STATUS SUMMARY" in combined_visualize
    assert "BMAD Task" in combined_visualize


def test_nurt_template_assets_sync_dry_run_reports_action(tmp_path: Path) -> None:
    """RED: sync template-assets dry-run should report non-destructive action plan."""

    result = run_nurt_command(
        cwd=tmp_path, args=["sync", "template-assets", "--dry-run"]
    )

    assert result.returncode == 0, (
        "Expected nurt sync template-assets --dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "DRY RUN" in combined_output
    assert "sync template-assets" in combined_output
    assert "manifest-derived sync plan" in combined_output
    assert "bundled snapshot assets" in combined_output
    assert "AGENTS.md" in combined_output
    assert "README.BMAD-GUIDE.md" in combined_output
    assert "docs/workflows/export-to-ralph/workflow.md" in combined_output
    assert "update-template-from-git.sh" not in combined_output
    assert "template source repo" not in combined_output


def test_nurt_tools_sync_dry_run_reports_action(tmp_path: Path) -> None:
    """RED: sync tools dry-run should report non-destructive action plan."""

    result = run_nurt_command(cwd=tmp_path, args=["sync", "tools", "--dry-run"])

    assert result.returncode == 0, (
        "Expected nurt sync tools --dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "DRY RUN" in combined_output
    assert "sync tools plan" in combined_output
    assert "uv" in combined_output
    assert "bun" in combined_output
    assert "turbo" in combined_output
    assert "opencode" in combined_output
    assert "btca" in combined_output
    assert "gh" in combined_output
    assert "ripgrep" in combined_output
    assert ".template_scripts" not in combined_output


def test_nurt_bmad_sync_dry_run_reports_action(tmp_path: Path) -> None:
    """RED: sync bmad dry-run should report non-destructive action plan."""

    result = run_nurt_command(cwd=tmp_path, args=["sync", "bmad", "--dry-run"])

    assert result.returncode == 0, (
        "Expected nurt sync bmad --dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "DRY RUN" in combined_output
    assert "bmad-method" in combined_output
    assert "install" in combined_output


def test_nurt_tools_sync_non_dry_run_reports_failures(tmp_path: Path) -> None:
    """Non-dry sync tools should surface deterministic failure messaging."""

    result = run_nurt_command(
        cwd=tmp_path,
        args=["sync", "tools"],
        env={"NURT_TOOLS_SYNC_SIMULATE_FAILURE": "1"},
    )

    assert result.returncode == 1, (
        "Expected simulated sync tools failure to return non-zero.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "Running nurt sync tools" in combined_output
    assert "uv: FAILED (simulated failure)" in combined_output
    assert "ripgrep: FAILED (simulated failure)" in combined_output


def test_nurt_template_assets_sync_fails_outside_project_root(tmp_path: Path) -> None:
    """Non-dry sync template-assets should fail with clear root-validation message."""

    result = run_nurt_command(cwd=tmp_path, args=["sync", "template-assets"])

    assert result.returncode == 1, (
        "Expected sync template-assets to fail outside project root.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "nurt sync template-assets must run from the root" in combined_output
    assert ".nurt/repo.json" in combined_output


def test_nurt_template_assets_sync_fails_with_dirty_git_repo(tmp_path: Path) -> None:
    """Non-dry sync template-assets should fail when working tree is dirty."""

    (tmp_path / ".nurt").mkdir()
    (tmp_path / ".nurt" / "repo.json").write_text(
        render_repo_marker(), encoding="utf-8"
    )
    (tmp_path / "README.BMAD-GUIDE.md").write_text("stale\n", encoding="utf-8")

    init_result = subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert init_result.returncode == 0, (
        "Expected git init to succeed in test fixture.\n"
        f"stdout:\n{init_result.stdout}\n"
        f"stderr:\n{init_result.stderr}"
    )

    add_result = subprocess.run(
        ["git", "add", "."],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert add_result.returncode == 0, (
        "Expected git add to succeed in test fixture.\n"
        f"stdout:\n{add_result.stdout}\n"
        f"stderr:\n{add_result.stderr}"
    )

    commit_result = subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test User",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-m",
            "Initial commit",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert commit_result.returncode == 0, (
        "Expected git commit to succeed in test fixture.\n"
        f"stdout:\n{commit_result.stdout}\n"
        f"stderr:\n{commit_result.stderr}"
    )

    (tmp_path / "README.BMAD-GUIDE.md").write_text("dirty change\n", encoding="utf-8")

    result = run_nurt_command(cwd=tmp_path, args=["sync", "template-assets"])

    assert result.returncode == 1, (
        "Expected sync template-assets to fail on dirty git repo.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "repository has uncommitted changes" in combined_output


def test_nurt_template_assets_validate_dry_run_reports_action(tmp_path: Path) -> None:
    """template-assets validate dry-run should report validation-focused planning details."""

    source_manifest = load_source_manifest()
    entries = source_manifest.get("entries")
    assert isinstance(entries, list)

    for index, entry in enumerate(entries, start=1):
        assert isinstance(entry, dict)
        source_relative = entry.get("source")
        assert isinstance(source_relative, str)
        source_path = tmp_path / source_relative
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(
            f"snapshot dry-run fixture {index}: {source_relative}\n",
            encoding="utf-8",
        )

    result = run_nurt_command(
        cwd=tmp_path,
        args=[
            "template-assets",
            "validate",
            "--dry-run",
            "--source-root",
            str(tmp_path),
        ],
    )

    assert result.returncode == 0, (
        "Expected template-assets validate dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = _combined_output(result)
    assert "DRY RUN" in combined_output
    assert "template-assets validate" in combined_output
    expected_destinations = {
        entry["destination"]
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("destination"), str)
    }
    assert combined_output.count("would validate bundled template:") == len(
        expected_destinations
    )

    representative_destinations = (
        next(
            path
            for path in sorted(expected_destinations)
            if path.startswith("templates/root_")
        ),
        next(
            path
            for path in sorted(expected_destinations)
            if path.startswith("templates/python_lane_")
        ),
        next(
            path
            for path in sorted(expected_destinations)
            if path.startswith("templates/foundation/")
        ),
    )
    for destination in representative_destinations:
        assert f"would validate bundled template: {destination}" in combined_output

    assert "metadata would be refreshed at metadata.json" in combined_output
    assert "runtime manifest would be refreshed at manifest.json" in combined_output
