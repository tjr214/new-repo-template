from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable

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
ALL_WIZARD_STEPS: tuple[str, ...] = (
    WIZARD_STEP_WELCOME,
    WIZARD_STEP_TARGETS,
    WIZARD_STEP_AUTH,
    WIZARD_STEP_REVIEW,
)

COMPACT_LAYOUT_WIDTH = 100
COMPACT_LAYOUT_HEIGHT = 26

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
class WizardStepDefinition:
    key: str
    label: str
    title: str
    description: str


STEP_DEFINITIONS: dict[str, WizardStepDefinition] = {
    WIZARD_STEP_WELCOME: WizardStepDefinition(
        key=WIZARD_STEP_WELCOME,
        label="Kickoff",
        title="Confirm project context",
        description="Start from the resolved project name and output path before choosing scaffold targets.",
    ),
    WIZARD_STEP_TARGETS: WizardStepDefinition(
        key=WIZARD_STEP_TARGETS,
        label="Targets",
        title="Select scaffold targets",
        description="Use direct keyboard or mouse selection and keep foundation exclusive from app lanes.",
    ),
    WIZARD_STEP_AUTH: WizardStepDefinition(
        key=WIZARD_STEP_AUTH,
        label="Auth",
        title="Resolve auth only when required",
        description="Choose the auth strategy only for the web plus backend fullstack path.",
    ),
    WIZARD_STEP_REVIEW: WizardStepDefinition(
        key=WIZARD_STEP_REVIEW,
        label="Review",
        title="Review the resolved plan",
        description="Confirm the exact scaffold inputs that will be handed back to the CLI for deterministic generation.",
    ),
}


def _normalize_targets(selected_targets: Iterable[str] | None) -> tuple[str, ...]:
    source = tuple(selected_targets or ("foundation",))
    seen: set[str] = set()
    normalized: list[str] = []

    for target in source:
        if target in TARGET_CHOICES and target not in seen:
            normalized.append(target)
            seen.add(target)

    if not normalized:
        return ("foundation",)

    if "foundation" in normalized and len(normalized) > 1:
        if normalized[-1] == "foundation":
            return ("foundation",)
        normalized = [target for target in normalized if target != "foundation"]

    return tuple(target for target in TARGET_CHOICES if target in normalized)


@dataclass(frozen=True)
class InteractiveWizardResult:
    targets: tuple[str, ...]
    auth: str | None


@dataclass(frozen=True)
class WizardState:
    project_name: str
    output_path: Path
    current_step: str
    selected_targets: tuple[str, ...]
    selected_auth: str | None
    highlighted_target: str

    @classmethod
    def create(
        cls,
        *,
        project_name: str,
        output_path: Path,
        initial_targets: tuple[str, ...] | None,
        initial_auth: str | None,
    ) -> WizardState:
        selected_targets = _normalize_targets(initial_targets)
        selected_auth = (
            initial_auth
            if initial_auth in AUTH_CHOICES
            and "web" in selected_targets
            and "backend" in selected_targets
            else None
        )
        return cls(
            project_name=project_name,
            output_path=output_path,
            current_step=WIZARD_STEP_WELCOME,
            selected_targets=selected_targets,
            selected_auth=selected_auth,
            highlighted_target=selected_targets[0],
        )._clamp_step()

    @property
    def auth_required(self) -> bool:
        return "web" in self.selected_targets and "backend" in self.selected_targets

    @property
    def step_order(self) -> tuple[str, ...]:
        if self.auth_required:
            return ALL_WIZARD_STEPS
        return (
            WIZARD_STEP_WELCOME,
            WIZARD_STEP_TARGETS,
            WIZARD_STEP_REVIEW,
        )

    @property
    def active_step(self) -> WizardStepDefinition:
        return STEP_DEFINITIONS[self.current_step]

    @property
    def step_title(self) -> str:
        return (
            f"Step {self.step_order.index(self.current_step) + 1} "
            f"of {len(self.step_order)} - {self.active_step.title}"
        )

    @property
    def resolved_auth(self) -> str | None:
        return self.selected_auth if self.auth_required else None

    def with_targets(self, selected_targets: Iterable[str]) -> WizardState:
        normalized_targets = _normalize_targets(selected_targets)
        highlighted_target = self.highlighted_target
        if highlighted_target not in normalized_targets:
            highlighted_target = normalized_targets[0]

        selected_auth = (
            self.selected_auth
            if "web" in normalized_targets and "backend" in normalized_targets
            else None
        )
        return replace(
            self,
            selected_targets=normalized_targets,
            selected_auth=selected_auth,
            highlighted_target=highlighted_target,
        )._clamp_step()

    def with_highlighted_target(self, highlighted_target: str) -> WizardState:
        if highlighted_target not in TARGET_CHOICES:
            return self
        return replace(self, highlighted_target=highlighted_target)

    def with_selected_auth(self, selected_auth: str | None) -> WizardState:
        resolved_auth = (
            selected_auth
            if selected_auth in AUTH_CHOICES and self.auth_required
            else None
        )
        return replace(self, selected_auth=resolved_auth)

    def next_step(self) -> WizardState:
        if self.current_step == WIZARD_STEP_TARGETS and not self.selected_targets:
            return self
        if self.current_step == WIZARD_STEP_AUTH and self.selected_auth is None:
            return self

        step_order = self.step_order
        current_index = step_order.index(self.current_step)
        if current_index >= len(step_order) - 1:
            return self
        return replace(self, current_step=step_order[current_index + 1])._clamp_step()

    def previous_step(self) -> WizardState:
        step_order = self.step_order
        current_index = step_order.index(self.current_step)
        if current_index == 0:
            return self
        return replace(self, current_step=step_order[current_index - 1])._clamp_step()

    def build_result(self) -> InteractiveWizardResult:
        return InteractiveWizardResult(
            targets=self.selected_targets,
            auth=self.resolved_auth,
        )

    def _clamp_step(self) -> WizardState:
        if self.current_step in self.step_order:
            return self
        return replace(self, current_step=self.step_order[-1])


