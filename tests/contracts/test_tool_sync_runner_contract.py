from __future__ import annotations

from collections.abc import Callable

from new_repo_template.tool_sync_runner import (
    ToolSyncResult,
    ToolSyncTask,
    ToolSyncUpdate,
    run_tool_sync,
)


def test_run_tool_sync_dry_run_reports_all_managed_tools() -> None:
    summary = run_tool_sync(dry_run=True)

    assert [result.tool for result in summary.results] == [
        "uv",
        "bun",
        "turbo",
        "opencode",
        "btca",
        "gh",
        "ripgrep",
    ]
    assert all(result.status == "DRY-RUN" for result in summary.results)
    assert summary.succeeded is True


def test_run_tool_sync_emits_running_and_final_updates_for_custom_tasks() -> None:
    updates: list[ToolSyncUpdate] = []
    logs: list[str] = []

    def fake_run(log: Callable[[str], None]) -> ToolSyncResult:
        log("installing demo tool")
        return ToolSyncResult(tool="demo", status="INSTALLED", detail="1.2.3")

    summary = run_tool_sync(
        dry_run=False,
        tasks=(
            ToolSyncTask(
                tool="demo",
                label="Demo Tool",
                dry_run_detail="would install demo tool",
                runner=fake_run,
            ),
        ),
        on_update=updates.append,
        on_log=logs.append,
    )

    assert summary.succeeded is True
    assert logs == ["installing demo tool"]
    assert updates[0] == ToolSyncUpdate(
        tool="demo",
        status="RUNNING",
        detail="Demo Tool",
    )
    assert updates[-1] == ToolSyncUpdate(
        tool="demo",
        status="INSTALLED",
        detail="1.2.3",
    )
