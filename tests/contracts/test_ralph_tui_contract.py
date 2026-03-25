from __future__ import annotations

import asyncio
from threading import Event
from time import sleep
from pathlib import Path

from textual.containers import VerticalScroll
from textual.widgets import Button, ContentSwitcher, Input, ListView, Markdown, RichLog

from new_repo_template.ralph_config import load_ralph_config
from new_repo_template.ralph_runner import RalphRunController
from new_repo_template.ralph_tui import RalphRunSummary, RalphTuiApp


def _write_task_file(repo_root: Path, *, framework: str, name: str) -> Path:
    task_path = repo_root / "docs" / "tasks" / f"{name}.yaml"
    task_path.parent.mkdir(parents=True, exist_ok=True)
    task_path.write_text(
        f"""metadata:\n  version: \"1.1.0\"\n  created_date: \"2026-03-24\"\n  last_updated: \"2026-03-24\"\n  author: \"test\"\n  license: null\n  framework: \"{framework}\"\ntask:\n  name: \"{name}\"\n  description: \"Demo\"\n  status: \"pending\"\n  phases:\n    - id: \"phase-1\"\n      name: \"Phase\"\n      description: \"Demo\"\n      status: \"pending\"\n      steps:\n        - id: \"step-1.1\"\n          name: \"Step\"\n          description: \"Demo\"\n          status: \"pending\"\n          instructions:\n            - id: \"instr-1.1.1\"\n              content: \"Demo\"\n              status: \"pending\"\n""",
        encoding="utf-8",
    )
    return task_path


def test_ralph_tui_loads_tasks_models_and_derived_status(tmp_path: Path) -> None:
    async def scenario() -> None:
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "ralph.config.yaml").write_text(
            """default_model: openai/gpt-5.4\nmax_loops: 20\nmodels:\n  - id: openai/gpt-5.4\n    label: GPT-5.4\n  - id: build/model\n    label: Build Model\n""",
            encoding="utf-8",
        )
        _write_task_file(repo_root, framework="bmad", name="alpha-task")
        _write_task_file(repo_root, framework="standalone", name="beta-task")

        app = RalphTuiApp(
            project_root=repo_root,
            config=load_ralph_config(cwd=repo_root),
            auto_start=False,
        )

        async with app.run_test(size=(140, 42)) as pilot:
            await pilot.pause()

            task_list = app.query_one("#task_list", ListView)
            model_list = app.query_one("#model_list", ListView)
            max_loops_input = app.query_one("#max_loops_input", Input)

            assert task_list.index == 0
            assert model_list.index == 0
            assert app.selected_task_path is not None
            assert app.framework_label == "bmad"
            assert app.agent_name == "bmad-master"
            assert app.bmad_closeout_label == "enabled"
            assert max_loops_input.value == "20"
            assert app.visualization_mode == "dashboard"
            assert "## Overview" in app.current_dashboard_markdown
            assert "## Up Next" in app.current_dashboard_markdown
            assert (
                "TASK IMPLEMENTATION PLAN - STATUS SUMMARY" in app.current_visualization
            )

            switcher = app.query_one("#visualization_switcher", ContentSwitcher)
            toggle_button = app.query_one("#toggle_visualization_button", Button)
            dashboard_scroll = app.query_one("#visual_dashboard_scroll", VerticalScroll)
            detail_scroll = app.query_one("#visual_detail_scroll", VerticalScroll)

            assert switcher.current == "visual_dashboard_scroll"
            assert str(toggle_button.label) == "Show Full Plan"
            assert dashboard_scroll.styles.overflow_x == "hidden"
            assert detail_scroll.styles.overflow_x == "hidden"

            app.action_toggle_visualization_mode()
            await pilot.pause()

            assert app.visualization_mode == "detail"
            assert switcher.current == "visual_detail_scroll"
            assert str(toggle_button.label) == "Show Dashboard"

            await pilot.click("#task_list")
            await pilot.press("down")
            await pilot.pause()

            assert app.framework_label == "standalone"
            assert app.agent_name == "build"
            assert app.bmad_closeout_label == "disabled"

    asyncio.run(scenario())


