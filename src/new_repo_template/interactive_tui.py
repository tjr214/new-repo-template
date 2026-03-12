from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    ContentSwitcher,
    Footer,
    Header,
    RadioButton,
    RadioSet,
    SelectionList,
    Static,
)
from textual.widgets.selection_list import Selection


WIZARD_STEP_WELCOME = "welcome"
WIZARD_STEP_TARGETS = "targets"
WIZARD_STEP_AUTH = "auth"
WIZARD_STEP_REVIEW = "review"

AUTH_CHOICES: tuple[str, str] = ("clerk", "better-auth")

TARGET_DESCRIPTIONS: dict[str, str] = {
    "foundation": "Monorepo base only",
    "python": "Python app lane",
    "web": "Web frontend app",
    "backend": "Backend/Convex app",
    "desktop": "Desktop app",
    "mobile": "Mobile app",
    "tv": "AndroidTV app",
}

TARGET_NOTES: dict[str, str] = {
    "foundation": "Baseline workspace only. This stays mutually exclusive with all app lanes.",
    "python": "Scaffolds the Python lane under apps/python with uv-based tooling.",
    "web": "Adds the TanStack Start web frontend lane.",
    "backend": "Adds the Convex backend lane. Pair with web for fullstack auth selection.",
    "desktop": "Adds the Electron desktop lane.",
    "mobile": "Adds the Expo mobile app lane.",
    "tv": "Adds the Expo Android TV lane with remote-first starter wiring.",
}

AUTH_NOTES: dict[str, str] = {
    "clerk": "Hosted authentication stack with Clerk-oriented wiring placeholders.",
    "better-auth": "Self-hostable authentication path with Better Auth-oriented wiring placeholders.",
}

TARGET_CHOICES: tuple[str, ...] = tuple(TARGET_DESCRIPTIONS)


@dataclass(frozen=True)
class InteractiveWizardResult:
    targets: tuple[str, ...]
    auth: str | None


