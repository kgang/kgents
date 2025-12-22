"""
Dawn Cockpit Snippet Pane: Right pane — the button pad.

The snippet pane is the killer feature: a vertical list of copyable
snippets where Enter = copy to clipboard.

Layout:
    ┌────────────────────────────────────────┐
    │  SNIPPETS (↑↓ select, ⏎ copy)          │
    │  ═══════════════════════════════       │
    │                                        │
    │  ▶ Voice: "Depth > breadth"            │ ← Static (always loaded)
    │  ▶ Quote: "The proof IS..."            │
    │  ▶ Pattern: Container-Owns-Work        │
    │                                        │
    │  ⟳ Path: self.portal.manifest          │ ← Query (lazy loaded)
    │  ⟳ Recent: "Completed Phase 5"         │
    │                                        │
    │  ★ My Note: Remember this              │ ← Custom (user added)
    │                                        │
    │  + [Add custom snippet]                │
    │                                        │
    │  ─────────────────────────────────     │
    │  [/] Search   [e] Edit   [x] Delete    │
    └────────────────────────────────────────┘

Snippet Patterns (Law 5: three_patterns):
    ▶ Static   - Configured at startup (voice anchors, quotes)
    ⟳ Query    - AGENTESE-derived, lazy loaded
    ★ Custom   - User-added, ephemeral per session

Key Bindings (when focused):
    ↑↓/jk    Navigate snippets
    Enter    Copy selected snippet to clipboard
    x        Delete custom snippet
    1-9      Quick select by number

See: spec/protocols/dawn-cockpit.md
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from rich.text import Text
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from ..snippets import CustomSnippet, QuerySnippet, Snippet, SnippetLibrary, StaticSnippet

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# Snippet type display configuration
SNIPPET_ICONS = {
    "static": "▶",
    "query": "⟳",
    "custom": "★",
}

SNIPPET_COLORS = {
    "static": "white",
    "query": "cyan",
    "custom": "green",
}


class SnippetItemWidget(Static):
    """
    A single snippet item widget for scroll-into-view support.

    Each snippet renders as its own widget so we can scroll to it.
    """

    is_selected: reactive[bool] = reactive(False)

    def __init__(
        self,
        snippet: Snippet,
        index: int,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.snippet = snippet
        self.index = index

    def render(self) -> Text:
        """Render the snippet item."""
        snippet_dict = self.snippet.to_dict()
        snippet_type = snippet_dict.get("type", "static")
        icon = SNIPPET_ICONS.get(snippet_type, "▶")
        color = SNIPPET_COLORS.get(snippet_type, "white")

        label = snippet_dict["label"]
        content = snippet_dict.get("content")
        is_loaded = snippet_dict.get("is_loaded", True)

        # Build preview
        if content:
            preview = content[:30] + "..." if len(content) > 30 else content
        elif not is_loaded:
            preview = "[not loaded]"
        else:
            preview = ""

        # Build text
        text = Text()

        # Selection indicator and main line
        if self.is_selected:
            text.append("▶ ", style="bold")
            text.append(f"{icon} {label}", style=f"bold {color}")
        else:
            text.append(f"  {icon} {label}", style=color)

        # Preview on next line
        if preview:
            text.append(f'\n      "{preview}"', style="dim")

        return text

    def watch_is_selected(self, selected: bool) -> None:
        """Update display when selection changes."""
        self.refresh()


class SnippetPane(Widget, can_focus=True):
    """
    The snippet pane widget — the button pad.

    Provides keyboard navigation and copy-on-Enter.

    Teaching:
        gotcha: Enter copies, not opens. This is the killer feature.
                The snippet content goes to clipboard immediately.
                (Evidence: spec/protocols/dawn-cockpit.md § Snippet Button Pad)

        gotcha: Query snippets show as collapsed until first access.
                Loading happens asynchronously when selected.
                (Evidence: spec/protocols/dawn-cockpit.md § QuerySnippet)
    """

    class SnippetCopied(Message):
        """Emitted when a snippet is copied to clipboard."""

        def __init__(self, snippet: Snippet, content: str) -> None:
            self.snippet = snippet
            self.content = content
            super().__init__()

    class SnippetSelected(Message):
        """Emitted when a snippet is selected."""

        def __init__(self, snippet: Snippet | None) -> None:
            self.snippet = snippet
            super().__init__()

    class SnippetEditRequested(Message):
        """Emitted when user requests to edit a snippet."""

        def __init__(self, snippet: Snippet) -> None:
            self.snippet = snippet
            super().__init__()

    class SnippetAddRequested(Message):
        """Emitted when user requests to add a new snippet."""

        pass

    is_active: reactive[bool] = reactive(False)
    _reactive_selected_index: reactive[int] = reactive(0)

    def __init__(
        self,
        snippet_library: SnippetLibrary,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.snippet_library = snippet_library
        self._snippets: list[Snippet] = []
        self._item_widgets: list[SnippetItemWidget] = []
        self._copy_callback: Any | None = None
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
    def selected_snippet(self) -> Snippet | None:
        """Get the currently selected snippet."""
        if 0 <= self.selected_index < len(self._snippets):
            return self._snippets[self.selected_index]
        return None

    def set_copy_callback(self, callback: Any) -> None:
        """Set callback for clipboard operations (for testing)."""
        self._copy_callback = callback

    CSS = """
    #snippets-scroll {
        height: 1fr;
        scrollbar-size: 1 1;
    }

    .snippet-item {
        height: auto;
        padding: 0;
        margin-bottom: 1;
    }
    """

    def compose(self) -> Any:
        """Compose the pane content."""
        yield Static("📋 SNIPPETS", id="snippet-title", classes="pane-title")
        yield Static("═" * 25, classes="separator")
        yield VerticalScroll(id="snippets-scroll")

    def on_mount(self) -> None:
        """Populate snippets on mount."""
        self.refresh_items()

    def refresh_items(self, force: bool = False) -> None:
        """
        Refresh the snippets display adaptively.

        Uses intelligent refresh:
        1. If snippet data unchanged → just update selection styling (no flash)
        2. If snippets changed → minimal rebuild
        3. Always shows something (no empty flash)

        Args:
            force: If True, always do full rebuild (for after edits)

        Teaching:
            gotcha: remove_children() + mount() causes a flash because there's
                    a render frame where the container is empty. Use adaptive
                    refresh to compare before/after and only rebuild if needed.
                    (Evidence: User report of flash on 'r' key)

            gotcha: Comparing only IDs is not enough — editing a snippet changes
                    content but keeps the same ID. Compare full dict for accuracy.
                    (Evidence: User report of edit not updating display)
        """
        # Capture old state for comparison (ID + label + content)
        old_fingerprints = [
            (s.to_dict()["id"], s.to_dict().get("label"), s.to_dict().get("content"))
            for s in self._snippets
        ]
        self._snippets = self.snippet_library.list_all()
        new_fingerprints = [
            (s.to_dict()["id"], s.to_dict().get("label"), s.to_dict().get("content"))
            for s in self._snippets
        ]

        # Only render if mounted (has DOM context)
        try:
            if not force and old_fingerprints == new_fingerprints and self._item_widgets:
                # Same snippets — just update selection styling (no flash!)
                self._update_selection_display()
            else:
                # Snippets changed — need to rebuild
                self._render_snippets()
        except Exception:
            pass  # Not mounted yet

        # Clamp selection
        if self._selected_index >= len(self._snippets):
            self._selected_index = max(0, len(self._snippets) - 1)

    def _render_snippets(self) -> None:
        """
        Render snippets to the scrollable container.

        Uses batched update to minimize flash:
        1. Create new widgets first
        2. Then swap in one operation
        """
        try:
            container = self.query_one("#snippets-scroll", VerticalScroll)
        except Exception:
            return  # Not mounted

        # Build new widgets first (before removing old ones)
        new_widgets: list[SnippetItemWidget] = []

        if not self._snippets:
            # Show placeholder — never empty
            container.remove_children()
            container.mount(
                Static("[dim]No snippets. Press [+] to add.[/dim]", id="empty-placeholder")
            )
            self._item_widgets = []
            return

        for i, snippet in enumerate(self._snippets):
            widget = SnippetItemWidget(
                snippet,
                i,
                id=f"snippet-{i}",
                classes="snippet-item",
            )
            widget.is_selected = i == self.selected_index
            new_widgets.append(widget)

        # Now do the swap — remove old, add new
        container.remove_children()
        self._item_widgets = new_widgets
        for widget in new_widgets:
            container.mount(widget)

        # Scroll to selected
        self._scroll_to_selected()

    def _scroll_to_selected(self) -> None:
        """Scroll to keep the selected item visible."""
        if not self._item_widgets or self.selected_index >= len(self._item_widgets):
            return

        try:
            selected_widget = self._item_widgets[self.selected_index]
            selected_widget.scroll_visible()
        except Exception:
            pass  # Widget not ready

    def _update_selection_display(self) -> None:
        """Update which widget shows as selected (without full re-render)."""
        for i, widget in enumerate(self._item_widgets):
            widget.is_selected = i == self.selected_index
        self._scroll_to_selected()

    def watch__reactive_selected_index(self, index: int) -> None:
        """Update display when selection changes."""
        if self._item_widgets:
            self._update_selection_display()
        else:
            self._render_snippets()
        self.post_message(self.SnippetSelected(self.selected_snippet))

    def watch_is_active(self, active: bool) -> None:
        """Update title styling when active state changes."""
        try:
            title = self.query_one("#snippet-title", Static)
            if active:
                title.update("[bold reverse green] 📋 SNIPPETS [/bold reverse green]")
            else:
                title.update("📋 SNIPPETS")
        except Exception:
            pass  # Not mounted yet

    def on_key(self, event: Any) -> None:
        """Handle keyboard navigation (only when active)."""
        if not self.is_active:
            return  # Let app handle keys when not active

        key = event.key

        # Only handle navigation keys, let others bubble up
        if key in ("up", "k") and self._snippets:
            self.selected_index = max(0, self.selected_index - 1)
            event.stop()
        elif key in ("down", "j") and self._snippets:
            self.selected_index = min(len(self._snippets) - 1, self.selected_index + 1)
            event.stop()
        elif key == "enter" and self._snippets:
            self._copy_selected()
            event.stop()
        elif key == "x" and self._snippets:
            self._delete_selected()
            event.stop()
        elif key == "e" and self._snippets:
            self._edit_selected()
            event.stop()
        elif key == "n":
            self._add_new()
            event.stop()
        elif key in "123456789" and self._snippets:
            index = int(key) - 1
            if index < len(self._snippets):
                self.selected_index = index
                event.stop()
        # Don't stop other keys - let them bubble to app (tab, etc.)

    def _copy_selected(self) -> None:
        """Copy the selected snippet to clipboard."""
        snippet = self.selected_snippet
        if not snippet:
            return

        snippet_dict = snippet.to_dict()
        content = snippet_dict.get("content")

        if not content:
            # Query snippet not loaded
            query = snippet_dict.get("query", "")
            content = f"[Query: {query}]"
            logger.debug("Snippet not loaded, using query placeholder: %s", query)

        # Try to copy to clipboard
        try:
            if self._copy_callback:
                self._copy_callback(content)
            else:
                # Try pyperclip first, fall back to pbcopy on macOS
                copied = False
                try:
                    import pyperclip  # type: ignore[import-untyped]  # No stubs

                    pyperclip.copy(content)
                    copied = True
                except ImportError:
                    pass  # pyperclip not available
                except Exception:
                    pass  # pyperclip failed

                if not copied:
                    # macOS fallback
                    try:
                        import subprocess

                        process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                        process.communicate(content.encode("utf-8"))
                    except Exception as e:
                        logger.debug(f"Clipboard copy failed: {e}")

            self.post_message(self.SnippetCopied(snippet, content))
        except Exception as e:
            logger.error(f"Failed to copy snippet: {e}")

    def _delete_selected(self) -> None:
        """Delete the selected custom snippet."""
        snippet = self.selected_snippet
        if not snippet:
            return

        snippet_dict = snippet.to_dict()
        if snippet_dict.get("type") != "custom":
            # Can only delete custom snippets
            return

        self.snippet_library.remove_custom(snippet_dict["id"])
        self.refresh_items()

    def _edit_selected(self) -> None:
        """Request edit for the selected snippet."""
        snippet = self.selected_snippet
        if not snippet:
            return

        snippet_dict = snippet.to_dict()
        if snippet_dict.get("type") != "custom":
            # Can only edit custom snippets
            return

        self.post_message(self.SnippetEditRequested(snippet))

    def _add_new(self) -> None:
        """Request to add a new snippet."""
        self.post_message(self.SnippetAddRequested())


__all__ = [
    "SnippetPane",
    "SnippetItemWidget",
]
