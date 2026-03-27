from __future__ import annotations

from pathlib import Path

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.worker import Worker
from textual.widgets import (
    Button,
    ContentSwitcher,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    RichLog,
    Static,
)

from new_repo_template.ralph_config import RalphConfig, load_ralph_config
from new_repo_template.ralph_runner import (
    RalphRunController,
    RalphRunSummary,
    archive_completed_task_file,
    run_ralph_loop,
)
from new_repo_template.ralph_tasks import (
    RalphExecutionSettings,
    RalphTaskPlan,
    build_ralph_dashboard_snapshot,
    discover_ralph_task_files,
    load_ralph_task_plan,
    render_ralph_dashboard_markdown,
    resolve_execution_settings,
    visualize_ralph_task_file,
)


class RalphTuiApp(App[None]):
    CSS = """
    Screen {
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

    #left_column {
        width: 38;
        min-width: 30;
        padding-right: 1;
    }

    #center_column {
        width: 42;
        min-width: 34;
        padding: 0 1;
    }

    #right_column {
        width: 1fr;
        min-width: 38;
        padding-left: 1;
    }

    .panel {
        border: round #2b6674;
        background: #0b1d28;
        padding: 1 1;
        margin-bottom: 1;
    }

    .panel_title {
        color: #79e0d4;
        margin-bottom: 1;
    }

    #task_list,
    #model_list {
        height: 10;
        border: round #3f9cae;
        background: #0f2632;
    }

    #max_loops_input {
        margin-top: 1;
    }

    #status_message {
        min-height: 3;
        color: #f5cf85;
    }

    #toggle_visualization_button {
        width: 100%;
        margin-bottom: 1;
    }

    #visualization_switcher {
        height: 18;
    }

    #visual_dashboard_scroll,
    #visual_detail_scroll {
        height: 1fr;
        overflow-y: auto;
        overflow-x: hidden;
    }

    #visualization_dashboard,
    #visualization_detail {
        width: 100%;
        text-wrap: wrap;
    }

    #log_pane {
        height: 1fr;
        border: round #2b6674;
        background: #0b1d28;
    }

    #actions {
        height: auto;
        margin-top: 1;
    }

    #actions Button {
        margin-right: 1;
    }
    """

    TITLE = "nurt ralph"
    SUB_TITLE = "Ralph loop controller"

    BINDINGS = [
        Binding("r", "run_selected", "Run"),
        Binding("t", "terminate_loop", "Terminate"),
        Binding("v", "toggle_visualization_mode", "View"),
        Binding("a", "archive_completed", "Archive"),
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", show=False),
    ]

    class LogLine(Message):
        def __init__(self, line: str) -> None:
            self.line = line
            super().__init__()

    class LoopChanged(Message):
        def __init__(self, loop_number: int) -> None:
            self.loop_number = loop_number
            super().__init__()

    class VisualizationChanged(Message):
        def __init__(self, visualization: str) -> None:
            self.visualization = visualization
            super().__init__()

    class RunFinished(Message):
        def __init__(
            self, summary: RalphRunSummary | None, error_message: str | None
        ) -> None:
            self.summary = summary
            self.error_message = error_message
            super().__init__()

    def __init__(
        self,
        *,
        project_root: Path,
        config: RalphConfig,
        auto_start: bool = False,
        run_callable=run_ralph_loop,
        use_worker_thread: bool = True,
    ) -> None:
        super().__init__()
        self.project_root = project_root
        self.config = config
        self.auto_start = auto_start
        self.run_callable = run_callable
        self.use_worker_thread = use_worker_thread
        self.task_files = discover_ralph_task_files(project_root)
        self.selected_task_index = 0
        self.selected_model_index = next(
            (
                index
                for index, model in enumerate(config.models)
                if model.id == config.default_model
            ),
            0,
        )
        self.max_loops = config.max_loops
        self.current_loop = 0
        self.current_visualization = ""
        self.current_dashboard_markdown = ""
        self.visualization_mode = "dashboard"
        self.log_history: list[str] = []
        self.last_run_summary: RalphRunSummary | None = None
        self.framework_label = "N/A"
        self.agent_name = "N/A"
        self.bmad_closeout_label = "disabled"
        self.pending_archive_path: Path | None = None
        self._run_in_progress = False
        self._run_controller: RalphRunController | None = None
        self._run_worker: Worker | None = None

    @property
    def selected_task_path(self) -> Path | None:
        if not self.task_files:
            return None
        return self.task_files[self.selected_task_index]

    @property
    def selected_model_id(self) -> str:
        return self.config.models[self.selected_model_index].id

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal(id="body"):
            with Vertical(id="left_column"):
                with Vertical(classes="panel"):
                    yield Static("Task Files", classes="panel_title")
                    yield ListView(*self._build_task_items(), id="task_list")
                with Vertical(classes="panel"):
                    yield Static("Models", classes="panel_title")
                    yield ListView(*self._build_model_items(), id="model_list")
                with Vertical(classes="panel"):
                    yield Static("Run Settings", classes="panel_title")
                    yield Static("Max Loops", id="max_loops_label")
                    yield Input(value=str(self.max_loops), id="max_loops_input")
                    yield Static(id="status_message")
                    with Horizontal(id="actions"):
                        yield Button("Run", id="run_button", variant="primary")
                        yield Button(
                            "Terminate", id="terminate_button", variant="error"
                        )
                        yield Button("Archive", id="archive_button")
            with Vertical(id="center_column"):
                with Vertical(classes="panel"):
                    yield Static("Execution Status", classes="panel_title")
                    yield Static(id="status_summary")
                with Vertical(classes="panel"):
                    yield Static("Visualization", classes="panel_title")
                    yield Button(
                        "Show Full Plan",
                        id="toggle_visualization_button",
                        variant="default",
                    )
                    with ContentSwitcher(
                        initial="visual_dashboard_scroll",
                        id="visualization_switcher",
                    ):
                        with VerticalScroll(id="visual_dashboard_scroll"):
                            yield Markdown("", id="visualization_dashboard")
                        with VerticalScroll(id="visual_detail_scroll"):
                            yield Static("", id="visualization_detail")
            with Vertical(id="right_column"):
                yield RichLog(
                    id="log_pane",
                    auto_scroll=True,
                    wrap=True,
                    markup=False,
                    highlight=False,
                )
        yield Footer()

    def _build_task_items(self) -> tuple[ListItem, ...]:
        if not self.task_files:
            return (ListItem(Label("No task files found")),)
        return tuple(
            ListItem(Label(path.relative_to(self.project_root).as_posix()))
            for path in self.task_files
        )

    def _build_model_items(self) -> tuple[ListItem, ...]:
        return tuple(
            ListItem(Label(f"{model.label} ({model.id})"))
            for model in self.config.models
        )

    def _selected_plan(self) -> RalphTaskPlan | None:
        if self.selected_task_path is None or not self.selected_task_path.exists():
            return None
        return load_ralph_task_plan(self.selected_task_path)

    def _selected_settings(self) -> RalphExecutionSettings | None:
        plan = self._selected_plan()
        if plan is None:
            return None
        return resolve_execution_settings(plan)

    def on_mount(self) -> None:
        self.query_one("#archive_button", Button).disabled = True
        self.query_one("#terminate_button", Button).disabled = True
        task_list = self.query_one("#task_list", ListView)
        model_list = self.query_one("#model_list", ListView)
        if self.task_files:
            task_list.index = self.selected_task_index
        model_list.index = self.selected_model_index
        self._refresh_selected_task_state()
        if self.auto_start and self.task_files:
            self.action_run_selected()

    def _refresh_selected_task_state(self) -> None:
        plan = self._selected_plan()
        settings = self._selected_settings()
        if plan is None or settings is None:
            self.framework_label = "N/A"
            self.agent_name = "N/A"
            self.bmad_closeout_label = "disabled"
            self.query_one("#status_message", Static).update(
                "No task files found under docs/tasks/. Add a task file, then reopen Ralph."
            )
            self.query_one("#run_button", Button).disabled = True
            self.current_visualization = "No visualization available."
            self.current_dashboard_markdown = "# No task selected\n\nSelect a task file to see the live Ralph dashboard.\n"
            self._refresh_visualization_widgets()
            self._apply_run_controls_state(is_running=False)
            self._refresh_status_summary()
            return

        self.framework_label = plan.framework
        self.agent_name = settings.agent
        self.bmad_closeout_label = "enabled" if settings.bmad_closeout else "disabled"
        self.query_one("#status_message", Static).update(
            "Ready to run the selected task."
            if not self._run_in_progress
            else "RALPH is running."
        )
        self.current_visualization = visualize_ralph_task_file(plan.path)
        self.current_dashboard_markdown = render_ralph_dashboard_markdown(plan.path)
        self._refresh_visualization_widgets()
        self._apply_run_controls_state(is_running=self._run_in_progress)
        self._refresh_status_summary()

    def _refresh_visualization_widgets(self) -> None:
        self.query_one("#visualization_dashboard", Markdown).update(
            self.current_dashboard_markdown
        )
        self.query_one("#visualization_detail", Static).update(
            self.current_visualization
        )
        switcher = self.query_one("#visualization_switcher", ContentSwitcher)
        switcher.current = (
            "visual_dashboard_scroll"
            if self.visualization_mode == "dashboard"
            else "visual_detail_scroll"
        )
        toggle_button = self.query_one("#toggle_visualization_button", Button)
        toggle_button.label = (
            "Show Full Plan"
            if self.visualization_mode == "dashboard"
            else "Show Dashboard"
        )

    def _apply_run_controls_state(self, *, is_running: bool) -> None:
        has_task = self.selected_task_path is not None
        self.query_one("#task_list", ListView).disabled = is_running
        self.query_one("#model_list", ListView).disabled = is_running
        self.query_one("#max_loops_input", Input).disabled = is_running
        self.query_one("#run_button", Button).disabled = is_running or not has_task
        self.query_one("#terminate_button", Button).disabled = not is_running
        if is_running:
            self.query_one("#archive_button", Button).disabled = True

    def _refresh_status_summary(self) -> None:
        task_label = (
            self.selected_task_path.relative_to(self.project_root).as_posix()
            if self.selected_task_path is not None
            else "None"
        )
        summary = Table.grid(padding=(0, 1))
        summary.add_column(style="bold #95dbe8")
        summary.add_column(style="#edf6f7")
        summary.add_row("Task", task_label)
        summary.add_row("Framework", self.framework_label)
        summary.add_row("Agent", self.agent_name)
        summary.add_row("Current Loop", str(self.current_loop))
        summary.add_row("Max Loops", str(self.max_loops))
        summary.add_row("BMAD Closeout", self.bmad_closeout_label)
        self.query_one("#status_summary", Static).update(
            Panel.fit(summary, border_style="#3f9cae")
        )

    def action_toggle_visualization_mode(self) -> None:
        self.visualization_mode = (
            "detail" if self.visualization_mode == "dashboard" else "dashboard"
        )
        self._refresh_visualization_widgets()

    @on(ListView.Highlighted, "#task_list")
    def _handle_task_highlighted(self, event: ListView.Highlighted) -> None:
        if not self.task_files or event.list_view.index is None:
            return
        self.selected_task_index = int(event.list_view.index)
        self.current_loop = 0
        self.pending_archive_path = None
        self.query_one("#archive_button", Button).disabled = True
        self._refresh_selected_task_state()

    @on(ListView.Highlighted, "#model_list")
    def _handle_model_highlighted(self, event: ListView.Highlighted) -> None:
        if event.list_view.index is None:
            return
        self.selected_model_index = int(event.list_view.index)
        self._refresh_status_summary()

    @on(Input.Changed, "#max_loops_input")
    def _handle_max_loops_changed(self, event: Input.Changed) -> None:
        self.update_max_loops(event.value)

    def update_max_loops(self, raw_value: str) -> None:
        if self._run_in_progress:
            return
        normalized = raw_value.strip()
        if normalized == "":
            return
        if normalized.isdigit() and int(normalized) > 0:
            self.max_loops = int(normalized)
            self.query_one("#status_message", Static).update(
                "Ready to run the selected task."
            )
            self._refresh_status_summary()
            return
        self.query_one("#status_message", Static).update(
            "Max Loops must be a positive integer."
        )

    @on(Button.Pressed, "#run_button")
    def _handle_run_pressed(self) -> None:
        self.action_run_selected()

    @on(Button.Pressed, "#archive_button")
    def _handle_archive_pressed(self) -> None:
        self.action_archive_completed()

    @on(Button.Pressed, "#terminate_button")
    def _handle_terminate_pressed(self) -> None:
        self.action_terminate_loop()

    @on(Button.Pressed, "#toggle_visualization_button")
    def _handle_visualization_toggle_pressed(self) -> None:
        self.action_toggle_visualization_mode()

    def action_run_selected(self) -> None:
        if self.selected_task_path is None or self._run_in_progress:
            return
        self._run_in_progress = True
        self._run_controller = RalphRunController()
        self._run_worker = None
        self.current_loop = 0
        self.last_run_summary = None
        self.pending_archive_path = None
        self.query_one("#status_message", Static).update("Launching Agent Loop...")
        self.query_one("#log_pane", RichLog).clear()
        self.log_history.clear()
        self._handle_log_line(RalphTuiApp.LogLine("Launching Agent Loop..."))
        self._apply_run_controls_state(is_running=True)
        self._refresh_status_summary()
        if self.use_worker_thread:
            self._run_worker = self.execute_run()
            return
        self._perform_run_sync()

    def _terminate_active_run(self, *, reason: str | None = None) -> None:
        if not self._run_in_progress:
            return
        if reason is not None:
            self.query_one("#status_message", Static).update(reason)
            self._handle_log_line(RalphTuiApp.LogLine(reason))
        if self._run_controller is not None:
            self._run_controller.terminate_active_process()
        if self._run_worker is not None:
            self._run_worker.cancel()

    def action_terminate_loop(self) -> None:
        self._terminate_active_run(reason="Terminating Agent Loop...")

    async def action_quit(self) -> None:
        self._terminate_active_run(reason="App closing. Terminating Agent Loop...")
        self.exit()

    def on_unmount(self) -> None:
        if self._run_controller is not None:
            self._run_controller.terminate_active_process()

    def action_archive_completed(self) -> None:
        if self.pending_archive_path is None:
            return
        archived_path = archive_completed_task_file(self.pending_archive_path)
        self.pending_archive_path = None
        self.query_one("#archive_button", Button).disabled = True
        self.query_one("#status_message", Static).update(
            f"Archived task file to {archived_path.relative_to(self.project_root).as_posix()}."
        )

    @work(thread=True, exclusive=True)
    def execute_run(self) -> None:
        self._run_selected_task(
            emit_message=lambda message: self.call_from_thread(
                self.post_message, message
            )
        )

    def _perform_run_sync(self) -> None:
        def emit_message(message: Message) -> None:
            if isinstance(message, RalphTuiApp.LogLine):
                self._handle_log_line(message)
            elif isinstance(message, RalphTuiApp.LoopChanged):
                self._handle_loop_changed(message)
            elif isinstance(message, RalphTuiApp.VisualizationChanged):
                self._handle_visualization_changed(message)
            elif isinstance(message, RalphTuiApp.RunFinished):
                self._handle_run_finished(message)

        self._run_selected_task(emit_message=emit_message)

    def _run_selected_task(self, *, emit_message) -> None:
        task_path = self.selected_task_path
        if task_path is None:
            emit_message(RalphTuiApp.RunFinished(None, "No task file selected."))
            return

        def emit_log(line: str) -> None:
            emit_message(RalphTuiApp.LogLine(line))

        def emit_loop(loop_number: int) -> None:
            emit_message(RalphTuiApp.LoopChanged(loop_number))

        def emit_visualization(visualization: str) -> None:
            emit_message(RalphTuiApp.VisualizationChanged(visualization))

        try:
            summary = self.run_callable(
                task_file=task_path,
                model=self.selected_model_id,
                max_loops=self.max_loops,
                cwd=self.project_root,
                on_log=emit_log,
                on_loop_change=emit_loop,
                on_visualization=emit_visualization,
                no_interactive=True,
                archive_completed=False,
                controller=self._run_controller,
            )
        except Exception as exc:
            emit_message(RalphTuiApp.RunFinished(None, str(exc)))
            return

        emit_message(RalphTuiApp.RunFinished(summary, None))

    @on(LogLine)
    def _handle_log_line(self, message: LogLine) -> None:
        self.log_history.append(message.line)
        self.query_one("#log_pane", RichLog).write(Text.from_ansi(message.line))
        if self._run_in_progress and message.line != "Launching Agent Loop...":
            self.query_one("#status_message", Static).update("Agent Loop Running...")

    @on(LoopChanged)
    def _handle_loop_changed(self, message: LoopChanged) -> None:
        self.current_loop = message.loop_number
        self._refresh_status_summary()

    @on(VisualizationChanged)
    def _handle_visualization_changed(self, message: VisualizationChanged) -> None:
        self.current_visualization = message.visualization
        task_path = self.selected_task_path
        if task_path is not None and task_path.exists():
            self.current_dashboard_markdown = render_ralph_dashboard_markdown(task_path)
            snapshot = build_ralph_dashboard_snapshot(task_path)
            self.framework_label = snapshot.framework
        self._refresh_visualization_widgets()

    @on(RunFinished)
    def _handle_run_finished(self, message: RunFinished) -> None:
        self._run_in_progress = False
        self._run_worker = None
        self._run_controller = None
        self._apply_run_controls_state(is_running=False)
        if message.error_message is not None:
            self.last_run_summary = None
            self.query_one("#status_message", Static).update(
                f"RALPH failed: {message.error_message}"
            )
            self._refresh_status_summary()
            return

        self.last_run_summary = message.summary
        assert message.summary is not None
        self.current_loop = message.summary.final_loop
        if message.summary.completed and message.summary.archived_path is None:
            current_task_path = self.selected_task_path
            if current_task_path is not None and current_task_path.exists():
                self.pending_archive_path = current_task_path
                self.query_one("#archive_button", Button).disabled = False

        if message.summary.terminated:
            self.query_one("#status_message", Static).update("Agent Loop Terminated.")
        elif message.summary.succeeded:
            if message.summary.completed:
                self.query_one("#status_message", Static).update(
                    "RALPH completed. Press a to archive the completed task or q to quit."
                )
            elif message.summary.reached_max_loops:
                self.query_one("#status_message", Static).update(
                    "RALPH stopped after reaching the configured max loops."
                )
            else:
                self.query_one("#status_message", Static).update("RALPH finished.")
        else:
            self.query_one("#status_message", Static).update(
                "RALPH finished with errors. Review the log pane for details."
            )
        self._refresh_status_summary()


def run_ralph_tui(*, project_root: Path) -> int:
    app = RalphTuiApp(
        project_root=project_root,
        config=load_ralph_config(cwd=project_root),
    )
    app.run()
    if app.last_run_summary is None:
        return 0
    return 0 if app.last_run_summary.succeeded else 1
