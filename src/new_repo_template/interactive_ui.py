from __future__ import annotations

import os
import sys
from dataclasses import dataclass


VALID_UI_MODES = {"auto", "plain", "rich"}
SIMULATE_RICH_UNAVAILABLE_ENV = "NURT_SIMULATE_RICH_UNAVAILABLE"

TARGET_DESCRIPTIONS: dict[str, str] = {
    "foundation": "Monorepo base only",
    "python": "Python app lane",
    "web": "Web frontend app",
    "backend": "Backend/Convex app",
    "desktop": "Desktop app",
    "mobile": "Mobile app",
    "tv": "AndroidTV app",
}


@dataclass(frozen=True)
class InteractiveUIConfig:
    mode: str
    use_rich: bool
    warning: str | None


def _is_truthy_env(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() not in {"", "0", "false", "no", "none"}


def _rich_is_available() -> bool:
    if _is_truthy_env(os.environ.get(SIMULATE_RICH_UNAVAILABLE_ENV)):
        return False

    try:
        import rich  # noqa: F401
    except ImportError:
        return False
    return True


def resolve_ui_config() -> InteractiveUIConfig:
    raw_mode = os.environ.get("NURT_UI_MODE", "auto").strip().lower()
    mode = raw_mode if raw_mode in VALID_UI_MODES else "auto"
    rich_available = _rich_is_available()
    interactive_tty = sys.stdin.isatty() and sys.stdout.isatty()

    if mode == "plain":
        return InteractiveUIConfig(mode=mode, use_rich=False, warning=None)

    if mode == "rich":
        if rich_available:
            return InteractiveUIConfig(mode=mode, use_rich=True, warning=None)
        return InteractiveUIConfig(
            mode=mode,
            use_rich=False,
            warning=(
                "Rich/Textual UI unavailable; falling back to plain prompts. "
                "Install `rich` and `textual` for enhanced interactive UI."
            ),
        )

    if rich_available and interactive_tty:
        return InteractiveUIConfig(mode=mode, use_rich=True, warning=None)

    return InteractiveUIConfig(mode=mode, use_rich=False, warning=None)


def render_target_menu(
    *, config: InteractiveUIConfig, targets: tuple[str, ...]
) -> None:
    if not config.use_rich:
        print("nurt new interactive mode")
        print("Select targets (comma-separated):")
        for index, target in enumerate(targets, start=1):
            print(f"  {index}) {target}")
        return

    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", justify="right", style="bold yellow")
    table.add_column("Target", style="bold white")
    table.add_column("Description", style="green")
    for index, target in enumerate(targets, start=1):
        table.add_row(str(index), target, TARGET_DESCRIPTIONS.get(target, ""))

    console.print(Panel("nurt new interactive mode", style="cyan"))
    console.print("Select targets (comma-separated):")
    console.print(table)


def render_auth_menu(*, config: InteractiveUIConfig) -> None:
    if not config.use_rich:
        print("Select auth provider for web+backend:")
        print("  1) clerk")
        print("  2) better-auth")
        return

    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", justify="right", style="bold yellow")
    table.add_column("Provider", style="bold white")
    table.add_column("Notes", style="green")
    table.add_row("1", "clerk", "Hosted auth stack")
    table.add_row("2", "better-auth", "Self-hostable auth stack")

    console.print(Panel("Auth provider selection", style="cyan"))
    console.print("Select auth provider for web+backend:")
    console.print(table)


def ask_user_input(*, config: InteractiveUIConfig, prompt: str, default: str) -> str:
    if not config.use_rich:
        value = input(prompt)
        return value.strip()

    from rich.prompt import Prompt

    value = Prompt.ask(prompt.rstrip(), default=default)
    return value.strip()
