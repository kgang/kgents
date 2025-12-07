"""OutputView widget for displaying session output."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Static, RichLog


class OutputHeader(Static):
    """Header showing current session context."""

    DEFAULT_CSS = """
    OutputHeader {
        height: 2;
        padding: 0 1;
        background: $surface;
        border-bottom: solid $surface-lighten-1;
    }

    OutputHeader .session-name {
        color: $text;
    }

    OutputHeader .state {
        color: $text-muted;
    }
    """

    session_name: reactive[str] = reactive("")
    state: reactive[str] = reactive("")
    glyph: reactive[str] = reactive("")

    def render(self) -> str:
        if not self.session_name:
            return "  [dim]no session selected[/dim]"
        return f"  {self.glyph} {self.session_name}  [dim]{self.state}[/dim]"


class OutputView(Vertical):
    """Container for session output with header context.

    Provides eye-strain optimization by echoing the selected session
    in the header, reducing need to scan back to session list.
    """

    DEFAULT_CSS = """
    OutputView {
        width: 100%;
        height: 100%;
    }

    OutputView RichLog {
        height: 1fr;
        scrollbar-gutter: stable;
    }
    """

    def compose(self) -> ComposeResult:
        yield OutputHeader(id="output-header")
        yield RichLog(id="output-log", highlight=True, markup=True)

    def update_session(
        self,
        session_name: str,
        output: str,
        glyph: str = "",
        state: str = "",
        **kwargs,
    ) -> None:
        """Update the output view with session content.

        Args:
            session_name: Name of the session
            output: Raw output content
            glyph: Status glyph (e.g., >>> for running)
            state: State description (e.g., "active", "paused")
            **kwargs: Additional context (ignored for now)
        """
        header = self.query_one("#output-header", OutputHeader)
        header.session_name = session_name
        header.state = state
        header.glyph = glyph

        log = self.query_one("#output-log", RichLog)
        log.clear()
        if output:
            for line in output.splitlines():
                log.write(line)
        else:
            log.write("[dim]no output yet[/dim]")

    def clear(self) -> None:
        """Clear the output view."""
        header = self.query_one("#output-header", OutputHeader)
        header.session_name = ""
        header.state = ""
        header.glyph = ""

        log = self.query_one("#output-log", RichLog)
        log.clear()
