"""
zen-agents: A contemplative TUI for managing parallel AI sessions.

Every iteration is Fix. Every conflict is Contradict.
Every pipeline is Compose. Every validation is Judge. Every fact is Ground.
"""

from textual.app import App

from .services import SessionManager, StateRefresher, TmuxService
from .screens import MainScreen


class ZenAgentsApp(App):
    """
    The zen-agents TUI application.

    A contemplative interface for managing parallel AI assistant sessions
    (Claude, Codex, Gemini, OpenRouter, Shell) with tmux isolation.
    """

    TITLE = "zen-agents"
    SUB_TITLE = "contemplative AI session management"

    CSS = """
    Screen {
        background: $background;
    }

    Header {
        background: $primary;
    }

    Footer {
        background: $surface;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("n", "new_session", "New Session"),
        ("?", "help", "Help"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tmux = TmuxService()
        self._manager = SessionManager(tmux=self._tmux)
        self._refresher = StateRefresher(
            manager=self._manager,
            poll_interval=1.0,
        )

    def on_mount(self) -> None:
        """Push the main screen on mount."""
        self.push_screen(MainScreen(
            manager=self._manager,
            refresher=self._refresher,
        ))

    async def action_quit(self) -> None:
        """Quit the application."""
        # Stop the refresher
        await self._refresher.stop()
        self.exit()

    def action_new_session(self) -> None:
        """Create a new session (delegate to screen)."""
        if isinstance(self.screen, MainScreen):
            self.screen.action_new_session()

    def action_help(self) -> None:
        """Show help."""
        if isinstance(self.screen, MainScreen):
            self.screen.action_help()


def main():
    """Main entry point."""
    app = ZenAgentsApp()
    app.run()


if __name__ == "__main__":
    main()
