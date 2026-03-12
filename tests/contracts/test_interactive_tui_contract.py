from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import RadioSet, SelectionList

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
