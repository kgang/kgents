"""
Dawn Cockpit Focus Pane: Left pane showing today's focus items.

The focus pane displays focus items organized by bucket, with
keyboard navigation and visual stale indicators.

Layout:
    ┌─────────────────────────────────────┐
    │  TODAY'S FOCUS                      │
    │  ═══════════════                    │
    │                                     │
    │  🔥 [1] Trail Persistence          │ ← Selected (highlighted)
    │      self.trail.persistence        │
    │                                     │
    │  🎯 [2] Portal React Tests         │
    │      plans/portal-fullstack.md     │
    │                                     │
    │  ⚠️ [3] Spec Hygiene (stale)        │ ← Stale indicator
    │      plans/spec-hygiene.md         │
    │                                     │
    │  ────────────────────────────────  │
    │  [a] Add   [d] Done   [h] Hygiene  │
    └─────────────────────────────────────┘

Key Bindings (when focused):
    ↑↓/jk    Navigate items
    Enter    Open/expand item
    d        Mark done (archive)
    1-9      Quick select by number

See: spec/protocols/dawn-cockpit.md
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from rich.text import Text
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from ..focus import Bucket, FocusItem, FocusManager

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# Bucket display configuration
BUCKET_EMOJI = {
    Bucket.TODAY: "🔥",
    Bucket.WEEK: "🎯",
    Bucket.SOMEDAY: "🧘",
}


class FocusItemWidget(Static):
    """
    A single focus item in the pane.

    Renders with number, emoji, label, and target path.
    Shows stale indicator when item is past threshold.
    """

    class Selected(Message):
        """Emitted when this item is selected."""

        def __init__(self, item: FocusItem) -> None:
            self.item = item
            super().__init__()

    class Activated(Message):
        """Emitted when this item is activated (Enter)."""

        def __init__(self, item: FocusItem) -> None:
            self.item = item
            super().__init__()

    is_selected: reactive[bool] = reactive(False)

    def __init__(
        self,
        item: FocusItem,
        index: int,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.item = item
        self.index = index

    def render(self) -> Text:
        """Render the focus item."""
        emoji = BUCKET_EMOJI.get(self.item.bucket, "📌")
        stale_marker = " ⚠️ (stale)" if self.item.is_stale else ""

        # Build the text
        text = Text()

        # Selection indicator
        if self.is_selected:
            text.append("▶ ", style="bold cyan")
        else:
            text.append("  ")

        # Number and emoji
        text.append(f"{emoji} [{self.index + 1}] ", style="bold")

        # Label
        label_style = "yellow" if self.item.is_stale else "white"
        text.append(self.item.label, style=label_style)

        # Stale marker
        if self.item.is_stale:
            text.append(stale_marker, style="dim yellow")

        # Target path on next line
        text.append(f"\n      {self.item.target}", style="dim")

        return text

    def watch_is_selected(self, selected: bool) -> None:
        """Update display when selection changes."""
        self.refresh()


class FocusPane(Widget, can_focus=True):
    """
    The focus pane widget containing all focus items.

    Provides keyboard navigation and selection handling.

    Teaching:
        gotcha: Items are displayed TODAY first, then WEEK, then SOMEDAY.
                This matches the bucket priority order.
                (Evidence: spec/protocols/dawn-cockpit.md § Focus Management)
    """

    class ItemSelected(Message):
        """Emitted when a focus item is selected."""

        def __init__(self, item: FocusItem | None) -> None:
            self.item = item
            super().__init__()

    class ItemActivated(Message):
        """Emitted when a focus item is activated (Enter)."""

        def __init__(self, item: FocusItem) -> None:
            self.item = item
            super().__init__()

    is_active: reactive[bool] = reactive(False)
    _reactive_selected_index: reactive[int] = reactive(0)

    def __init__(
        self,
        focus_manager: FocusManager,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.focus_manager = focus_manager
        self._items: list[FocusItem] = []
        self._item_widgets: list[FocusItemWidget] = []
        self._selected_index: int = 0  # Non-reactive for testing

    @property
    def selected_index(self) -> int:
        """Get selected index."""
        return self._selected_index

    @selected_index.setter
    def selected_index(self, value: int) -> None:
        """Set selected index and update reactive."""
        self._selected_index = value
        # Only update reactive if we're in a running app
        try:
            self._reactive_selected_index = value
        except Exception:
            pass  # Not in app context

    @property
    def selected_item(self) -> FocusItem | None:
        """Get the currently selected item."""
        if 0 <= self.selected_index < len(self._items):
            return self._items[self.selected_index]
        return None

    def compose(self) -> Any:
        """Compose the pane content."""
        yield Static("📍 FOCUS", id="focus-title", classes="pane-title")
        yield Static("═" * 20, classes="separator")
        # Items will be added dynamically
        yield Static(id="items-container")

    def on_mount(self) -> None:
        """Populate items on mount."""
        self.refresh_items()

    def refresh_items(self) -> None:
        """Refresh the focus items display."""
        # Get items in bucket priority order
        self._items = []
        for bucket in [Bucket.TODAY, Bucket.WEEK, Bucket.SOMEDAY]:
            self._items.extend(self.focus_manager.list(bucket=bucket))

        # Update display
        self._render_items()

        # Clamp selection
        if self.selected_index >= len(self._items):
            self.selected_index = max(0, len(self._items) - 1)

    def _render_items(self) -> None:
        """Render items to the container."""
        container = self.query_one("#items-container", Static)

        if not self._items:
            container.update("[dim]No focus items. Press [a] to add.[/dim]")
            return

        # Build content
        lines = []
        for i, item in enumerate(self._items):
            emoji = BUCKET_EMOJI.get(item.bucket, "📌")
            stale = " ⚠️" if item.is_stale else ""
            selected = "▶ " if i == self.selected_index else "  "
            style = "bold cyan" if i == self.selected_index else ""
            label_style = "yellow" if item.is_stale else ""

            if i == self.selected_index:
                lines.append(
                    f"[bold cyan]{selected}{emoji} [{i + 1}] {item.label}{stale}[/bold cyan]"
                )
            elif item.is_stale:
                lines.append(f"  {emoji} [{i + 1}] [yellow]{item.label}{stale}[/yellow]")
            else:
                lines.append(f"  {emoji} [{i + 1}] {item.label}")

            lines.append(f"[dim]      {item.target}[/dim]")
            lines.append("")

        container.update("\n".join(lines))

    def watch__reactive_selected_index(self, index: int) -> None:
        """Update display when selection changes."""
        self._render_items()
        self.post_message(self.ItemSelected(self.selected_item))

    def watch_is_active(self, active: bool) -> None:
        """Update title styling when active state changes."""
        try:
            title = self.query_one("#focus-title", Static)
            if active:
                title.update("[bold reverse cyan] 📍 FOCUS [/bold reverse cyan]")
            else:
                title.update("📍 FOCUS")
        except Exception:
            pass  # Not mounted yet

    def on_key(self, event: Any) -> None:
        """Handle keyboard navigation (only when active or focused).

        Teaching:
            gotcha: Check both is_active AND has_focus. When user tabs or clicks
                    into a pane, the first Enter may arrive before is_active is
                    propagated from the reactive watcher. Using has_focus as
                    fallback ensures the key is handled.
                    (Evidence: User report of Enter twice needed after focus)
        """
        if not self.is_active and not self.has_focus:
            return  # Let app handle keys when not active

        key = event.key

        # Only handle navigation keys, let others bubble up
        if key in ("up", "k") and self._items:
            self.selected_index = max(0, self.selected_index - 1)
            event.stop()
        elif key in ("down", "j") and self._items:
            self.selected_index = min(len(self._items) - 1, self.selected_index + 1)
            event.stop()
        elif key == "enter" and self.selected_item:
            self.post_message(self.ItemActivated(self.selected_item))
            event.stop()
        elif key in "123456789" and self._items:
            index = int(key) - 1
            if index < len(self._items):
                self.selected_index = index
                event.stop()
        # Don't stop other keys - let them bubble to app (tab, a, d, h, etc.)


__all__ = [
    "FocusPane",
    "FocusItemWidget",
]
