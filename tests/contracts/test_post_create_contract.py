from __future__ import annotations

from pathlib import Path

from rich.console import Console

from new_repo_template import post_create


def test_post_create_pipeline_runs_requested_steps_in_required_order(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        post_create,
        "run_bmad_sync",
        lambda **_: calls.append("bmad") or 0,
    )
    monkeypatch.setattr(
        post_create,
        "generate_project_lockfiles",
        lambda **_: calls.append("lockfiles") or 0,
    )
    monkeypatch.setattr(
        post_create,
        "initialize_git_repository",
        lambda **_: calls.append("git-init") or 0,
    )
    monkeypatch.setattr(
        post_create,
        "create_initial_commit",
        lambda **_: calls.append("git-commit") or 0,
    )
    monkeypatch.setattr(
        post_create,
        "run_tools_sync",
        lambda **_: calls.append("tools") or 0,
    )

    status = post_create.run_post_create_pipeline(
        project_root=tmp_path / "demo-project",
        install_bmad=True,
        install_core_tools=True,
    )

    assert status == 0
    assert calls == ["bmad", "lockfiles", "git-init", "git-commit", "tools"]


def test_post_create_pipeline_stops_before_git_when_bmad_fails(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        post_create,
        "run_bmad_sync",
        lambda **_: calls.append("bmad") or 1,
    )
    monkeypatch.setattr(
        post_create,
        "generate_project_lockfiles",
        lambda **_: calls.append("lockfiles") or 0,
    )
    monkeypatch.setattr(
        post_create,
        "initialize_git_repository",
        lambda **_: calls.append("git-init") or 0,
    )
    monkeypatch.setattr(
        post_create,
        "create_initial_commit",
        lambda **_: calls.append("git-commit") or 0,
    )
    monkeypatch.setattr(
        post_create,
        "run_tools_sync",
        lambda **_: calls.append("tools") or 0,
    )

    status = post_create.run_post_create_pipeline(
        project_root=tmp_path / "demo-project",
        install_bmad=True,
        install_core_tools=True,
    )

    assert status == 1
    assert calls == ["bmad"]


def test_post_create_pipeline_skips_optional_steps_when_not_requested(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        post_create,
        "run_bmad_sync",
        lambda **_: calls.append("bmad") or 0,
    )
    monkeypatch.setattr(
        post_create,
        "generate_project_lockfiles",
        lambda **_: calls.append("lockfiles") or 0,
    )
    monkeypatch.setattr(
        post_create,
        "initialize_git_repository",
        lambda **_: calls.append("git-init") or 0,
    )
    monkeypatch.setattr(
        post_create,
        "create_initial_commit",
        lambda **_: calls.append("git-commit") or 0,
    )
    monkeypatch.setattr(
        post_create,
        "run_tools_sync",
        lambda **_: calls.append("tools") or 0,
    )

    status = post_create.run_post_create_pipeline(
        project_root=tmp_path / "demo-project",
        install_bmad=False,
        install_core_tools=False,
    )

    assert status == 0
    assert calls == ["lockfiles", "git-init", "git-commit"]


def test_render_post_create_plan_reflects_selected_options(tmp_path: Path) -> None:
    rendered = post_create.render_post_create_plan(
        project_root=tmp_path / "demo-project",
        install_bmad=True,
        install_core_tools=False,
    )

    assert "Post-create automation plan:" in rendered
    assert "BMAD Method: yes" in rendered
    assert "Core tools updater: no" in rendered
    assert 'git init -> git add . -> git commit -m "Initial Commit"' in rendered


def test_render_completion_overview_calls_out_cd_handoff(tmp_path: Path) -> None:
    console = Console(record=True, width=100)
    console.print(
        post_create.render_completion_overview(
            project_root=tmp_path / "demo-project",
            targets=("web", "backend"),
            auth="clerk",
            install_bmad=True,
            install_core_tools=False,
        )
    )

    rendered = console.export_text()
    assert "Setup Complete" in rendered
    assert "web, backend" in rendered
    assert "clerk" in rendered
    assert "Next step: change into the new project directory." in rendered
    assert "cd demo-project" in rendered