class NewProjectWizardApp(App[InteractiveWizardResult | None]):
    CSS = """
    Screen {
        background: #06121f;
        color: #edf4f7;
    }

    Header {
        dock: top;
    }

    Footer {
        dock: bottom;
    }

    #wizard_body {
        height: 1fr;
        padding: 1 1 0 1;
    }

    #progress_column {
        width: 22;
        min-width: 18;
        padding: 0 1 0 0;
    }

    #progress_rail {
        height: 1fr;
        border: round #1d5363;
        background: #0a1a24;
        padding: 1 1;
    }

    #main_column {
        width: 3fr;
        padding: 0 1;
    }

    #hero_panel {
        margin-bottom: 1;
    }

    #step_copy {
        margin: 0 0 1 0;
        color: #b6cdd7;
    }

    #step_switcher {
        height: 1fr;
    }

    #welcome,
    #targets,
    #auth,
    #review {
        height: 1fr;
    }

    #welcome_panel,
    #target_details,
    #auth_notes,
    #review_panel {
        height: 1fr;
    }

    #targets_layout {
        height: 1fr;
    }

    #targets_list {
        width: 2fr;
        border: round #278ea5;
        background: #0a1a24;
        padding: 1 1;
        margin-right: 1;
    }

    #target_details {
        width: 1fr;
        border: round #1d5363;
        background: #0a1a24;
        padding: 1 1;
    }

    #auth_options {
        border: round #278ea5;
        background: #0a1a24;
        padding: 1 1;
        margin-bottom: 1;
    }

    #auth_notes {
        border: round #1d5363;
        background: #0a1a24;
        padding: 1 1;
    }

    #status_message {
        min-height: 3;
        margin-top: 1;
        padding: 0 1;
        color: #f7d28a;
    }

    #actions {
        height: auto;
        align-horizontal: right;
        margin-top: 1;
    }

    #actions Button {
        margin-left: 1;
        min-width: 12;
    }

    #summary_column {
        width: 32;
        min-width: 28;
        border: round #1d5363;
        background: #0a1a24;
        padding: 1 1;
    }

    #summary_panel {
        height: 1fr;
    }
    """

    TITLE = "nurt new"
    SUB_TITLE = "Interactive project wizard"

    BINDINGS = [
        Binding("ctrl+n", "next_step", "Next"),
        Binding("ctrl+b", "prev_step", "Back"),
        Binding("ctrl+r", "confirm_step", "Confirm"),
        Binding("q", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        *,
        project_name: str,
        output_path: Path,
        initial_targets: tuple[str, ...] | None = None,
        initial_auth: str | None = None,
    ) -> None:
        super().__init__()
        self.project_name = project_name
        self.output_path = output_path
        self.current_step = WIZARD_STEP_WELCOME
        self.selected_targets = initial_targets or ("foundation",)
        self.selected_auth = initial_auth if initial_auth in AUTH_CHOICES else None
        self.highlighted_target = self.selected_targets[0]
        self.final_result: InteractiveWizardResult | None = None
        self._syncing_targets = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)

        with Horizontal(id="wizard_body"):
            with Vertical(id="progress_column"):
                yield Static(id="progress_rail")

            with Vertical(id="main_column"):
                yield Static(id="hero_panel")
                yield Static(id="step_copy")
                with ContentSwitcher(initial=WIZARD_STEP_WELCOME, id="step_switcher"):
                    yield Static(id=WIZARD_STEP_WELCOME)
                    with Vertical(id=WIZARD_STEP_TARGETS):
                        with Horizontal(id="targets_layout"):
                            yield SelectionList[str](
                                *self._build_target_selections(),
                                id="targets_list",
                            )
                            yield Static(id="target_details")
                    with Vertical(id=WIZARD_STEP_AUTH):
                        with RadioSet(id="auth_options"):
                            yield RadioButton(
                                "Clerk",
                                id="auth-clerk",
                                value=self.selected_auth == "clerk",
                            )
                            yield RadioButton(
                                "Better Auth",
                                id="auth-better-auth",
                                value=self.selected_auth == "better-auth",
                            )
                        yield Static(id="auth_notes")
                    yield Static(id=WIZARD_STEP_REVIEW)
                yield Static(id="status_message")
                with Horizontal(id="actions"):
                    yield Button("Back", id="back_button")
                    yield Button("Next", id="next_button", variant="primary")
                    yield Button("Confirm", id="confirm_button", variant="success")
                    yield Button("Cancel", id="cancel_button")

            with Vertical(id="summary_column"):
                yield Static(id="summary_panel")

        yield Footer()

    def on_mount(self) -> None:
        self._refresh_ui()

    def _build_target_selections(self) -> tuple[Selection[str], ...]:
        return tuple(
            Selection(
                Text.assemble(
                    (target, "bold white"),
                    "  ",
                    (TARGET_DESCRIPTIONS[target], "dim"),
                ),
                target,
                target in self.selected_targets,
            )
            for target in TARGET_CHOICES
        )

    def _auth_required(self) -> bool:
        return "web" in self.selected_targets and "backend" in self.selected_targets

    def _step_order(self) -> tuple[str, ...]:
        if self._auth_required():
            return (
                WIZARD_STEP_WELCOME,
                WIZARD_STEP_TARGETS,
                WIZARD_STEP_AUTH,
                WIZARD_STEP_REVIEW,
            )
        return (
            WIZARD_STEP_WELCOME,
            WIZARD_STEP_TARGETS,
            WIZARD_STEP_REVIEW,
        )

    def _step_title(self) -> str:
        titles = {
            WIZARD_STEP_WELCOME: "Kickoff",
            WIZARD_STEP_TARGETS: "Select Targets",
            WIZARD_STEP_AUTH: "Choose Auth",
            WIZARD_STEP_REVIEW: "Review Plan",
        }
        step_order = self._step_order()
        return f"Step {step_order.index(self.current_step) + 1} of {len(step_order)} - {titles[self.current_step]}"

    def _render_hero_panel(self) -> Panel:
        welcome_text = Text.assemble(
            ("Professional scaffold setup", "bold #7be0d6"),
            "\n",
            (
                "Choose targets directly, resolve auth only when needed, and keep the scaffold plan visible while you work.",
                "#d7e7ec",
            ),
        )

        details_table = Table.grid(expand=True)
        details_table.add_column(style="bold #9ad9e7", ratio=1)
        details_table.add_column(style="#edf4f7", ratio=3)
        details_table.add_row("Project", self.project_name)
        details_table.add_row("Output", str(self.output_path))

        return Panel(
            Group(welcome_text, Text(""), details_table),
            title="nurt new",
            border_style="#278ea5",
        )

    def _render_progress_rail(self) -> Panel:
        step_order = (
            WIZARD_STEP_WELCOME,
            WIZARD_STEP_TARGETS,
            WIZARD_STEP_AUTH,
            WIZARD_STEP_REVIEW,
        )
        current_position = step_order.index(self.current_step)
        auth_enabled = self._auth_required()
        lines: list[Text] = []

        for index, step in enumerate(step_order):
            label = {
                WIZARD_STEP_WELCOME: "Kickoff",
                WIZARD_STEP_TARGETS: "Targets",
                WIZARD_STEP_AUTH: "Auth",
                WIZARD_STEP_REVIEW: "Review",
            }[step]

            if step == WIZARD_STEP_AUTH and not auth_enabled:
                marker = "·"
                style = "dim"
                label = "Auth (skipped)"
            elif index < current_position:
                marker = "●"
                style = "bold #7be0d6"
            elif index == current_position:
                marker = "◉"
                style = "bold #f7d28a"
            else:
                marker = "○"
                style = "#7c9aa7"

            lines.append(Text.assemble((f"{marker} {label}", style)))
            if index < len(step_order) - 1:
                lines.append(Text("│", style="#28505c"))

        return Panel(Group(*lines), title="Flow", border_style="#1d5363")

    def _render_target_details(self) -> Panel:
        description = TARGET_DESCRIPTIONS[self.highlighted_target]
        notes = TARGET_NOTES[self.highlighted_target]
        return Panel(
            Group(
                Text(self.highlighted_target, style="bold #7be0d6"),
                Text(description, style="#edf4f7"),
                Text(""),
                Text(notes, style="#b6cdd7"),
            ),
            title="Target Details",
            border_style="#1d5363",
        )

    def _render_auth_notes(self) -> Panel:
        if self.selected_auth is None:
            body = Group(
                Text("Select an auth provider to continue.", style="#edf4f7"),
                Text(
                    "This step appears only when both web and backend are selected.",
                    style="#b6cdd7",
                ),
            )
        else:
            body = Group(
                Text(self.selected_auth, style="bold #7be0d6"),
                Text(AUTH_NOTES[self.selected_auth], style="#edf4f7"),
            )
        return Panel(body, title="Auth Notes", border_style="#1d5363")

    def _render_summary_panel(self) -> Panel:
        grid = Table.grid(expand=True, padding=(0, 1))
        grid.add_column(style="bold #9ad9e7", ratio=1)
        grid.add_column(style="#edf4f7", ratio=3)
        grid.add_row("Project", self.project_name)
        grid.add_row("Output", str(self.output_path))
        grid.add_row(
            "Targets",
            ", ".join(self.selected_targets)
            if self.selected_targets
            else "None selected",
        )

        if self._auth_required():
            auth_value = self.selected_auth or "Required"
        else:
            auth_value = "Not needed"
        grid.add_row("Auth", auth_value)

        notes: list[Text] = []
        if self._auth_required() and self.selected_auth is None:
            notes.append(
                Text("Auth is required for web + backend.", style="bold yellow")
            )
        if self.selected_targets == ("foundation",):
            notes.append(
                Text(
                    "Foundation stays exclusive to the monorepo baseline.",
                    style="#b6cdd7",
                )
            )

        renderables: list[RenderableType] = [grid]
        if notes:
            renderables.extend([Text(""), *notes])

        return Panel(
            Group(*renderables), title="Scaffold Summary", border_style="#278ea5"
        )

    def _render_review_panel(self) -> Panel:
        plan_table = Table.grid(expand=True, padding=(0, 1))
        plan_table.add_column(style="bold #9ad9e7", ratio=1)
        plan_table.add_column(style="#edf4f7", ratio=3)
        plan_table.add_row(
            "Targets",
            ", ".join(self.selected_targets)
            if self.selected_targets
            else "None selected",
        )
        plan_table.add_row(
            "Auth",
            self.selected_auth if self.selected_auth is not None else "Not required",
        )
        plan_table.add_row("Output", str(self.output_path))

        return Panel(
            Group(
                Text(
                    "Review the resolved scaffold plan before confirming.",
                    style="#edf4f7",
                ),
                Text(""),
                plan_table,
            ),
            title="Resolved Plan",
            border_style="#278ea5",
        )

    def _status_text(self) -> str:
        if self.current_step == WIZARD_STEP_WELCOME:
            return "Press Ctrl+N or use Next to begin the guided setup."
        if self.current_step == WIZARD_STEP_TARGETS and not self.selected_targets:
            return "Choose at least one target to continue."
        if self.current_step == WIZARD_STEP_AUTH and self.selected_auth is None:
            return "Select an auth provider to continue."
        if self.current_step == WIZARD_STEP_REVIEW:
            return "Confirm to hand the resolved selections back to the scaffold flow."
        return (
            "Use arrows and Space to choose targets, or mouse controls if you prefer."
        )

    def _refresh_ui(self) -> None:
        self.query_one("#hero_panel", Static).update(self._render_hero_panel())
        self.query_one("#progress_rail", Static).update(self._render_progress_rail())
        self.query_one("#step_copy", Static).update(self._step_title())
        self.query_one("#step_switcher", ContentSwitcher).current = self.current_step
        self.query_one("#summary_panel", Static).update(self._render_summary_panel())
        self.query_one("#target_details", Static).update(self._render_target_details())
        self.query_one("#auth_notes", Static).update(self._render_auth_notes())
        self.query_one("#review", Static).update(self._render_review_panel())
        self.query_one("#welcome", Static).update(
            Panel(
                Group(
                    Text(
                        "Start with target selection, then review the exact scaffold outcome.",
                        style="#edf4f7",
                    ),
                    Text(""),
                    Text("- direct multi-select for targets", style="#b6cdd7"),
                    Text("- conditional auth step for web + backend", style="#b6cdd7"),
                    Text("- persistent summary while you choose", style="#b6cdd7"),
                ),
                title="What changes in this TUI",
                border_style="#278ea5",
            )
        )
        self.query_one("#status_message", Static).update(self._status_text())
        self._refresh_actions()
        self.call_after_refresh(self._focus_current_step)

    def _refresh_actions(self) -> None:
        back_button = self.query_one("#back_button", Button)
        next_button = self.query_one("#next_button", Button)
        confirm_button = self.query_one("#confirm_button", Button)

        back_button.disabled = self.current_step == WIZARD_STEP_WELCOME
        next_button.display = self.current_step != WIZARD_STEP_REVIEW
        confirm_button.display = self.current_step == WIZARD_STEP_REVIEW

        if self.current_step == WIZARD_STEP_AUTH:
            next_button.disabled = self.selected_auth is None
        elif self.current_step == WIZARD_STEP_TARGETS:
            next_button.disabled = not self.selected_targets
        else:
            next_button.disabled = False

    def _focus_current_step(self) -> None:
        if self.current_step == WIZARD_STEP_WELCOME:
            self.query_one("#next_button", Button).focus()
            return
        if self.current_step == WIZARD_STEP_TARGETS:
            self.query_one("#targets_list", SelectionList).focus()
            return
        if self.current_step == WIZARD_STEP_AUTH:
            self.query_one("#auth_options", RadioSet).focus()
            return
        self.query_one("#confirm_button", Button).focus()

    def _sync_targets_from_widget(self, selection_list: SelectionList[str]) -> None:
        self.selected_targets = tuple(str(target) for target in selection_list.selected)
        if self.highlighted_target not in TARGET_CHOICES:
            self.highlighted_target = TARGET_CHOICES[0]
        if not self._auth_required():
            self.selected_auth = None
            radio_set = self.query_one("#auth_options", RadioSet)
            if radio_set.pressed_button is not None:
                radio_set.pressed_button.value = False
        self._refresh_ui()

    def _go_to_next_step(self) -> None:
        if self.current_step == WIZARD_STEP_WELCOME:
            self.current_step = WIZARD_STEP_TARGETS
        elif self.current_step == WIZARD_STEP_TARGETS:
            self.current_step = (
                WIZARD_STEP_AUTH if self._auth_required() else WIZARD_STEP_REVIEW
            )
        elif self.current_step == WIZARD_STEP_AUTH:
            self.current_step = WIZARD_STEP_REVIEW
        self._refresh_ui()

    def _go_to_previous_step(self) -> None:
        if self.current_step == WIZARD_STEP_TARGETS:
            self.current_step = WIZARD_STEP_WELCOME
        elif self.current_step == WIZARD_STEP_AUTH:
            self.current_step = WIZARD_STEP_TARGETS
        elif self.current_step == WIZARD_STEP_REVIEW:
            self.current_step = (
                WIZARD_STEP_AUTH if self._auth_required() else WIZARD_STEP_TARGETS
            )
        self._refresh_ui()

    def action_next_step(self) -> None:
        if self.current_step == WIZARD_STEP_REVIEW:
            return
        if self.current_step == WIZARD_STEP_TARGETS and not self.selected_targets:
            return
        if self.current_step == WIZARD_STEP_AUTH and self.selected_auth is None:
            return
        self._go_to_next_step()

    def action_prev_step(self) -> None:
        if self.current_step == WIZARD_STEP_WELCOME:
            return
        self._go_to_previous_step()

    def action_confirm_step(self) -> None:
        if self.current_step != WIZARD_STEP_REVIEW:
            return
        self.final_result = InteractiveWizardResult(
            targets=self.selected_targets,
            auth=self.selected_auth if self._auth_required() else None,
        )
        self.exit(self.final_result)

    def action_cancel(self) -> None:
        self.final_result = None
        self.exit(None)

    @on(Button.Pressed, "#back_button")
    def _handle_back_button(self) -> None:
        self.action_prev_step()

    @on(Button.Pressed, "#next_button")
    def _handle_next_button(self) -> None:
        self.action_next_step()

    @on(Button.Pressed, "#confirm_button")
    def _handle_confirm_button(self) -> None:
        self.action_confirm_step()

    @on(Button.Pressed, "#cancel_button")
    def _handle_cancel_button(self) -> None:
        self.action_cancel()

    @on(SelectionList.SelectionHighlighted, "#targets_list")
    def _handle_target_highlighted(
        self, event: SelectionList.SelectionHighlighted[str]
    ) -> None:
        self.highlighted_target = str(event.selection.value)
        self.query_one("#target_details", Static).update(self._render_target_details())

    @on(SelectionList.SelectionToggled, "#targets_list")
    def _handle_target_toggled(
        self, event: SelectionList.SelectionToggled[str]
    ) -> None:
        if self._syncing_targets:
            return

        toggled_target = str(event.selection.value)
        selection_list = event.selection_list

        self._syncing_targets = True
        if toggled_target == "foundation" and "foundation" in selection_list.selected:
            for target in TARGET_CHOICES:
                if target != "foundation":
                    selection_list.deselect(target)
        elif (
            toggled_target != "foundation" and toggled_target in selection_list.selected
        ):
            selection_list.deselect("foundation")
        self._syncing_targets = False

        self._sync_targets_from_widget(selection_list)

    @on(SelectionList.SelectedChanged, "#targets_list")
    def _handle_targets_changed(
        self, event: SelectionList.SelectedChanged[str]
    ) -> None:
        self._sync_targets_from_widget(event.selection_list)

    @on(RadioSet.Changed, "#auth_options")
    def _handle_auth_changed(self, event: RadioSet.Changed) -> None:
        pressed_id = event.pressed.id
        if pressed_id == "auth-clerk":
            self.selected_auth = "clerk"
        elif pressed_id == "auth-better-auth":
            self.selected_auth = "better-auth"
        else:
            self.selected_auth = None
        self._refresh_ui()


def run_interactive_wizard(
    *,
    project_name: str,
    output_path: Path,
    initial_targets: tuple[str, ...] | None = None,
    initial_auth: str | None = None,
) -> InteractiveWizardResult | None:
    return NewProjectWizardApp(
        project_name=project_name,
        output_path=output_path,
        initial_targets=initial_targets,
        initial_auth=initial_auth,
    ).run()
