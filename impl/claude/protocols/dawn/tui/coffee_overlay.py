"""
Dawn Cockpit Coffee Overlay: Morning Coffee Ritual Screen.

The Morning Coffee ritual is Kent's daily grounding practice — a four-movement
sequence that transforms scattered morning energy into focused intention.

Movements:
    1. Garden View   — What grew overnight (git changes, witness marks)
    2. Hygiene Pass  — Stale items needing attention
    3. Focus Set     — Confirm today's 1-3 items
    4. Snippet Prime — Prepare button pad for day

Layout:
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │  ☕ MORNING COFFEE — Movement 1/4: Garden View                              │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │                                                                             │
    │  Yesterday's Harvest                                                        │
    │  ─────────────────                                                          │
    │  ◉ 3 files changed → Brain persistence hardening                           │
    │  ◉ New test: test_semantic_consistency.py                                  │
    │  ...                                                                        │
    │                                                                             │
    │  [Enter] Continue   [s] Skip to Menu   [Esc] Return to Dawn                │
    └─────────────────────────────────────────────────────────────────────────────┘

Key Bindings:
    Enter   Advance to next movement
    s       Skip to movement selector
    Esc     Return to Dawn cockpit

Philosophy:
    "The gardener doesn't count the petals. The gardener tends the garden."

See: spec/protocols/dawn-cockpit.md § Morning Coffee Integration
AGENTESE: time.dawn.coffee
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Key
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Static

if TYPE_CHECKING:
    from ..focus import FocusManager
    from ..snippets import SnippetLibrary

logger = logging.getLogger(__name__)


class Movement(Enum):
    """The four movements of Morning Coffee."""

    GARDEN = 1  # What grew overnight
    HYGIENE = 2  # Stale items needing attention
    FOCUS = 3  # Confirm today's 1-3 items
    SNIPPET = 4  # Prepare button pad for day

    @property
    def title(self) -> str:
        """Human-readable title for movement."""
        return {
            Movement.GARDEN: "Garden View",
            Movement.HYGIENE: "Hygiene Pass",
            Movement.FOCUS: "Focus Set",
            Movement.SNIPPET: "Snippet Prime",
        }[self]

    @property
    def subtitle(self) -> str:
        """Subtitle describing the movement."""
        return {
            Movement.GARDEN: "What grew overnight",
            Movement.HYGIENE: "Stale items needing attention",
            Movement.FOCUS: "Confirm today's 1-3 items",
            Movement.SNIPPET: "Prepare button pad for day",
        }[self]

    @property
    def icon(self) -> str:
        """Icon for movement."""
        return {
            Movement.GARDEN: "🌱",
            Movement.HYGIENE: "🧹",
            Movement.FOCUS: "🎯",
            Movement.SNIPPET: "📋",
        }[self]


@dataclass
class CoffeeResult:
    """Result from completing the coffee ritual."""

    completed: bool
    movement_reached: Movement
    focus_confirmed: bool
    time_spent_seconds: float


class CoffeeOverlay(ModalScreen[CoffeeResult]):
    """
    Morning Coffee ritual overlay.

    Guides Kent through the four movements of his daily ritual,
    grounding scattered morning energy into focused intention.

    Returns:
        CoffeeResult with completion status and metadata

    Teaching:
        gotcha: Each movement gathers data asynchronously but renders
                statically. Use refresh_content() to update display.
                (Evidence: Textual async patterns)

        gotcha: The coffee ritual is CONTEMPLATIVE. Don't rush the user.
                Each movement should feel spacious, not cramped.
                (Evidence: spec/protocols/dawn-cockpit.md § Morning Coffee)
    """

    BINDINGS = [
        ("escape", "cancel", "Return to Dawn"),
        ("enter", "advance", "Continue"),
        ("s", "skip_to_menu", "Skip"),
    ]

    CSS = """
    CoffeeOverlay {
        align: center middle;
    }

    #coffee-container {
        width: 70;
        height: 20;
        border: double $primary;
        background: $surface;
        padding: 1 2;
    }

    #coffee-header {
        text-align: center;
        text-style: bold;
        color: $warning;
        padding-bottom: 1;
    }

    #movement-title {
        text-align: center;
        text-style: bold reverse;
        padding: 0 1;
        margin-bottom: 1;
    }

    #movement-subtitle {
        text-align: center;
        text-style: italic;
        color: $text-muted;
        margin-bottom: 1;
    }

    #content-scroll {
        height: 1fr;
        border: solid $primary-background;
        padding: 0 1;
        margin-bottom: 1;
    }

    #content-area {
        height: auto;
    }

    .content-item {
        padding: 0;
    }

    #help-bar {
        text-align: center;
        color: $text-muted;
    }

    #progress-bar {
        text-align: center;
        padding-top: 1;
    }

    .progress-dot {
        width: 3;
    }

    .progress-active {
        color: $success;
        text-style: bold;
    }

    .progress-done {
        color: $primary;
    }

    .progress-pending {
        color: $text-muted;
    }
    """

    current_movement: reactive[Movement] = reactive(Movement.GARDEN)

    def __init__(
        self,
        focus_manager: "FocusManager | None" = None,
        snippet_library: "SnippetLibrary | None" = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._focus_manager = focus_manager
        self._snippet_library = snippet_library
        self._start_time = datetime.now()
        self._focus_confirmed = False
        self._movement_content: dict[Movement, list[str]] = {}

    def compose(self) -> Any:
        """Compose the coffee overlay."""
        with Vertical(id="coffee-container"):
            yield Static("☕ MORNING COFFEE", id="coffee-header")
            yield Static("", id="movement-title")
            yield Static("", id="movement-subtitle")
            with VerticalScroll(id="content-scroll"):
                yield Vertical(id="content-area")
            yield Static("", id="help-bar")
            with Horizontal(id="progress-bar"):
                for m in Movement:
                    yield Static("○", classes="progress-dot progress-pending", id=f"dot-{m.value}")

    async def on_mount(self) -> None:
        """Initialize and start the ritual."""
        self._update_header()
        await self._load_movement_content()
        self._render_content()

    def watch_current_movement(self, movement: Movement) -> None:
        """Update display when movement changes."""
        # Guard: widgets may not be mounted yet
        try:
            self._update_header()
            # Load content async
            asyncio.create_task(self._refresh_movement())
        except Exception:
            pass  # Not mounted yet

    async def _refresh_movement(self) -> None:
        """Refresh current movement content."""
        await self._load_movement_content()
        self._render_content()

    def _update_header(self) -> None:
        """Update header with current movement info."""
        movement = self.current_movement
        self.query_one("#movement-title", Static).update(
            f"{movement.icon} Movement {movement.value}/4: {movement.title}"
        )
        self.query_one("#movement-subtitle", Static).update(movement.subtitle)
        self.query_one("#help-bar", Static).update(
            "[Enter] Continue   [s] Skip   [Esc] Return to Dawn"
        )

        # Update progress dots
        for m in Movement:
            dot = self.query_one(f"#dot-{m.value}", Static)
            if m.value < movement.value:
                dot.update("●")
                dot.remove_class("progress-pending", "progress-active")
                dot.add_class("progress-done")
            elif m.value == movement.value:
                dot.update("◉")
                dot.remove_class("progress-pending", "progress-done")
                dot.add_class("progress-active")
            else:
                dot.update("○")
                dot.remove_class("progress-done", "progress-active")
                dot.add_class("progress-pending")

    async def _load_movement_content(self) -> None:
        """Load content for current movement."""
        movement = self.current_movement
        content: list[str] = []

        try:
            if movement == Movement.GARDEN:
                content = await self._load_garden_content()
            elif movement == Movement.HYGIENE:
                content = await self._load_hygiene_content()
            elif movement == Movement.FOCUS:
                content = await self._load_focus_content()
            elif movement == Movement.SNIPPET:
                content = await self._load_snippet_content()
        except Exception as e:
            logger.debug(f"Failed to load {movement.title} content: {e}")
            content = [f"[dim]Content unavailable: {e}[/dim]"]

        self._movement_content[movement] = content or ["[dim]Nothing to show[/dim]"]

    async def _load_garden_content(self) -> list[str]:
        """Load garden view content (what grew overnight)."""
        items: list[str] = []

        # Try to get git changes
        try:
            import subprocess

            result = subprocess.run(
                ["git", "log", "--oneline", "-5", "--since=yesterday"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                items.append("[bold]Recent Commits[/bold]")
                items.append("───────────────")
                for line in result.stdout.strip().split("\n")[:5]:
                    items.append(f"  ◉ {line}")
                items.append("")
        except Exception:
            pass

        # Try to get modified files
        try:
            import subprocess

            result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                items.append("[bold]Working Tree[/bold]")
                items.append("────────────")
                for line in result.stdout.strip().split("\n")[:5]:
                    items.append(f"  {line}")
                items.append("")
        except Exception:
            pass

        if not items:
            items = [
                "[dim]No overnight changes detected[/dim]",
                "",
                "The garden rested peacefully.",
            ]

        return items

    async def _load_hygiene_content(self) -> list[str]:
        """Load hygiene pass content (stale items)."""
        items: list[str] = []

        if self._focus_manager:
            stale = self._focus_manager.get_stale()
            if stale:
                items.append("[bold]Stale Focus Items[/bold]")
                items.append("──────────────────")
                for item in stale[:5]:
                    items.append(f"  ⚠️ {item.label} ({item.bucket.value})")
                items.append("")
            else:
                items.append("✓ All focus items are fresh!")
                items.append("")
        else:
            items.append("[dim]Focus manager not available[/dim]")

        return items

    async def _load_focus_content(self) -> list[str]:
        """Load focus set content (today's items)."""
        items: list[str] = []

        if self._focus_manager:
            from ..focus import Bucket

            today = self._focus_manager.list(bucket=Bucket.TODAY)
            week = self._focus_manager.list(bucket=Bucket.WEEK)

            items.append("[bold]Today's Focus[/bold]")
            items.append("──────────────")
            if today:
                for i, item in enumerate(today[:3], 1):
                    stale_marker = " ⚠️" if item.is_stale else ""
                    items.append(f"  [{i}] {item.label}{stale_marker}")
            else:
                items.append("  [dim]No items set for today[/dim]")
            items.append("")

            if week:
                items.append("[bold]This Week[/bold]")
                items.append("───────────")
                for item in week[:3]:
                    items.append(f"  · {item.label}")
                items.append("")

            self._focus_confirmed = True  # Mark as confirmed when viewed
        else:
            items.append("[dim]Focus manager not available[/dim]")

        return items

    async def _load_snippet_content(self) -> list[str]:
        """Load snippet prime content (button pad status)."""
        items: list[str] = []

        if self._snippet_library:
            static = self._snippet_library.list_static()
            query = self._snippet_library.list_query()
            custom = self._snippet_library.list_custom()

            items.append("[bold]Snippet Button Pad[/bold]")
            items.append("───────────────────")
            items.append(f"  ▶ Static snippets: {len(static)}")
            items.append(f"  ⟳ Query snippets: {len(query)}")
            items.append(f"  ★ Custom snippets: {len(custom)}")
            items.append("")

            if custom:
                items.append("[bold]Recent Custom[/bold]")
                items.append("──────────────")
                for s in custom[:3]:
                    items.append(f"  ★ {s.label}")
                items.append("")

            items.append("☕ Coffee complete! Your button pad is primed.")
        else:
            items.append("[dim]Snippet library not available[/dim]")

        return items

    def _render_content(self) -> None:
        """Render current movement content."""
        content_area = self.query_one("#content-area", Vertical)
        content_area.remove_children()

        items = self._movement_content.get(self.current_movement, ["Loading..."])
        for item in items:
            content_area.mount(Static(item, classes="content-item"))

    def action_advance(self) -> None:
        """Advance to next movement or complete."""
        current_value = self.current_movement.value
        if current_value < 4:
            self.current_movement = Movement(current_value + 1)
        else:
            # Complete the ritual
            self._complete()

    def action_skip_to_menu(self) -> None:
        """Skip to movement selector (show all movements briefly)."""
        # For now, just complete
        self._complete()

    def action_cancel(self) -> None:
        """Cancel and return to Dawn."""
        elapsed = (datetime.now() - self._start_time).total_seconds()
        self.dismiss(
            CoffeeResult(
                completed=False,
                movement_reached=self.current_movement,
                focus_confirmed=self._focus_confirmed,
                time_spent_seconds=elapsed,
            )
        )

    def _complete(self) -> None:
        """Complete the coffee ritual."""
        elapsed = (datetime.now() - self._start_time).total_seconds()
        self.dismiss(
            CoffeeResult(
                completed=True,
                movement_reached=self.current_movement,
                focus_confirmed=self._focus_confirmed,
                time_spent_seconds=elapsed,
            )
        )

    def on_key(self, event: Key) -> None:
        """Handle keyboard events."""
        # Let bindings handle known keys
        pass


__all__ = [
    "CoffeeOverlay",
    "CoffeeResult",
    "Movement",
]
