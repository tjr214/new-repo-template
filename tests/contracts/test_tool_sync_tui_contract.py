from __future__ import annotations

import asyncio

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
