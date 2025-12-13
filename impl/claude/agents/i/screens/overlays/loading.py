"""
LoadingOverlay - Show progress during async operations.

Displays a spinner and optional progress message.
Philosophy: "Make waiting delightful, not anxious."
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Static

from ...theme.dashboard import THEME

if TYPE_CHECKING:
    pass


# Spinner frames (Unicode block animation)
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class LoadingOverlay(ModalScreen[None]):
    """
    Loading overlay with spinner and progress message.

    Shows during async operations to indicate progress.
    Auto-dismisses when operation completes.

    Usage:
        async with app.push_screen(LoadingOverlay("Processing...")):
            await long_running_operation()
    """

    CSS = f"""
    LoadingOverlay {{
        align: center middle;
    }}

    LoadingOverlay #loading-container {{
        width: 50;
        height: auto;
        border: round {THEME.border};
        background: {THEME.background};
        padding: 2;
    }}

    LoadingOverlay #spinner {{
        height: 1;
        text-align: center;
        color: {THEME.accent};
        text-style: bold;
        margin-bottom: 1;
    }}

    LoadingOverlay #message {{
        height: auto;
        text-align: center;
        color: {THEME.text_secondary};
    }}

    LoadingOverlay #progress-bar {{
        height: 1;
        margin-top: 1;
    }}

    LoadingOverlay .progress-filled {{
        color: {THEME.success};
    }}

    LoadingOverlay .progress-empty {{
        color: {THEME.border};
    }}
    """

    # Reactive properties
    message: reactive[str] = reactive("Loading...")
    progress: reactive[float | None] = reactive(None)  # 0.0-1.0 or None
    frame_index: reactive[int] = reactive(0)

    def __init__(
        self,
        message: str = "Loading...",
        progress: float | None = None,
        name: str | None = None,
    ) -> None:
        super().__init__(name=name)
        self.message = message
        self.progress = progress
        self._animation_task: asyncio.Task[None] | None = None

    def compose(self) -> ComposeResult:
        """Compose the loading overlay."""
        with Container(id="loading-container"):
            with Vertical():
                yield Static(id="spinner")
                yield Static(self.message, id="message")
                if self.progress is not None:
                    yield Static(id="progress-bar")

    async def on_mount(self) -> None:
        """Start spinner animation on mount."""
        self._animation_task = asyncio.create_task(self._animate_spinner())

    async def on_unmount(self) -> None:
        """Stop spinner animation on unmount."""
        if self._animation_task:
            self._animation_task.cancel()
            try:
                await self._animation_task
            except asyncio.CancelledError:
                pass

    async def _animate_spinner(self) -> None:
        """Animate the spinner continuously."""
        while True:
            # Update spinner frame
            spinner_widget = self.query_one("#spinner", Static)
            spinner_widget.update(SPINNER_FRAMES[self.frame_index])

            # Advance frame
            self.frame_index = (self.frame_index + 1) % len(SPINNER_FRAMES)

            await asyncio.sleep(THEME.spinner_interval / 1000.0)

    def watch_message(self, new_message: str) -> None:
        """React to message changes."""
        try:
            message_widget = self.query_one("#message", Static)
            message_widget.update(new_message)
        except Exception:
            # Widget not yet mounted
            pass

    def watch_progress(self, new_progress: float | None) -> None:
        """React to progress changes."""
        if new_progress is None:
            return

        try:
            progress_widget = self.query_one("#progress-bar", Static)
            # Render progress bar
            bar_width = 40
            filled = int(new_progress * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            pct = int(new_progress * 100)
            progress_widget.update(f"{bar} {pct}%")
        except Exception:
            # Widget not yet mounted or doesn't exist
            pass

    def set_message(self, message: str) -> None:
        """Update the loading message."""
        self.message = message

    def set_progress(self, progress: float) -> None:
        """
        Update the progress value (0.0 to 1.0).

        If progress was None, this will show the progress bar.
        """
        self.progress = progress


__all__ = ["LoadingOverlay"]
