"""zen-agents: Agent-based session management TUI.

Main Textual application with agent dependency injection.
"""

import shutil
import sys
from pathlib import Path

from textual.app import App
from textual.binding import Binding

from ..ground import ZenGround, zen_ground
from ..tmux.capture import TmuxCapture, capture_output
from .screens.main import MainScreen
from .styles import BASE_CSS, ThemeName, get_theme, DEFAULT_THEME


def check_dependencies() -> None:
    """Check for required dependencies.

    Exits with error if tmux is missing.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not shutil.which("tmux"):
        errors.append("tmux is not installed or not in PATH")

    if not shutil.which("claude"):
        warnings.append("claude CLI not found - Claude sessions won't work")

    if errors:
        print("Error: Missing required dependencies:\n")
        for e in errors:
            print(f"  - {e}")
        print("\nPlease install tmux: https://github.com/tmux/tmux")
        sys.exit(1)

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - {w}")
        print()


class ZenAgentsApp(App):
    """The main zen-agents application.

    Agent-based architecture:
    - ZenGround: Empirical seed (config + sessions + tmux facts)
    - ZenJudge: Validation pipelines
    - TmuxCapture: Output capture agent
    - SessionContradict/Sublate: Conflict resolution

    All services are agents, injected at construction.
    """

    TITLE = "zen-agents"

    BINDINGS = [
        Binding("ctrl+s", "screenshot", "Screenshot", show=False),
    ]

    def __init__(
        self,
        ground: ZenGround | None = None,
        capture: TmuxCapture | None = None,
        working_dir: Path | None = None,
        focus_tmux_session: str | None = None,
        theme: ThemeName | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Inject agents (use singletons if not provided)
        self._ground = ground or zen_ground
        self._capture = capture or capture_output
        self._working_dir = working_dir or Path.cwd()
        self._focus_tmux_session = focus_tmux_session
        self._current_theme = theme or DEFAULT_THEME

        # Generate CSS with theme variables
        theme_obj = get_theme(self._current_theme)
        self.CSS = theme_obj.to_css_vars() + BASE_CSS + """
        Screen {
            background: $background;
        }
        """

    def set_theme(self, theme_name: ThemeName) -> None:
        """Switch to a different color theme."""
        self._current_theme = theme_name
        theme = get_theme(theme_name)

        # Apply theme by updating design system dark mode
        self.design = self.design.copy_with(
            dark=(theme_name != ThemeName.LIGHT),
        )

        # Note: Full color theme switching would require reloading CSS
        # or using dynamic CSS injection. For now, this handles dark/light.
        self.refresh()

    def on_mount(self) -> None:
        """Push the main screen."""
        self.push_screen(MainScreen(
            ground=self._ground,
            capture=self._capture,
        ))

    async def action_quit(self) -> None:
        """Quit the app, saving state first."""
        await self._ground.save()
        self.exit()


def main():
    """Run the zen-agents application."""
    import subprocess

    check_dependencies()

    # Create agent instances (persist across attach/detach cycles)
    ground = ZenGround()
    capture = capture_output

    focus_tmux_session = None
    while True:
        app = ZenAgentsApp(
            ground=ground,
            capture=capture,
            focus_tmux_session=focus_tmux_session,
        )
        result = app.run()

        # Handle attach exit - attach to tmux then return to TUI
        if result and isinstance(result, str) and result.startswith("attach:"):
            tmux_name = result.split(":", 1)[1]
            subprocess.run(["tmux", "attach", "-t", tmux_name])
            focus_tmux_session = tmux_name
            continue

        # Any other exit breaks the loop
        break


if __name__ == "__main__":
    main()