class NewProjectWizardApp(App[InteractiveWizardResult | None]):
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

    #wizard_body {
        height: 1fr;
        padding: 1 1 0 1;
        overflow-y: auto;
    }

    #progress_column {
        width: 24;
        min-width: 20;
        padding: 0 1 0 0;
    }

    #progress_rail {
        border: round #2b6674;
        background: #0b1d28;
        padding: 1 1;
    }

    #main_column {
        width: 3fr;
        min-width: 48;
        padding: 0 1;
    }

    #hero_panel {
        margin-bottom: 1;
    }

    #step_copy {
        margin: 0 0 1 0;
        color: #c5d8de;
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

    #targets_layout {
        height: 1fr;
    }

    #targets_list {
        width: 2fr;
        min-width: 32;
        border: round #3f9cae;
        background: #0b1d28;
        padding: 1 1;
        margin-right: 1;
    }

    #target_details,
    #auth_notes,
    #summary_column {
        border: round #2b6674;
        background: #0b1d28;
        padding: 1 1;
    }

    #target_details {
        width: 1fr;
        min-width: 24;
    }

    #auth_options {
        border: round #3f9cae;
        background: #0b1d28;
        padding: 1 1;
        margin-bottom: 1;
    }

    #status_message {
        min-height: 3;
        margin-top: 1;
        padding: 0 1;
        color: #f5cf85;
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
        width: 34;
        min-width: 28;
    }

    #summary_panel {
        height: auto;
    }

    Screen.compact #wizard_body {
        layout: vertical;
        padding-top: 0;
    }

    Screen.compact #progress_column,
    Screen.compact #main_column,
    Screen.compact #summary_column {
        width: auto;
        min-width: 0;
        padding: 0;
    }

    Screen.compact #progress_column {
        margin-bottom: 1;
    }

    Screen.compact #summary_column {
        margin-top: 1;
    }

    Screen.compact #step_switcher,
    Screen.compact #welcome,
    Screen.compact #targets,
    Screen.compact #auth,
    Screen.compact #review,
    Screen.compact #targets_layout,
    Screen.compact #progress_rail,
    Screen.compact #target_details,
    Screen.compact #auth_notes,
    Screen.compact #summary_panel {
        height: auto;
    }

    Screen.compact #targets_layout {
        layout: vertical;
    }

    Screen.compact #targets_list {
        width: auto;
        min-width: 0;
        margin-right: 0;
        margin-bottom: 1;
    }

    Screen.compact #actions {
        margin-top: 0;
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
        self.state = WizardState.create(
            project_name=project_name,
            output_path=output_path,
            initial_targets=initial_targets,
            initial_auth=initial_auth,
        )
        self.final_result: InteractiveWizardResult | None = None
        self._syncing_targets = False
        self._syncing_auth = False

    @property
    def current_step(self) -> str:
        return self.state.current_step

    @property
    def selected_targets(self) -> tuple[str, ...]:
        return self.state.selected_targets

    @property
    def selected_auth(self) -> str | None:
        return self.state.selected_auth

    @property
    def highlighted_target(self) -> str:
        return self.state.highlighted_target

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
                                value=self.state.selected_auth == "clerk",
                            )
                            yield RadioButton(
                                "Better Auth",
                                id="auth-better-auth",
                                value=self.state.selected_auth == "better-auth",
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
        self._refresh_responsive_mode()
        self._refresh_ui()

    def on_resize(self) -> None:
        if not self.is_mounted:
            return
        self._refresh_responsive_mode()
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
                target in self.state.selected_targets,
            )
            for target in TARGET_CHOICES
        )

    def _is_compact_layout(self) -> bool:
        return (
            self.size.width < COMPACT_LAYOUT_WIDTH
            or self.size.height < COMPACT_LAYOUT_HEIGHT
        )

    def _refresh_responsive_mode(self) -> None:
        screen = self.screen
        if self._is_compact_layout():
            if not screen.has_class("compact"):
                screen.add_class("compact")
            return
        if screen.has_class("compact"):
            screen.remove_class("compact")

    def _set_state(self, new_state: WizardState) -> None:
        if new_state == self.state:
            return
        self.state = new_state
        self._refresh_ui()

    def _render_hero_panel(self) -> Panel:
        eyebrow = Text.assemble(
            ("nurt new", "bold #79e0d4"),
            "  ",
            (self.state.active_step.label.upper(), "bold #f5cf85"),
        )
        support_copy = Text(
            "A typed Textual wizard that keeps scaffold decisions visible and hands a deterministic plan back to the CLI.",
            style="#d7e7ec",
        )

        details_table = Table.grid(expand=True)
        details_table.add_column(style="bold #95dbe8", ratio=1)
        details_table.add_column(style="#edf6f7", ratio=3)
        details_table.add_row("Project", self.state.project_name)
        details_table.add_row("Output", str(self.state.output_path))

        return Panel(
            Group(eyebrow, Text(""), support_copy, Text(""), details_table),
            title="Scaffold Context",
            border_style="#3f9cae",
        )

    def _render_progress_rail(self) -> Panel:
        current_position = ALL_WIZARD_STEPS.index(self.state.current_step)
        lines: list[Text] = []

        if self._is_compact_layout():
            compact_flow = Text()
            for index, step in enumerate(ALL_WIZARD_STEPS):
                if index:
                    compact_flow.append("  /  ", style="#315c67")
                label = STEP_DEFINITIONS[step].label
                if step == WIZARD_STEP_AUTH and not self.state.auth_required:
                    compact_flow.append(f"{index + 1}. {label} skip", style="dim")
                elif index < current_position:
                    compact_flow.append(f"{index + 1}. {label}", style="bold #79e0d4")
                elif index == current_position:
                    compact_flow.append(f"{index + 1}. {label}", style="bold #f5cf85")
                else:
                    compact_flow.append(f"{index + 1}. {label}", style="#7c9aa7")
            return Panel(compact_flow, title="Flow", border_style="#2b6674")

        for index, step in enumerate(ALL_WIZARD_STEPS):
            label = STEP_DEFINITIONS[step].label
            if step == WIZARD_STEP_AUTH and not self.state.auth_required:
                marker = "·"
                style = "dim"
                label = f"{label} (skipped)"
            elif index < current_position:
                marker = "●"
                style = "bold #79e0d4"
            elif index == current_position:
                marker = "◉"
                style = "bold #f5cf85"
            else:
                marker = "○"
                style = "#7c9aa7"

            lines.append(Text.assemble((f"{marker} {label}", style)))
            if index < len(ALL_WIZARD_STEPS) - 1:
                lines.append(Text("│", style="#315c67"))

        return Panel(Group(*lines), title="Flow", border_style="#2b6674")

    def _render_target_details(self) -> Panel:
        description = TARGET_DESCRIPTIONS[self.state.highlighted_target]
        notes = TARGET_NOTES[self.state.highlighted_target]
        return Panel(
            Group(
                Text(self.state.highlighted_target, style="bold #79e0d4"),
                Text(description, style="#edf6f7"),
                Text(""),
                Text(notes, style="#c5d8de"),
            ),
            title="Target Details",
            border_style="#2b6674",
        )

    def _render_auth_notes(self) -> Panel:
        if self.state.selected_auth is None:
            body = Group(
                Text("Select an auth provider to continue.", style="#edf6f7"),
                Text(
                    "This step appears only when both web and backend are selected.",
                    style="#c5d8de",
                ),
            )
        else:
            body = Group(
                Text(self.state.selected_auth, style="bold #79e0d4"),
                Text(AUTH_NOTES[self.state.selected_auth], style="#edf6f7"),
            )
        return Panel(body, title="Auth Notes", border_style="#2b6674")

    def _render_summary_panel(self) -> Panel:
        grid = Table.grid(expand=True, padding=(0, 1))
        grid.add_column(style="bold #95dbe8", ratio=1)
        grid.add_column(style="#edf6f7", ratio=3)
        grid.add_row("Step", self.state.active_step.label)
        grid.add_row("Project", self.state.project_name)
        grid.add_row("Output", str(self.state.output_path))
        grid.add_row("Targets", ", ".join(self.state.selected_targets))
        grid.add_row(
            "Auth",
            self.state.resolved_auth
            or ("Required" if self.state.auth_required else "Not needed"),
        )

        notes: list[RenderableType] = []
        if self.state.auth_required and self.state.selected_auth is None:
            notes.append(
                Text("Auth is still required for web + backend.", style="bold yellow")
            )
        if self.state.selected_targets == ("foundation",):
            notes.append(
                Text(
                    "Foundation stays exclusive to the monorepo baseline.",
                    style="#c5d8de",
                )
            )

        renderables: list[RenderableType] = [grid]
        if notes:
            renderables.extend([Text(""), *notes])

        return Panel(
            Group(*renderables),
            title="Scaffold Summary",
            border_style="#3f9cae",
        )

    def _render_review_panel(self) -> Panel:
        plan_table = Table.grid(expand=True, padding=(0, 1))
        plan_table.add_column(style="bold #95dbe8", ratio=1)
        plan_table.add_column(style="#edf6f7", ratio=3)
        plan_table.add_row("Targets", ", ".join(self.state.selected_targets))
        plan_table.add_row("Auth", self.state.resolved_auth or "Not required")
        plan_table.add_row("Output", str(self.state.output_path))

        return Panel(
            Group(
                Text(
                    "Confirm exits the wizard, returns this typed plan to the CLI, then starts scaffold generation and lockfile work.",
                    style="#edf6f7",
                ),
                Text(""),
                plan_table,
            ),
            title="Resolved Plan",
            border_style="#3f9cae",
        )

    def _render_welcome_panel(self) -> Panel:
        return Panel(
            Group(
                Text(
                    "Move through target selection, optional auth, and a final review before any scaffold work begins.",
                    style="#edf6f7",
                ),
                Text(""),
                Text(
                    "- direct target multi-select with keyboard or mouse",
                    style="#c5d8de",
                ),
                Text(
                    "- responsive layout that stacks cleanly for 80x24 terminals",
                    style="#c5d8de",
                ),
                Text(
                    "- persistent summary so review never feels disconnected",
                    style="#c5d8de",
                ),
            ),
            title="What this wizard optimizes",
            border_style="#3f9cae",
        )

    def _render_step_copy(self) -> Text:
        return Text.assemble(
            (self.state.step_title, "bold #edf6f7"),
            "\n",
            (self.state.active_step.description, "#c5d8de"),
        )

    def _status_text(self) -> str:
        if self.state.current_step == WIZARD_STEP_WELCOME:
            return "Press Ctrl+N or use Next to begin the guided setup."
        if (
            self.state.current_step == WIZARD_STEP_TARGETS
            and not self.state.selected_targets
        ):
            return "Choose at least one target to continue."
        if (
            self.state.current_step == WIZARD_STEP_AUTH
            and self.state.selected_auth is None
        ):
            return "Select an auth provider to continue."
        if self.state.current_step == WIZARD_STEP_REVIEW:
            return "Confirm to hand the resolved selections back to the scaffold flow."
        return (
            "Use arrows and Space to choose targets, or mouse controls if you prefer."
        )

    def _sync_auth_controls(self) -> None:
        radio_set = self.query_one("#auth_options", RadioSet)
        current_button = radio_set.pressed_button
        current_id = current_button.id if current_button is not None else None
        desired_id = (
            f"auth-{self.state.selected_auth}"
            if self.state.selected_auth is not None
            else None
        )
        if current_id == desired_id:
            return

        self._syncing_auth = True
        try:
            if desired_id is None:
                if current_button is not None:
                    current_button.value = False
            else:
                self.query_one(f"#{desired_id}", RadioButton).value = True
        finally:
            self._syncing_auth = False

    def _refresh_ui(self) -> None:
        self.query_one("#hero_panel", Static).update(self._render_hero_panel())
        self.query_one("#progress_rail", Static).update(self._render_progress_rail())
        self.query_one("#step_copy", Static).update(self._render_step_copy())
        self.query_one(
            "#step_switcher", ContentSwitcher
        ).current = self.state.current_step
        self.query_one("#summary_panel", Static).update(self._render_summary_panel())
        self.query_one("#target_details", Static).update(self._render_target_details())
        self.query_one("#auth_notes", Static).update(self._render_auth_notes())
        self.query_one("#review", Static).update(self._render_review_panel())
        self.query_one("#welcome", Static).update(self._render_welcome_panel())
        self.query_one("#status_message", Static).update(self._status_text())
        self._sync_auth_controls()
        self._refresh_actions()
        self.call_after_refresh(self._focus_current_step)

    def _refresh_actions(self) -> None:
        back_button = self.query_one("#back_button", Button)
        next_button = self.query_one("#next_button", Button)
        confirm_button = self.query_one("#confirm_button", Button)

        back_button.disabled = self.state.current_step == WIZARD_STEP_WELCOME
        next_button.display = self.state.current_step != WIZARD_STEP_REVIEW
        confirm_button.display = self.state.current_step == WIZARD_STEP_REVIEW

        if self.state.current_step == WIZARD_STEP_AUTH:
            next_button.disabled = self.state.selected_auth is None
        elif self.state.current_step == WIZARD_STEP_TARGETS:
            next_button.disabled = not self.state.selected_targets
        else:
            next_button.disabled = False

    def _focus_current_step(self) -> None:
        if self.state.current_step == WIZARD_STEP_WELCOME:
            self.query_one("#next_button", Button).focus()
            return
        if self.state.current_step == WIZARD_STEP_TARGETS:
            self.query_one("#targets_list", SelectionList).focus()
            return
        if self.state.current_step == WIZARD_STEP_AUTH:
            self.query_one("#auth_options", RadioSet).focus()
            return
        self.query_one("#confirm_button", Button).focus()

    def _sync_targets_from_widget(self, selection_list: SelectionList[str]) -> None:
        self._set_state(self.state.with_targets(selection_list.selected))

    def action_next_step(self) -> None:
        if self.state.current_step == WIZARD_STEP_REVIEW:
            return
        self._set_state(self.state.next_step())

    def action_prev_step(self) -> None:
        if self.state.current_step == WIZARD_STEP_WELCOME:
            return
        self._set_state(self.state.previous_step())

    def action_confirm_step(self) -> None:
        if self.state.current_step != WIZARD_STEP_REVIEW:
            return
        self.final_result = self.state.build_result()
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
        new_state = self.state.with_highlighted_target(str(event.selection.value))
        if new_state == self.state:
            return
        self.state = new_state
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
        if self._syncing_auth:
            return
        pressed_id = event.pressed.id
        if pressed_id == "auth-clerk":
            self._set_state(self.state.with_selected_auth("clerk"))
        elif pressed_id == "auth-better-auth":
            self._set_state(self.state.with_selected_auth("better-auth"))
        else:
            self._set_state(self.state.with_selected_auth(None))


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
