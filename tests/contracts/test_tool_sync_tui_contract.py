from __future__ import annotations

import asyncio

from rich.color import Color
from textual.widgets import DataTable, RichLog

from new_repo_template.tool_sync_runner import (
    ToolSyncResult,
    ToolSyncSummary,
    ToolSyncUpdate,
)
from new_repo_template.tool_sync_tui import ToolSyncTuiApp


def test_tool_sync_tui_updates_status_rows_and_log_history() -> None:
    async def scenario() -> None:
        app = ToolSyncTuiApp(auto_start=False)

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.pause()

            app._handle_status_updated(
                ToolSyncTuiApp.StatusUpdated(
                    ToolSyncUpdate(tool="uv", status="RUNNING", detail="uv")
                )
            )
            app._handle_log_line(ToolSyncTuiApp.LogLine("checking uv"))
            app._handle_sync_finished(
                ToolSyncTuiApp.SyncFinished(
                    ToolSyncSummary(
                        results=(
                            ToolSyncResult(
                                tool="uv",
                                status="UP-TO-DATE",
                                detail="uv 0.8.12",
                            ),
                        )
                    )
                )
            )
            await pilot.pause()

            assert app.status_by_tool["uv"] == ToolSyncUpdate(
                tool="uv",
                status="RUNNING",
                detail="uv",
            )
            assert app.log_history == ["checking uv"]
            assert app.final_summary is not None
            assert app.final_summary.succeeded is True

    asyncio.run(scenario())


def test_tool_sync_tui_uses_rich_log_and_resized_columns() -> None:
    async def scenario() -> None:
        app = ToolSyncTuiApp(auto_start=False)

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.pause()

            table = app.query_one("#status_table", DataTable)
            log_widget = app.query_one("#log_pane", RichLog)
            tool_key, status_key, detail_key = tuple(table.columns.keys())

            assert table.columns[tool_key].width >= 11
            assert table.columns[status_key].width >= 12
            assert table.columns[detail_key].width > table.columns[status_key].width
            assert isinstance(log_widget, RichLog)

    asyncio.run(scenario())


def test_tool_sync_tui_preserves_ansi_styling_in_rich_log() -> None:
    async def scenario() -> None:
        app = ToolSyncTuiApp(auto_start=False)

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.pause()

            app._handle_log_line(
                ToolSyncTuiApp.LogLine("\x1b[0;31mError: demo failure\x1b[0m")
            )
            await pilot.pause()

            log_widget = app.query_one("#log_pane", RichLog)
            strip = log_widget.lines[-1]
            segment = strip._segments[0]

            assert app.log_history[-1] == "\x1b[0;31mError: demo failure\x1b[0m"
            assert segment.text == "Error: demo failure"
            assert segment.style is not None
            assert segment.style.color is not None
            assert segment.style.color.number == Color.parse("red").number

    asyncio.run(scenario())
