"""
ASCII Projection for Gardener-Logos.

Beautiful CLI rendering of the garden state with:
- Season-aware styling
- Progress bars for plots
- Gesture history
- Health indicators

See: spec/protocols/gardener-logos.md Part IV.2
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..garden import GardenState
    from ..personality import TendingPersonality
    from ..plots import PlotState


def project_garden_to_ascii(
    garden: "GardenState",
    personality: "TendingPersonality | None" = None,
    width: int = 72,
    show_gestures: int = 5,
) -> str:
    """
    Project garden state to ASCII art for CLI.

    Layout:
    ┌────────────────────────────────────────────────────────────────────────┐
    │ 🌱 GARDEN                                                Season: BLOOMING │
    ├────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │   PLOTS                                                                 │
    │   ├── coalition-forge ████████░░ 80% [🌸 BLOOMING]                     │
    │   ├── gestalt-live    ████░░░░░░ 40% [🌱 SPROUTING]                    │
    │   └── prompt-logos    ██████████ 100% [🌾 HARVEST]                      │
    │                                                                         │
    │   SESSION: Research Phase | SENSE                                       │
    │   ├── Intent: "Unify Gardener and Prompt Logos"                         │
    │   └── Crystals: 3 relevant from Brain                                   │
    │                                                                         │
    │   RECENT GESTURES                                                       │
    │   └── 10:30 observe concept.prompt.* → "Strong infrastructure"          │
    │   └── 10:25 water concept.prompt.task → "Added security checks"         │
    │                                                                         │
    │   Health: ████████░░ 80%  |  Entropy: █████████░ 90%                    │
    │                                                                         │
    └────────────────────────────────────────────────────────────────────────┘
    """
    from ..personality import default_personality

    if personality is None:
        personality = default_personality()

    lines: list[str] = []

    # Top border
    border = "┌" + "─" * (width - 2) + "┐"
    lines.append(border)

    # Header with season
    season = garden.season
    season_str = f"Season: {season.name}"
    garden_label = f"{season.emoji} GARDEN"
    padding = width - len(garden_label) - len(season_str) - 4
    header = f"│ {garden_label}{' ' * padding}{season_str} │"
    lines.append(header)

    # Separator
    lines.append("├" + "─" * (width - 2) + "┤")

    # Greeting (personalized)
    greeting = personality.craft_greeting(garden)
    lines.append(_pad_line(f"  {greeting}", width))
    lines.append(_pad_line("", width))

    # Plots section
    if garden.plots:
        lines.append(_pad_line("  PLOTS", width))
        plot_names = list(garden.plots.keys())
        for i, name in enumerate(plot_names):
            plot = garden.plots[name]
            is_last = i == len(plot_names) - 1
            prefix = "└──" if is_last else "├──"

            # Progress bar (10 chars)
            progress = int(plot.progress * 10)
            bar = "█" * progress + "░" * (10 - progress)
            pct = f"{plot.progress * 100:.0f}%"

            # Season indicator
            effective_season = plot.get_effective_season(garden.season)
            season_indicator = f"[{effective_season.emoji}]"

            # Mark active plot
            active_marker = " ◀" if name == garden.active_plot else ""

            plot_line = f"  {prefix} {plot.display_name:<16} {bar} {pct:>4} {season_indicator}{active_marker}"
            lines.append(_pad_line(plot_line, width))

        lines.append(_pad_line("", width))

    # Session info (if linked)
    if garden.session_id:
        lines.append(_pad_line("  SESSION", width))
        lines.append(_pad_line(f"  ├── ID: {garden.session_id[:8]}...", width))
        if garden.memory_crystals:
            lines.append(
                _pad_line(f"  └── Crystals: {len(garden.memory_crystals)} from Brain", width)
            )
        lines.append(_pad_line("", width))

    # Recent gestures
    if garden.recent_gestures and show_gestures > 0:
        lines.append(_pad_line("  RECENT GESTURES", width))
        gestures = garden.recent_gestures[-show_gestures:]
        for i, gesture in enumerate(reversed(gestures)):  # Most recent first
            is_last = i == len(gestures) - 1
            prefix = "└──" if is_last else "├──"
            display = gesture.display()
            # Truncate if needed
            max_len = width - 10
            if len(display) > max_len:
                display = display[: max_len - 3] + "..."
            lines.append(_pad_line(f"  {prefix} {display}", width))
        lines.append(_pad_line("", width))

    # Health and entropy bars
    health_pct = garden.metrics.health_score
    health_bar = _progress_bar(health_pct, 10)
    entropy_remaining = max(0, garden.metrics.entropy_budget - garden.metrics.entropy_spent)
    entropy_pct = (
        entropy_remaining / garden.metrics.entropy_budget
        if garden.metrics.entropy_budget > 0
        else 0
    )
    entropy_bar = _progress_bar(entropy_pct, 10)

    status_line = (
        f"  Health: {health_bar} {health_pct:.0%}  │  Entropy: {entropy_bar} {entropy_pct:.0%}"
    )
    lines.append(_pad_line(status_line, width))
    lines.append(_pad_line("", width))

    # Bottom border
    lines.append("└" + "─" * (width - 2) + "┘")

    return "\n".join(lines)


def project_plot_to_ascii(
    plot: "PlotState",
    garden_season: "GardenState",
    width: int = 60,
) -> str:
    """
    Project a single plot to ASCII art.

    Detailed view of one plot including:
    - Progress
    - Prompts in the plot
    - Recent momentum
    """
    lines: list[str] = []

    # Border
    lines.append("┌" + "─" * (width - 2) + "┐")

    # Header
    effective_season = plot.get_effective_season(garden_season.season)
    header = f"│ {effective_season.emoji} {plot.display_name}"
    header = header + " " * (width - len(header) - 1) + "│"
    lines.append(header)

    lines.append("├" + "─" * (width - 2) + "┤")

    # Path and linkages
    lines.append(_pad_line(f"  Path: {plot.path}", width))
    if plot.plan_path:
        lines.append(_pad_line(f"  Plan: {plot.plan_path}", width))
    if plot.crown_jewel:
        lines.append(_pad_line(f"  Crown Jewel: {plot.crown_jewel}", width))

    lines.append(_pad_line("", width))

    # Progress
    progress_bar = _progress_bar(plot.progress, 20)
    lines.append(_pad_line(f"  Progress: {progress_bar} {plot.progress:.0%}", width))

    # Rigidity
    rigidity_bar = _progress_bar(plot.rigidity, 10)
    lines.append(_pad_line(f"  Rigidity: {rigidity_bar} {plot.rigidity:.0%}", width))

    lines.append(_pad_line("", width))

    # Prompts
    if plot.prompts:
        lines.append(_pad_line(f"  Prompts ({len(plot.prompts)}):", width))
        for prompt_id in plot.prompts[:5]:
            lines.append(_pad_line(f"    • {prompt_id}", width))
        if len(plot.prompts) > 5:
            lines.append(_pad_line(f"    ... and {len(plot.prompts) - 5} more", width))
        lines.append(_pad_line("", width))

    # Tags
    if plot.tags:
        tags_str = " ".join(f"#{tag}" for tag in plot.tags[:5])
        lines.append(_pad_line(f"  Tags: {tags_str}", width))
        lines.append(_pad_line("", width))

    # Bottom border
    lines.append("└" + "─" * (width - 2) + "┘")

    return "\n".join(lines)


def _pad_line(content: str, width: int) -> str:
    """Pad a line to fit within width with borders."""
    # Account for emoji width (some take 2 chars)
    visible_len = len(content)
    padding_needed = width - visible_len - 2
    if padding_needed < 0:
        # Truncate if too long
        content = content[: width - 5] + "..."
        padding_needed = 0
    return f"│{content}{' ' * padding_needed}│"


def _progress_bar(value: float, length: int = 10) -> str:
    """Create a progress bar string."""
    filled = int(value * length)
    return "█" * filled + "░" * (length - filled)


__all__ = [
    "project_garden_to_ascii",
    "project_plot_to_ascii",
]
