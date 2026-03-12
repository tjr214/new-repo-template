from __future__ import annotations

import asyncio
from pathlib import Path

from rich.console import Console
from textual.containers import Vertical
from textual.widgets import Input, RadioSet, SelectionList, Static

from new_repo_template.interactive_tui import (
    InteractiveWizardResult,
    NewProjectWizardApp,
)


def test_textual_wizard_project_name_normalizes_and_advances_on_enter(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name=None,
            output_root=tmp_path,
        )

        async with app.run_test(size=(120, 36)) as pilot:
            project_input = app.query_one("#project_name_input", Input)
            project_input.value = "My Cool App"
            await pilot.pause()

            await pilot.press("enter")
            await pilot.pause()

            assert app.current_step == "targets"
            assert app.project_name == "my-cool-app"
            assert app.output_path == tmp_path / "my-cool-app"

    asyncio.run(scenario())


def test_textual_wizard_foundation_selection_is_exclusive(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name="demo-foundation-exclusive",
            output_root=tmp_path,
        )

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.press("enter")
            await pilot.pause()

            selection_list = app.query_one("#targets_list", SelectionList)
            assert selection_list.selected == ["foundation"]

            await pilot.press("down", "down", "space")
            await pilot.pause()
            assert selection_list.selected == ["web"]

            await pilot.press("home", "space")
            await pilot.pause()
            assert selection_list.selected == ["foundation"]

    asyncio.run(scenario())


def test_textual_wizard_backend_requires_auth_and_none_is_valid(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name="demo-backend-only",
            output_root=tmp_path,
        )

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.press("enter")
            await pilot.pause()

            await pilot.press("down", "down", "down", "space")
            await pilot.pause()
            assert app.selected_targets == ("backend",)

            await pilot.press("enter")
            await pilot.pause()
            assert app.current_step == "auth"

            radio_set = app.query_one("#auth_options", RadioSet)
            assert radio_set.pressed_button is None

            await pilot.click("#auth-none")
            await pilot.pause()

            await pilot.press("enter")
            await pilot.pause()
            assert app.current_step == "review"
            assert app.selected_auth == "none"

            await pilot.press("enter")
            await pilot.pause()

        assert app.final_result == InteractiveWizardResult(
            project_name="demo-backend-only",
            targets=("backend",),
            auth="none",
        )

    asyncio.run(scenario())


def test_textual_wizard_skips_auth_when_backend_not_selected(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name="demo-python",
            output_root=tmp_path,
        )

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.press("enter")
            await pilot.pause()

            await pilot.press("down", "space")
            await pilot.pause()

            assert app.selected_targets == ("python",)

            await pilot.press("enter")
            await pilot.pause()
            assert app.current_step == "review"
            assert app.selected_auth is None

            await pilot.press("enter")
            await pilot.pause()

        assert app.final_result == InteractiveWizardResult(
            project_name="demo-python",
            targets=("python",),
            auth=None,
        )

    asyncio.run(scenario())


def test_textual_wizard_clears_stale_auth_when_targets_change(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name="demo-auth-reset",
            output_root=tmp_path,
        )

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.press("enter")
            await pilot.pause()

            await pilot.press("down", "down", "down", "space")
            await pilot.pause()
            assert app.selected_targets == ("backend",)

            await pilot.press("enter")
            await pilot.pause()
            assert app.current_step == "auth"

            await pilot.click("#auth-clerk")
            await pilot.pause()
            assert app.selected_auth == "clerk"

            await pilot.press("escape")
            await pilot.pause()
            assert app.current_step == "targets"

            await pilot.press("home", "down", "down", "down", "space")
            await pilot.pause()

            assert app.selected_targets == ("foundation",)
            assert app.selected_auth is None

            await pilot.press("enter")
            await pilot.pause()
            assert app.current_step == "review"

    asyncio.run(scenario())


def test_textual_wizard_escape_goes_back_and_exits_from_first_step(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name="demo-escape",
            output_root=tmp_path,
        )

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.press("enter")
            await pilot.pause()
            assert app.current_step == "targets"

            await pilot.press("escape")
            await pilot.pause()
            assert app.current_step == "project"

            await pilot.press("escape")
            await pilot.pause()

        assert app.final_result is None

    asyncio.run(scenario())


def test_textual_wizard_ctrl_q_quits(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name="demo-quit",
            output_root=tmp_path,
        )

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.press("ctrl+q")
            await pilot.pause()

        assert app.final_result is None

    asyncio.run(scenario())


def test_textual_wizard_uses_wide_layout_at_standard_size(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name="demo-wide-layout",
            output_root=tmp_path,
        )

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.press("enter")
            await pilot.pause()

            progress = app.query_one("#progress_column", Vertical)
            main = app.query_one("#main_column", Vertical)
            summary = app.query_one("#summary_column", Vertical)
            selection_list = app.query_one("#targets_list", SelectionList)
            target_details = app.query_one("#target_details", Static)

            assert not app.screen.has_class("compact")
            assert progress.region.x < main.region.x < summary.region.x
            assert target_details.region.x > selection_list.region.x
            assert target_details.region.y == selection_list.region.y

    asyncio.run(scenario())


def test_textual_wizard_uses_compact_layout_for_80x24(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name="demo-compact-layout",
            output_root=tmp_path,
        )

        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.press("enter")
            await pilot.pause()

            progress = app.query_one("#progress_column", Vertical)
            main = app.query_one("#main_column", Vertical)
            summary = app.query_one("#summary_column", Vertical)
            selection_list = app.query_one("#targets_list", SelectionList)
            target_details = app.query_one("#target_details", Static)

            assert app.screen.has_class("compact")
            assert progress.region.y < main.region.y < summary.region.y
            assert selection_list.region.y < target_details.region.y
            assert selection_list.region.x == target_details.region.x

    asyncio.run(scenario())


def test_textual_wizard_summary_wraps_output_path_across_lines() -> None:
    app = NewProjectWizardApp(
        project_name="demo-summary-wrap",
        output_root=Path(
            "/Users/example/projects/very/long/path/for/testing/summary/output"
        ),
    )

    console = Console(record=True, width=38)
    console.print(app._render_summary_panel())
    rendered = console.export_text()

    assert "Output" in rendered
    assert "Users/example/projects" in rendered
    assert "ery/long/path/for/testing" in rendered
    assert "summary/output/demo-summ" in rendered
