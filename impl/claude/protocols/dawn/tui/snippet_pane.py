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

    def compose(self) -> Any:
        """Compose the pane content."""
        yield Static("📋 SNIPPETS", id="snippet-title", classes="pane-title")
        yield Static("═" * 25, classes="separator")
        yield Static(id="snippets-container")
        yield Static("─" * 25, classes="separator")
        yield Static("[dim]↑↓ select  ⏎ copy  [x] delete[/dim]", id="help")

    def on_mount(self) -> None:
        """Populate snippets on mount."""
        self.refresh_items()

    def refresh_items(self) -> None:
        """Refresh the snippets display."""
        self._snippets = self.snippet_library.list_all()

        # Only render if mounted (has DOM context)
        try:
            self._render_snippets()
        except Exception:
            pass  # Not mounted yet

        # Clamp selection
        if self._selected_index >= len(self._snippets):
            self._selected_index = max(0, len(self._snippets) - 1)

    def _render_snippets(self) -> None:
        """Render snippets to the container."""
        container = self.query_one("#snippets-container", Static)

        if not self._snippets:
            container.update("[dim]No snippets. Load defaults with snippet_library.load_defaults()[/dim]")
            return

        lines = []
        for i, snippet in enumerate(self._snippets):
            snippet_dict = snippet.to_dict()
            snippet_type = snippet_dict.get("type", "static")
            icon = SNIPPET_ICONS.get(snippet_type, "▶")
            color = SNIPPET_COLORS.get(snippet_type, "white")

            # Selection indicator
            selected = i == self.selected_index
            prefix = "▶ " if selected else "  "

            # Label display
            label = snippet_dict["label"]

            # Content preview (truncated)
            content = snippet_dict.get("content")
            is_loaded = snippet_dict.get("is_loaded", True)

            if content:
                preview = content[:30] + "..." if len(content) > 30 else content
            elif not is_loaded:
                preview = "[not loaded]"
            else:
                preview = ""

            # Build line
            if selected:
                lines.append(f"[bold {color}]{prefix}{icon} {label}[/bold {color}]")
            else:
                lines.append(f"[{color}]  {icon} {label}[/{color}]")

            if preview:
                lines.append(f"[dim]      \"{preview}\"[/dim]")
            lines.append("")

        container.update("\n".join(lines))

    def watch__reactive_selected_index(self, index: int) -> None:
        """Update display when selection changes."""
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
        # DEBUG: Log every key received
        logger.warning(f"SnippetPane.on_key: key={event.key!r}, is_active={self.is_active}, snippets={len(self._snippets)}")

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
        elif key in "123456789" and self._snippets:
            index = int(key) - 1
            if index < len(self._snippets):
                self.selected_index = index
                event.stop()
        # Don't stop other keys - let them bubble to app (tab, etc.)

    def _copy_selected(self) -> None:
        """Copy the selected snippet to clipboard."""
        logger.warning(f"_copy_selected called, selected_snippet={self.selected_snippet}")
        snippet = self.selected_snippet
        if not snippet:
            logger.warning("_copy_selected: No snippet selected, returning")
            return

        snippet_dict = snippet.to_dict()
        logger.warning(f"_copy_selected: snippet_dict={snippet_dict}")
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
                try:
                    import pyperclip
                    pyperclip.copy(content)
                except ImportError:
                    # pyperclip not available - emit message anyway
                    logger.debug("pyperclip not available, skipping clipboard copy")
                except Exception as e:
                    logger.debug("Clipboard copy failed: %s", e)

            self.post_message(self.SnippetCopied(snippet, content))
        except Exception as e:
            logger.error("Failed to copy snippet: %s", e)

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


__all__ = [
    "SnippetPane",
]
