from __future__ import annotations

import asyncio
from pathlib import Path

from textual.containers import Vertical
from textual.widgets import RadioSet, SelectionList, Static

from new_repo_template.interactive_tui import (
    InteractiveWizardResult,
    NewProjectWizardApp,
)


def test_textual_wizard_foundation_selection_is_exclusive(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name="demo-foundation-exclusive",
            output_path=tmp_path / "demo-foundation-exclusive",
        )

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.press("ctrl+n")
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


def test_textual_wizard_requires_auth_for_web_backend(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name="demo-web-backend",
            output_path=tmp_path / "demo-web-backend",
        )

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.press("ctrl+n")
            await pilot.pause()

            await pilot.press("down", "down", "space", "down", "space")
            await pilot.pause()

            assert app.selected_targets == ("web", "backend")

            await pilot.press("ctrl+n")
            await pilot.pause()
            assert app.current_step == "auth"

            radio_set = app.query_one("#auth_options", RadioSet)
            assert radio_set.pressed_button is None

            await pilot.click("#auth-better-auth")
            await pilot.pause()

            await pilot.press("ctrl+n")
            await pilot.pause()
            assert app.current_step == "review"
            assert app.selected_auth == "better-auth"

            await pilot.press("ctrl+r")
            await pilot.pause()

        assert app.final_result == InteractiveWizardResult(
            targets=("web", "backend"),
            auth="better-auth",
        )

    asyncio.run(scenario())


def test_textual_wizard_skips_auth_when_not_needed(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name="demo-python",
            output_path=tmp_path / "demo-python",
        )

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.press("ctrl+n")
            await pilot.pause()

            await pilot.press("down", "space")
            await pilot.pause()

            assert app.selected_targets == ("python",)

            await pilot.press("ctrl+n")
            await pilot.pause()
            assert app.current_step == "review"
            assert app.selected_auth is None

            await pilot.press("ctrl+r")
            await pilot.pause()

        assert app.final_result == InteractiveWizardResult(
            targets=("python",),
            auth=None,
        )

    asyncio.run(scenario())


def test_textual_wizard_clears_stale_auth_when_targets_change(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name="demo-auth-reset",
            output_path=tmp_path / "demo-auth-reset",
        )

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.press("ctrl+n")
            await pilot.pause()

            await pilot.press("down", "down", "space", "down", "space")
            await pilot.pause()
            assert app.selected_targets == ("web", "backend")

            await pilot.press("ctrl+n")
            await pilot.pause()
            assert app.current_step == "auth"

            await pilot.click("#auth-clerk")
            await pilot.pause()
            assert app.selected_auth == "clerk"

            await pilot.press("ctrl+b")
            await pilot.pause()
            assert app.current_step == "targets"

            await pilot.press("home", "down", "down", "down", "space")
            await pilot.pause()

            assert app.selected_targets == ("web",)
            assert app.selected_auth is None

            await pilot.press("ctrl+n")
            await pilot.pause()
            assert app.current_step == "review"

    asyncio.run(scenario())


def test_textual_wizard_uses_wide_layout_at_standard_size(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = NewProjectWizardApp(
            project_name="demo-wide-layout",
            output_path=tmp_path / "demo-wide-layout",
        )

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.press("ctrl+n")
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
            output_path=tmp_path / "demo-compact-layout",
        )

        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.press("ctrl+n")
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