def test_ralph_tui_runs_injected_runner_and_updates_loop_and_logs(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "ralph.config.yaml").write_text(
            """default_model: openai/gpt-5.4\nmax_loops: 20\nmodels:\n  - id: openai/gpt-5.4\n    label: GPT-5.4\n""",
            encoding="utf-8",
        )
        task_path = _write_task_file(repo_root, framework="bmad", name="alpha-task")

        app = RalphTuiApp(
            project_root=repo_root,
            config=load_ralph_config(cwd=repo_root),
            auto_start=False,
            use_worker_thread=False,
        )

        async with app.run_test(size=(140, 42)) as pilot:
            await pilot.pause()

            app._handle_visualization_changed(
                RalphTuiApp.VisualizationChanged("demo visualization")
            )
            app._handle_loop_changed(RalphTuiApp.LoopChanged(1))
            app._handle_log_line(RalphTuiApp.LogLine("loop started"))
            app._handle_run_finished(
                RalphTuiApp.RunFinished(
                    RalphRunSummary(
                        succeeded=True,
                        completed=True,
                        reached_max_loops=False,
                        final_loop=1,
                        task_file=task_path,
                        archived_path=None,
                        framework="bmad",
                    ),
                    None,
                )
            )
            await pilot.pause()

            log_widget = app.query_one("#log_pane", RichLog)

            assert app.current_loop == 1
            assert app.last_run_summary is not None
            assert app.last_run_summary.completed is True
            assert "demo visualization" in app.current_visualization
            assert "## Overview" in app.current_dashboard_markdown
            assert app.log_history[-1] == "loop started"
            assert log_widget.lines

    asyncio.run(scenario())


def test_ralph_tui_locks_controls_and_can_terminate_active_run(tmp_path: Path) -> None:
    async def scenario() -> None:
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "ralph.config.yaml").write_text(
            """default_model: openai/gpt-5.4\nmax_loops: 20\nmodels:\n  - id: openai/gpt-5.4\n    label: GPT-5.4\n""",
            encoding="utf-8",
        )
        _write_task_file(repo_root, framework="bmad", name="alpha-task")
        started = Event()

        def fake_run_callable(**kwargs: object) -> RalphRunSummary:
            controller = kwargs["controller"]
            assert controller is not None
            assert isinstance(controller, RalphRunController)
            started.set()
            while not controller.stop_requested:
                sleep(0.02)
            return RalphRunSummary(
                succeeded=False,
                completed=False,
                reached_max_loops=False,
                final_loop=1,
                task_file=repo_root / "docs" / "tasks" / "alpha-task.yaml",
                archived_path=None,
                framework="bmad",
                terminated=True,
            )

        app = RalphTuiApp(
            project_root=repo_root,
            config=load_ralph_config(cwd=repo_root),
            auto_start=False,
            run_callable=fake_run_callable,
        )

        async with app.run_test(size=(140, 42)) as pilot:
            await pilot.pause()
            app.action_run_selected()
            await pilot.pause(0.2)
            assert started.is_set() is True

            model_list = app.query_one("#model_list", ListView)
            task_list = app.query_one("#task_list", ListView)
            max_loops_input = app.query_one("#max_loops_input", Input)
            terminate_button = app.query_one("#terminate_button", Button)
            log_widget = app.query_one("#log_pane", RichLog)
            dashboard_widget = app.query_one("#visualization_dashboard", Markdown)

            assert model_list.disabled is True
            assert task_list.disabled is True
            assert max_loops_input.disabled is True
            assert terminate_button.disabled is False
            assert log_widget.wrap is True
            assert dashboard_widget.parent is not None

            app.action_terminate_loop()
            await pilot.pause(0.2)

            assert app._run_in_progress is False
            assert app.last_run_summary is not None
            assert app.last_run_summary.terminated is True
            assert app.query_one("#model_list", ListView).disabled is False
            assert app.query_one("#terminate_button", Button).disabled is True

    asyncio.run(scenario())
