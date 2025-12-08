"""Log Viewer Widget - Display session output with LLM analysis.

A contemplative viewer for session logs, with integrated analysis panel
powered by kgents HypothesisEngine.
"""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, RichLog, Static
from rich.markdown import Markdown


class LogViewer(Vertical):
    """
    Session log viewer with integrated analysis panel.

    Displays raw session output (from tmux pane capture) and provides
    LLM-powered analysis via the "Analyze" button.

    Layout:
        - Log Container (70%): Raw session output with syntax highlighting
        - Analysis Container (30%): Markdown-rendered analysis from HypothesisEngine

    Messages:
        AnalyzeRequested: Emitted when user clicks Analyze button
    """

    DEFAULT_CSS = """
    LogViewer {
        height: 100%;
        border: solid $surface-lighten-1;
        margin-top: 1;
    }

    LogViewer #log-container {
        height: 70%;
        border-bottom: solid $surface-lighten-1;
    }

    LogViewer #log-header {
        dock: top;
        height: 1;
        padding: 0 1;
        background: $surface;
        color: $text-muted;
    }

    LogViewer #raw-log {
        height: 1fr;
        scrollbar-gutter: stable;
    }

    LogViewer #analysis-container {
        height: 30%;
    }

    LogViewer #analysis-header {
        dock: top;
        height: 3;
        padding: 0 1;
        background: $surface;
    }

    LogViewer #analysis-header Static {
        width: 1fr;
        padding-top: 1;
    }

    LogViewer #analysis-header Button {
        margin-left: 1;
    }

    LogViewer #analysis-panel {
        height: 1fr;
        padding: 0 1;
        overflow-y: auto;
    }

    LogViewer .empty-state {
        color: $text-muted;
        text-align: center;
        padding: 1;
    }

    LogViewer .analyzing {
        color: $warning;
    }
    """

    class AnalyzeRequested(Message):
        """Emitted when user requests log analysis."""
        pass

    # Reactive properties
    log_content: reactive[str] = reactive("")
    analysis_content: reactive[str] = reactive("")
    is_analyzing: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        with Vertical(id="log-container"):
            yield Static("Session Output", id="log-header")
            yield RichLog(id="raw-log", wrap=True, highlight=True)

        with Vertical(id="analysis-container"):
            with Horizontal(id="analysis-header"):
                yield Static("Analysis")
                yield Button("Analyze", id="analyze-btn", variant="primary")
            yield Static(
                "Select a session and click Analyze",
                id="analysis-panel",
                classes="empty-state"
            )

    def watch_log_content(self, content: str) -> None:
        """Update log display when content changes."""
        try:
            log = self.query_one("#raw-log", RichLog)
            log.clear()
            if content:
                log.write(content)
            else:
                log.write("[dim]No output captured[/dim]")
        except Exception:
            pass  # Widget may not be mounted yet

    def watch_analysis_content(self, content: str) -> None:
        """Update analysis display when content changes."""
        try:
            panel = self.query_one("#analysis-panel", Static)
            if content:
                panel.remove_class("empty-state")
                panel.update(Markdown(content))
            else:
                panel.add_class("empty-state")
                panel.update("Select a session and click Analyze")
        except Exception:
            pass  # Widget may not be mounted yet

    def watch_is_analyzing(self, analyzing: bool) -> None:
        """Update UI state during analysis."""
        try:
            btn = self.query_one("#analyze-btn", Button)
            panel = self.query_one("#analysis-panel", Static)

            if analyzing:
                btn.disabled = True
                btn.label = "Analyzing..."
                panel.add_class("analyzing")
                panel.update("Generating hypotheses...")
            else:
                btn.disabled = False
                btn.label = "Analyze"
                panel.remove_class("analyzing")
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "analyze-btn" and not self.is_analyzing:
            self.post_message(self.AnalyzeRequested())

    # Public API

    def update_log(self, content: str) -> None:
        """Update log content.

        Args:
            content: Raw log text to display
        """
        self.log_content = content

    def show_analysis(self, analysis: str) -> None:
        """Show analysis result.

        Args:
            analysis: Markdown-formatted analysis text
        """
        self.is_analyzing = False
        self.analysis_content = analysis

    def show_error(self, error: str) -> None:
        """Show analysis error.

        Args:
            error: Error message
        """
        self.is_analyzing = False
        self.analysis_content = f"**Error:** {error}"

    def start_analyzing(self) -> None:
        """Mark analysis as in progress."""
        self.is_analyzing = True

    def clear(self) -> None:
        """Clear both log and analysis."""
        self.log_content = ""
        self.analysis_content = ""
        self.is_analyzing = False

    def append_log(self, text: str) -> None:
        """Append text to the log.

        Useful for streaming output.

        Args:
            text: Text to append
        """
        try:
            log = self.query_one("#raw-log", RichLog)
            log.write(text)
        except Exception:
            pass
