"""
I-gent Renderers: ASCII visualization at all scales.

This module provides renderers for each scale level:
- GlyphRenderer: ● A
- CardRenderer: Box with metrics
- PageRenderer: Full agent view (open book)
- GardenRenderer: Multiple agents in spatial layout
- LibraryRenderer: Multiple gardens

Aesthetic principles:
- Paper-Terminal: warm cream (#fdfbf7), warm black (#1a1918)
- Box-drawing characters for structure
- Progress bars: █ for filled, ░ for empty
- Consistent grammar across scales
"""

from typing import List

from .core_types import (
    AgentState,
    GardenState,
    Glyph,
    LibraryState,
)


def _progress_bar(value: float, width: int = 10) -> str:
    """Render a progress bar: ████████░░"""
    filled = int(value * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def _box_line(content: str, width: int, left: str = "│", right: str = "│") -> str:
    """Create a line within a box, padded to width."""
    padding = width - len(content) - 2  # 2 for left/right borders
    return f"{left} {content}{' ' * max(0, padding)}{right}"


class GlyphRenderer:
    """
    Renders the atomic unit: phase symbol + identity.

    Example:
        >>> renderer = GlyphRenderer(Glyph("robin", Phase.ACTIVE))
        >>> print(renderer.render())
        ● robin
    """

    def __init__(self, glyph: Glyph):
        self.glyph = glyph

    def render(self) -> str:
        """Render: symbol space id"""
        return self.glyph.render()

    def render_short(self) -> str:
        """Render compact: symbolID"""
        return self.glyph.short()


class CardRenderer:
    """
    Renders a glyph with context—metrics visible at a glance.

    Example:
        ┌─ robin ─────────┐
        │ ● active        │
        │ joy: █████████░ │
        │ eth: ████████░░ │
        └─────────────────┘
    """

    def __init__(
        self,
        state: AgentState,
        width: int = 18,
    ):
        self.state = state
        self.width = max(width, len(state.agent_id) + 8)

    def render(self) -> str:
        """Render the card."""
        lines = []
        inner_width = self.width - 2  # Account for borders

        # Top border with title
        title = f" {self.state.agent_id} "
        left_dashes = (inner_width - len(title)) // 2
        right_dashes = inner_width - len(title) - left_dashes
        lines.append(f"┌{'─' * left_dashes}{title}{'─' * right_dashes}┐")

        # Phase line
        phase_str = f"{self.state.glyph.phase.symbol} {self.state.phase.value}"
        lines.append(_box_line(phase_str, self.width))

        # Time line (if available)
        lines.append(_box_line(f"t: {self.state.elapsed_str}", self.width))

        # Joy bar (if available)
        if self.state.joy is not None:
            joy_bar = _progress_bar(self.state.joy, 10)
            lines.append(_box_line(f"joy: {joy_bar}", self.width))

        # Ethics bar (if available)
        if self.state.ethics is not None:
            eth_bar = _progress_bar(self.state.ethics, 10)
            lines.append(_box_line(f"eth: {eth_bar}", self.width))

        # Bottom border
        lines.append(f"└{'─' * inner_width}┘")

        return "\n".join(lines)


class PageRenderer:
    r"""
    Renders the full view of a single agent—the "open book" metaphor.

    Example:
        ╔══ robin ════════════════════════════════════════════════╗
        ║                                                          ║
        ║  "A B-gent researching protein folding patterns."        ║
        ║                                                          ║
        ║  state: ● active                     t: 00:14:32         ║
        ║  ────────────────────────────────────────────────────    ║
        ║  joy: ███████░░░░  ethics: █████████░░                   ║
        ║                                                          ║
        ║  ┌─ composition graph ────────────────────────────────┐  ║
        ║  │      ● A                                           │  ║
        ║  │       \                                            │  ║
        ║  │        ◐ C ←── forming                             │  ║
        ║  └────────────────────────────────────────────────────┘  ║
        ║                                                          ║
        ║  [observe]  [invoke]  [compose]  [rest]                  ║
        ╚══════════════════════════════════════════════════════════╝
    """

    def __init__(self, state: AgentState, width: int = 60):
        self.state = state
        self.width = max(width, 40)

    def render(self) -> str:
        """Render the page view."""
        lines = []
        inner_width = self.width - 2

        # Title bar
        title = f" {self.state.agent_id} "
        left_eq = (inner_width - len(title)) // 2
        right_eq = inner_width - len(title) - left_eq
        lines.append(f"╔{'═' * left_eq}{title}{'═' * right_eq}╗")

        # Empty line
        lines.append(f"║{' ' * inner_width}║")

        # Epigraph (if available)
        if self.state.epigraph:
            epigraph_line = f'  "{self.state.epigraph}"'
            if len(epigraph_line) > inner_width - 2:
                epigraph_line = epigraph_line[: inner_width - 5] + '..."'
            lines.append(f"║{epigraph_line:{inner_width}}║")
            lines.append(f"║{' ' * inner_width}║")

        # State line
        phase_str = f"{self.state.glyph.phase.symbol} {self.state.phase.value}"
        time_str = f"t: {self.state.elapsed_str}"
        state_line = f"  state: {phase_str}"
        padding = inner_width - len(state_line) - len(time_str) - 2
        lines.append(f"║{state_line}{' ' * max(0, padding)}{time_str}  ║")

        # Separator
        lines.append(f"║  {'─' * (inner_width - 4)}  ║")

        # Metrics line
        metrics_parts = []
        if self.state.joy is not None:
            metrics_parts.append(f"joy: {_progress_bar(self.state.joy, 10)}")
        if self.state.ethics is not None:
            metrics_parts.append(f"ethics: {_progress_bar(self.state.ethics, 10)}")
        if metrics_parts:
            metrics_line = "  " + "  ".join(metrics_parts)
            lines.append(f"║{metrics_line:{inner_width}}║")
            lines.append(f"║{' ' * inner_width}║")

        # Composition graph (if has relationships)
        if self.state.composes_with or self.state.composed_by:
            lines.append(self._render_composition_section(inner_width))
            lines.append(f"║{' ' * inner_width}║")

        # Margin notes (last 3)
        if self.state.margin_notes:
            lines.append(self._render_margin_notes_section(inner_width))
            lines.append(f"║{' ' * inner_width}║")

        # Actions
        actions = "  [observe]  [invoke]  [compose]  [rest]"
        lines.append(f"║{actions:{inner_width}}║")

        # Bottom border
        lines.append(f"╚{'═' * inner_width}╝")

        return "\n".join(lines)

    def _render_composition_section(self, inner_width: int) -> str:
        """Render the composition graph section."""
        lines = []
        box_width = inner_width - 6

        # Box header
        title = " composition graph "
        left_dash = (box_width - len(title)) // 2
        right_dash = box_width - len(title) - left_dash
        lines.append(f"║  ┌{'─' * left_dash}{title}{'─' * right_dash}┐  ║")

        # Render simple graph
        self_glyph = f"      {self.state.glyph.render()}"
        lines.append(f"║  │{self_glyph:{box_width}}│  ║")

        for target in self.state.composes_with[:3]:  # Limit to 3
            arrow_line = f"        ↓ {target}"
            lines.append(f"║  │{arrow_line:{box_width}}│  ║")

        for source in self.state.composed_by[:3]:  # Limit to 3
            arrow_line = f"        ↑ (from {source})"
            lines.append(f"║  │{arrow_line:{box_width}}│  ║")

        # Box footer
        lines.append(f"║  └{'─' * box_width}┘  ║")

        return "\n".join(lines)

    def _render_margin_notes_section(self, inner_width: int) -> str:
        """Render the margin notes section (last 3 notes)."""
        lines = []
        box_width = inner_width - 6

        # Box header
        title = " margin notes "
        left_dash = (box_width - len(title)) // 2
        right_dash = box_width - len(title) - left_dash
        lines.append(f"║  ┌{'─' * left_dash}{title}{'─' * right_dash}┐  ║")

        # Last 3 notes
        recent_notes = self.state.margin_notes[-3:]
        for note in recent_notes:
            note_text = note.render()
            if len(note_text) > box_width - 2:
                note_text = note_text[: box_width - 5] + "..."
            lines.append(f"║  │ {note_text:{box_width - 2}}│  ║")

        # Box footer
        lines.append(f"║  └{'─' * box_width}┘  ║")

        return "\n".join(lines)


class GardenRenderer:
    """
    Renders multiple agents in spatial relationship—the zen garden view.

    Example:
        ┌─ kgents dashboard ──────────────────────────── t: 00:14:32 ─┐
        │                                                            │
        │       ● A ─────────┐                                       │
        │                    │                                       │
        │       ○ B ─────────┼──────── ◐ C                          │
        │                    │          │                            │
        │       ◐ D ─────────┘          │                            │
        │                               │                            │
        │                         ● K ──┘                            │
        │                                                            │
        │  ════════════════════════════════════════════════════════  │
        │  breath: ░░░░████░░░░  (exhale)                            │
        │                                                            │
        │  focus: [A]  │  > open page A                              │
        └────────────────────────────────────────────────────────────┘
    """

    def __init__(
        self,
        garden: GardenState,
        width: int = 64,
        breath_position: float = 0.5,  # 0.0 - 1.0 in breath cycle
    ):
        self.garden = garden
        self.width = max(width, 50)
        self.breath_position = breath_position

    def render(self) -> str:
        """Render the garden view."""
        lines = []
        inner_width = self.width - 2

        # Title bar with time
        title = f" {self.garden.name} "
        time_str = f" t: {self.garden.elapsed_str} "
        left_space = (inner_width - len(title) - len(time_str)) // 2
        right_space = inner_width - len(title) - len(time_str) - left_space
        lines.append(f"┌{'─' * left_space}{title}{'─' * right_space}{time_str}─┐")

        # Empty line
        lines.append(f"│{' ' * inner_width}│")

        # Agent glyphs in simple layout
        lines.extend(self._render_agent_layout(inner_width))

        # Separator
        lines.append(f"│{' ' * inner_width}│")
        lines.append(f"│  {'═' * (inner_width - 4)}  │")

        # Breath cycle
        breath = self._render_breath()
        breath_phase = "exhale" if self.breath_position < 0.5 else "inhale"
        breath_line = f"  breath: {breath}  ({breath_phase})"
        lines.append(f"│{breath_line:{inner_width}}│")

        # Empty line
        lines.append(f"│{' ' * inner_width}│")

        # Focus line
        focus_str = f"[{self.garden.focus}]" if self.garden.focus else "[none]"
        focus_line = f"  focus: {focus_str}  │  > open page {self.garden.focus or '...'}"
        lines.append(f"│{focus_line:{inner_width}}│")

        # Bottom border
        lines.append(f"└{'─' * inner_width}┘")

        return "\n".join(lines)

    def _render_agent_layout(self, inner_width: int) -> List[str]:
        """Render agents in a simple spatial layout."""
        lines = []

        if not self.garden.agents:
            empty_line = "       (empty garden)"
            lines.append(f"│{empty_line:{inner_width}}│")
            return lines

        # Simple layout: show glyphs with composition arrows
        agent_list = list(self.garden.agents.values())

        # Group agents into rows
        agents_per_row = 4
        for i in range(0, len(agent_list), agents_per_row):
            row_agents = agent_list[i : i + agents_per_row]
            row_parts = []
            for agent in row_agents:
                glyph_str = agent.glyph.render()
                # Mark focus with brackets
                if agent.agent_id == self.garden.focus:
                    glyph_str = f"[{glyph_str}]"
                row_parts.append(f"{glyph_str:12}")

            row_line = "       " + "".join(row_parts)
            lines.append(f"│{row_line:{inner_width}}│")

            # Show composition arrows for this row
            for agent in row_agents:
                if agent.composes_with:
                    arrow_line = f"         └─▶ {', '.join(agent.composes_with[:2])}"
                    if len(arrow_line) < inner_width:
                        lines.append(f"│{arrow_line:{inner_width}}│")

        return lines

    def _render_breath(self) -> str:
        """Render the breath cycle indicator."""
        width = 12
        # Sine-wave-like pattern centered at position
        pattern = []
        for i in range(width):
            pos = i / width
            # Distance from current breath position (wrapping)
            dist = min(
                abs(pos - self.breath_position),
                abs(pos - self.breath_position + 1),
                abs(pos - self.breath_position - 1),
            )
            if dist < 0.2:
                pattern.append("█")
            elif dist < 0.3:
                pattern.append("▓")
            else:
                pattern.append("░")
        return "".join(pattern)


class LibraryRenderer:
    """
    Renders multiple gardens—the ecosystem/galaxy level.

    Example:
        ┌─ kgents library ───────────────────────────── t: 00:14:32 ─┐
        │                                                            │
        │  ┌─ garden:main ───────┐  ┌─ garden:experiment ─────┐      │
        │  │  ●A  ○B  ◐C         │  │  ◐A  ●B  ○C             │      │
        │  │       ●K            │  │       ◐K                │      │
        │  │  health: ████░      │  │  health: ██░░           │      │
        │  └─────────────────────┘  └─────────────────────────┘      │
        │           │                        │                       │
        │           └──────────┬─────────────┘                       │
        │                      ▼                                     │
        │           ┌─ garden:production ──────┐                     │
        │           │  ●A  ●B  ●C              │                     │
        │           │       ●K                 │                     │
        │           │  health: █████           │                     │
        │           └──────────────────────────┘                     │
        │                                                            │
        │  total gardens: 3  │  orchestration: converging            │
        │  > enter garden:main                                       │
        └────────────────────────────────────────────────────────────┘
    """

    def __init__(self, library: LibraryState, width: int = 64):
        self.library = library
        self.width = max(width, 50)

    def render(self) -> str:
        """Render the library view."""
        lines = []
        inner_width = self.width - 2

        # Calculate elapsed time
        elapsed = self.library.current_time - self.library.system_start
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_str = f" t: {hours:02d}:{minutes:02d}:{seconds:02d} "

        # Title bar
        title = f" {self.library.name} "
        left_space = (inner_width - len(title) - len(time_str)) // 2
        right_space = inner_width - len(title) - len(time_str) - left_space
        lines.append(f"┌{'─' * left_space}{title}{'─' * right_space}{time_str}─┐")

        # Empty line
        lines.append(f"│{' ' * inner_width}│")

        # Garden mini-cards
        for garden_name, garden in self.library.gardens.items():
            lines.extend(self._render_garden_card(garden, inner_width))
            lines.append(f"│{' ' * inner_width}│")

        # Status line
        total = len(self.library.gardens)
        status_line = (
            f"  total gardens: {total}  │  orchestration: {self.library.orchestration_status}"
        )
        lines.append(f"│{status_line:{inner_width}}│")

        # Focus line
        focus_garden = self.library.focus or "..."
        focus_line = f"  > enter {focus_garden}"
        lines.append(f"│{focus_line:{inner_width}}│")

        # Bottom border
        lines.append(f"└{'─' * inner_width}┘")

        return "\n".join(lines)

    def _render_garden_card(self, garden: GardenState, outer_width: int) -> List[str]:
        """Render a mini-card for a garden."""
        lines = []
        card_width = min(24, outer_width - 8)

        # Title
        title = f" {garden.name} "
        left_dash = (card_width - len(title)) // 2
        right_dash = card_width - len(title) - left_dash
        lines.append(
            f"│  ┌{'─' * left_dash}{title}{'─' * right_dash}┐{' ' * (outer_width - card_width - 4)}│"
        )

        # Glyph summary
        summary = garden.glyph_summary()
        if len(summary) > card_width - 4:
            summary = summary[: card_width - 7] + "..."
        lines.append(f"│  │  {summary:{card_width - 4}}│{' ' * (outer_width - card_width - 4)}│")

        # Health bar
        if garden.health is not None:
            health_bar = _progress_bar(garden.health, 5)
            health_line = f"health: {health_bar}"
            lines.append(
                f"│  │  {health_line:{card_width - 4}}│{' ' * (outer_width - card_width - 4)}│"
            )

        # Bottom
        lines.append(f"│  └{'─' * card_width}┘{' ' * (outer_width - card_width - 4)}│")

        return lines
