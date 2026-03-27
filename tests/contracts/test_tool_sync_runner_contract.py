from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from new_repo_template.tool_sync_runner import (
    ToolSyncResult,
    ToolSyncTask,
    ToolSyncUpdate,
    run_tool_sync,
)
from new_repo_template.version_baseline import VersionDiff


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
    assert any("OpenCode Installation/Update Script" in line for line in logs)
    assert any("Checking Demo Tool..." in line for line in logs)
    assert "installing demo tool" in logs
    assert any("Done." in line for line in logs)
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


def test_run_tool_sync_refreshes_version_baseline_when_bun_or_turbo_update(
    tmp_path: Path,
) -> None:
    baseline_path = tmp_path / "version-baseline.json"
    baseline_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_at": "2026-03-01T00:00:00Z",
                "managed_tools": {
                    "bun": {"source": "npm:bun", "version": "1.3.10"},
                    "python": {"source": "endoflife:python", "version": "3.14.3"},
                    "turbo": {"source": "npm:turbo", "version": "2.8.19"},
                    "typescript": {"source": "npm:typescript", "version": "6.0.2"},
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    logs: list[str] = []

    def fake_bun(log: Callable[[str], None]) -> ToolSyncResult:
        log("updating bun")
        return ToolSyncResult(tool="bun", status="UPDATED", detail="1.3.10 -> 1.3.11")

    def fake_turbo(log: Callable[[str], None]) -> ToolSyncResult:
        log("installing turbo")
        return ToolSyncResult(tool="turbo", status="INSTALLED", detail="2.8.20")

    summary = run_tool_sync(
        dry_run=False,
        cwd=tmp_path,
        on_log=logs.append,
        tasks=(
            ToolSyncTask(
                tool="bun",
                label="bun",
                dry_run_detail="would update bun",
                runner=fake_bun,
            ),
            ToolSyncTask(
                tool="turbo",
                label="turborepo",
                dry_run_detail="would update turbo",
                runner=fake_turbo,
            ),
        ),
    )

    updated = json.loads(baseline_path.read_text(encoding="utf-8"))
    managed_tools = updated["managed_tools"]

    assert managed_tools["bun"]["version"] == "1.3.11"
    assert managed_tools["turbo"]["version"] == "2.8.20"
    assert summary.baseline_diffs == (
        VersionDiff(tool="bun", current="1.3.10", latest="1.3.11"),
        VersionDiff(tool="turbo", current="2.8.19", latest="2.8.20"),
    )
    assert any(
        "Updated version baseline metadata from sync tools:" in line for line in logs
    )
    assert any("- bun: 1.3.10 -> 1.3.11" in line for line in logs)
