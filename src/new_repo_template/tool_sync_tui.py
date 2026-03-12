from __future__ import annotations

from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import DataTable, Footer, Header, Log, Static

from new_repo_template.tool_sync_runner import (
    ToolSyncSummary,
    ToolSyncUpdate,
    default_tool_tasks,
    run_tool_sync,
)


class ToolSyncTuiApp(App[None]):
    CSS = """
    Screen {
        layout: vertical;
        background: #071521;
        color: #edf6f7;
    }

    Header {
        dock: top;
    }

    Footer {
        dock: bottom;
    }

    #body {
        height: 1fr;
        padding: 1 1 0 1;
    }

    #status_message {
        margin-bottom: 1;
        color: #c5d8de;
    }

    #status_table {
        height: 10;
        min-height: 8;
        margin-bottom: 1;
        border: round #3f9cae;
        background: #0b1d28;
    }

    #log_pane {
        height: 1fr;
        border: round #2b6674;
        background: #0b1d28;
    }
    """

    TITLE = "nurt tools sync"
    SUB_TITLE = "Core tools updater"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", show=False),
    ]

    class StatusUpdated(Message):
        def __init__(self, update: ToolSyncUpdate) -> None:
            self.update = update
            super().__init__()

    class LogLine(Message):
        def __init__(self, line: str) -> None:
            self.line = line
            super().__init__()

    class SyncFinished(Message):
        def __init__(self, summary: ToolSyncSummary) -> None:
            self.summary = summary
            super().__init__()

    def __init__(self, *, cwd: Path | None = None, auto_start: bool = True) -> None:
        super().__init__()
        self.cwd = cwd
        self.auto_start = auto_start
        self.tasks = default_tool_tasks(cwd=cwd)
        self.status_by_tool: dict[str, ToolSyncUpdate] = {
            task.tool: ToolSyncUpdate(
                tool=task.tool, status="PENDING", detail="not run"
            )
            for task in self.tasks
        }
        self.log_history: list[str] = []
        self.final_summary: ToolSyncSummary | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="body"):
            yield Static(
                "The status table stays visible while the log pane streams installer output in real time.",
                id="status_message",
            )
            yield DataTable(id="status_table")
            yield Log(id="log_pane", auto_scroll=True)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#status_table", DataTable)
        table.add_column("Tool", key="tool")
        table.add_column("Status", key="status")
        table.add_column("Details", key="detail")
        table.fixed_rows = 1
        table.zebra_stripes = True

        for task in self.tasks:
            table.add_row(task.tool, "PENDING", "not run", key=task.tool)

        if self.auto_start:
            self.run_sync()

    @work(thread=True, exclusive=True)
    def run_sync(self) -> None:
        def emit_update(update: ToolSyncUpdate) -> None:
            self.call_from_thread(
                self.post_message,
                ToolSyncTuiApp.StatusUpdated(update),
            )

        def emit_log(line: str) -> None:
            self.call_from_thread(
                self.post_message,
                ToolSyncTuiApp.LogLine(line),
            )

        summary = run_tool_sync(
            dry_run=False,
            tasks=self.tasks,
            cwd=self.cwd,
            on_update=emit_update,
            on_log=emit_log,
        )
        self.call_from_thread(
            self.post_message,
            ToolSyncTuiApp.SyncFinished(summary),
        )

    @on(StatusUpdated)
    def _handle_status_updated(self, message: StatusUpdated) -> None:
        update = message.update
        self.status_by_tool[update.tool] = update
        table = self.query_one("#status_table", DataTable)
        table.update_cell(update.tool, "status", update.status)
        table.update_cell(update.tool, "detail", update.detail)

    @on(LogLine)
    def _handle_log_line(self, message: LogLine) -> None:
        self.log_history.append(message.line)
        self.query_one("#log_pane", Log).write_line(message.line)

    @on(SyncFinished)
    def _handle_sync_finished(self, message: SyncFinished) -> None:
        self.final_summary = message.summary
        status_copy = (
            "Core tools updater completed successfully. Press q to exit."
            if message.summary.succeeded
            else "Core tools updater finished with errors. Press q to exit."
        )
        self.query_one("#status_message", Static).update(status_copy)


def run_tool_sync_tui(*, cwd: Path | None = None) -> int:
    app = ToolSyncTuiApp(cwd=cwd)
    app.run()
    if app.final_summary is None:
        return 1
    return 0 if app.final_summary.succeeded else 1
