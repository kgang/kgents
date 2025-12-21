"""
Morning Coffee CLI Formatting: Rich terminal output for the liminal ritual.

This module provides formatters that transform Coffee data structures into
beautiful terminal output with boxes, emoji, and thoughtful spacing.

"The morning mind knows things the afternoon mind has forgotten."

Design Principles:
1. Non-demanding: Garden/Weather are observations, not interrogations
2. Scannable: Key information visible at a glance
3. Warm: Feels like warming up, not booting up
4. Skippable: Clear exits at every movement

See: spec/services/morning-coffee.md
"""

from __future__ import annotations

from datetime import date
from typing import Any

# =============================================================================
# Box Drawing Characters
# =============================================================================

BOX_TOP_LEFT = "┌"
BOX_TOP_RIGHT = "┐"
BOX_BOTTOM_LEFT = "└"
BOX_BOTTOM_RIGHT = "┘"
BOX_HORIZONTAL = "─"
BOX_VERTICAL = "│"
BOX_T_DOWN = "┬"
BOX_T_UP = "┴"
BOX_T_LEFT = "├"
BOX_T_RIGHT = "┤"
BOX_CROSS = "┼"

DEFAULT_WIDTH = 68


# =============================================================================
# Utilities
# =============================================================================


def _box(title: str, content: str, width: int = DEFAULT_WIDTH) -> str:
    """
    Wrap content in a box with a title.

    Example:
        ┌───────────────────────────────────────────────────────────────────┐
        │  Garden View                                                      │
        ├───────────────────────────────────────────────────────────────────┤
        │  Content here...                                                  │
        └───────────────────────────────────────────────────────────────────┘
    """
    lines = []
    inner_width = width - 2  # Account for │ on each side

    # Top border
    lines.append(f"{BOX_TOP_LEFT}{BOX_HORIZONTAL * inner_width}{BOX_TOP_RIGHT}")

    # Title
    title_padded = f"  {title}".ljust(inner_width)
    lines.append(f"{BOX_VERTICAL}{title_padded}{BOX_VERTICAL}")

    # Separator
    lines.append(f"{BOX_T_LEFT}{BOX_HORIZONTAL * inner_width}{BOX_T_RIGHT}")

    # Content
    for line in content.split("\n"):
        # Truncate if too long
        if len(line) > inner_width - 2:
            line = line[: inner_width - 5] + "..."
        padded = f"  {line}".ljust(inner_width)
        lines.append(f"{BOX_VERTICAL}{padded}{BOX_VERTICAL}")

    # Bottom border
    lines.append(f"{BOX_BOTTOM_LEFT}{BOX_HORIZONTAL * inner_width}{BOX_BOTTOM_RIGHT}")

    return "\n".join(lines)


def _truncate(text: str, max_len: int = 50) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


# =============================================================================
# Garden View Formatter
# =============================================================================


def format_garden_view(data: dict[str, Any]) -> str:
    """
    Format GardenView as rich CLI output.

    Input: GardenView.to_dict() or GardenResponse

    Example output:
    ┌───────────────────────────────────────────────────────────────────┐
    │  🌱 Yesterday's Garden                                           │
    ├───────────────────────────────────────────────────────────────────┤
    │                                                                   │
    │  🌾 HARVEST (complete)                                           │
    │     • Brain persistence hardening                                │
    │     • New test: test_semantic_consistency.py                     │
    │                                                                   │
    │  🌿 GROWING (in progress)                                        │
    │     • Gestalt crystalline rendering (85%)                        │
    │                                                                   │
    │  🌱 SPROUTING (emerging)                                         │
    │     • ASHC L0 kernel design                                      │
    │                                                                   │
    │  🌰 SEEDS (ideas)                                                │
    │     • Voice archaeology patterns                                 │
    │                                                                   │
    └───────────────────────────────────────────────────────────────────┘
    """
    lines = []

    # Categories with their items
    categories = [
        ("🌾 HARVEST", "harvest", "complete"),
        ("🌿 GROWING", "growing", "in progress"),
        ("🌱 SPROUTING", "sprouting", "emerging"),
        ("🌰 SEEDS", "seeds", "ideas"),
    ]

    has_any = False
    for emoji_label, key, desc in categories:
        items = data.get(key, [])
        if items:
            has_any = True
            lines.append(f"{emoji_label} ({desc})")
            for item in items[:5]:  # Limit to 5 per category
                desc_text = item.get("description", str(item))
                if isinstance(desc_text, str):
                    lines.append(f"   • {_truncate(desc_text, 55)}")
            lines.append("")  # Spacing

    if not has_any:
        lines.append("Nothing grew while you slept. The garden rests.")
        lines.append("")
        lines.append("Perhaps today will be a planting day.")

    content = "\n".join(lines).rstrip()
    return _box("🌱 Yesterday's Garden", content)


# =============================================================================
# Weather Formatter
# =============================================================================


def format_weather(data: dict[str, Any]) -> str:
    """
    Format ConceptualWeather as rich CLI output.

    Example output:
    ┌───────────────────────────────────────────────────────────────────┐
    │  🌤️ Conceptual Weather                                           │
    ├───────────────────────────────────────────────────────────────────┤
    │                                                                   │
    │  🔄 REFACTORING                                                  │
    │     S-gents → D-gents consolidation                              │
    │                                                                   │
    │  🌊 EMERGING                                                     │
    │     Failure-as-Evidence principle taking shape                   │
    │                                                                   │
    │  🏗️ SCAFFOLDING                                                  │
    │     ASHC compiler architecture building                          │
    │                                                                   │
    │  ⚡ TENSION                                                      │
    │     Depth vs. breadth in crown jewel work                        │
    │                                                                   │
    └───────────────────────────────────────────────────────────────────┘
    """
    lines = []

    categories = [
        ("🔄 REFACTORING", "refactoring"),
        ("🌊 EMERGING", "emerging"),
        ("🏗️ SCAFFOLDING", "scaffolding"),
        ("⚡ TENSION", "tension"),
    ]

    has_any = False
    for emoji_label, key in categories:
        patterns = data.get(key, [])
        if patterns:
            has_any = True
            lines.append(f"{emoji_label}")
            for pattern in patterns[:3]:  # Limit to 3 per category
                label = pattern.get("label", str(pattern))
                if isinstance(label, str):
                    lines.append(f"   {_truncate(label, 55)}")
            lines.append("")  # Spacing

    if not has_any:
        lines.append("Clear skies. No significant conceptual movements.")
        lines.append("")
        lines.append("A calm day for focused work.")

    content = "\n".join(lines).rstrip()
    return _box("🌤️ Conceptual Weather", content)


# =============================================================================
# Menu Formatter
# =============================================================================


def format_menu(data: dict[str, Any]) -> str:
    """
    Format ChallengeMenu as rich CLI output.

    Example output:
    ┌───────────────────────────────────────────────────────────────────┐
    │  🍳 Today's Menu                                                 │
    ├───────────────────────────────────────────────────────────────────┤
    │                                                                   │
    │  🧘 GENTLE (warmup, low stakes)                                  │
    │     1. Write a test for existing behavior                        │
    │     2. Document a pattern you discovered                         │
    │                                                                   │
    │  🎯 FOCUSED (clear objective, moderate depth)                    │
    │     3. Wire ASHC L0 kernel to AST                                │
    │     4. Complete Gestalt facet interaction                        │
    │                                                                   │
    │  🔥 INTENSE (deep work, high cognitive load)                     │
    │     5. Bootstrap regeneration implementation                     │
    │                                                                   │
    │  🎲 SERENDIPITOUS                                                │
    │     "What caught your eye in the garden view?"                   │
    │                                                                   │
    └───────────────────────────────────────────────────────────────────┘
    """
    lines = []
    item_num = 1

    categories = [
        ("🧘 GENTLE", "gentle", "warmup, low stakes"),
        ("🎯 FOCUSED", "focused", "clear objective, moderate depth"),
        ("🔥 INTENSE", "intense", "deep work, high cognitive load"),
    ]

    for emoji_label, key, desc in categories:
        items = data.get(key, [])
        if items:
            lines.append(f"{emoji_label} ({desc})")
            for item in items[:3]:  # Limit to 3 per level
                label = item.get("label", str(item))
                if isinstance(label, str):
                    lines.append(f"   {item_num}. {_truncate(label, 50)}")
                    item_num += 1
            lines.append("")  # Spacing

    # Always show serendipitous option
    prompt = data.get("serendipitous_prompt", "What caught your eye in the garden view?")
    lines.append("🎲 SERENDIPITOUS")
    lines.append(f'   "{prompt}"')
    lines.append("")

    content = "\n".join(lines).rstrip()
    return _box("🍳 Today's Menu", content)


# =============================================================================
# Voice Capture Formatter
# =============================================================================


def format_capture_questions() -> str:
    """
    Format voice capture questions for interactive flow.

    Returns prompts for the CLI to display.
    """
    lines = [
        "📝 Fresh Capture",
        "",
        "Answer what feels right. Skip with Enter.",
        "",
        "  Q1: What's on your mind that has nothing to do with code?",
        "      (Dreams, ideas, something from breakfast, a feeling...)",
        "",
        "  Q2: Looking at the garden view, what catches your eye?",
        "      (A file, a pattern, something that sparked curiosity...)",
        "",
        "  Q3: What would make today feel like a good day?",
        "      (Ship one feature, understand the problem, have fun...)",
        "",
        "  Q4: Any other thoughts? (optional)",
        "      (Energy level, mood, anything else...)",
    ]
    return "\n".join(lines)


def format_captured_voice(data: dict[str, Any]) -> str:
    """
    Format the confirmation after a voice is captured.
    """
    voice = data.get("voice", {})
    saved_path = data.get("saved_path", "")

    lines = ["✨ Voice captured", ""]

    if voice.get("success_criteria"):
        lines.append(f'   Success criteria: "{_truncate(voice["success_criteria"], 50)}"')
        lines.append("")

    if saved_path:
        lines.append(f"   Saved to: {saved_path}")

    lines.append("")
    lines.append("   This becomes your voice anchor for the day.")

    return _box("📝 Fresh Capture", "\n".join(lines))


# =============================================================================
# Manifest Formatter
# =============================================================================


def format_manifest(data: dict[str, Any]) -> str:
    """
    Format ritual manifest (status overview).
    """
    lines = []

    # Status
    if data.get("today_voice"):
        lines.append("☕ Morning Coffee complete today")
        voice = data["today_voice"]
        if voice.get("success_criteria"):
            lines.append("")
            lines.append(f'   Today\'s goal: "{_truncate(voice["success_criteria"], 45)}"')
    elif data.get("is_active"):
        movement = data.get("current_movement", "unknown")
        lines.append(f"☕ Ritual in progress: {movement}")
    else:
        lines.append("☕ Morning Coffee ready")
        lines.append("")
        lines.append("   Run `kg coffee --quick` for garden + menu")
        lines.append("   Run `kg coffee garden` to start the full ritual")

    # Last ritual
    if data.get("last_ritual"):
        lines.append("")
        lines.append(f"   Last ritual: {data['last_ritual']}")

    return "\n".join(lines)


# =============================================================================
# History Formatter
# =============================================================================


def format_history(data: dict[str, Any]) -> str:
    """
    Format voice capture history.
    """
    voices = data.get("voices", [])
    patterns = data.get("patterns")

    if not voices:
        return "No voice captures yet.\n\nRun `kg coffee capture` to record your first."

    lines = []

    for voice in voices[:7]:
        capture_date = voice.get("captured_date", "unknown")
        success = voice.get("success_criteria", "")
        emoji = "✅" if voice.get("is_substantive") else "○"

        lines.append(f"{emoji} {capture_date}")
        if success:
            lines.append(f"   {_truncate(success, 55)}")
        lines.append("")

    if patterns and patterns.get("common_themes"):
        lines.append("📊 Common themes: " + ", ".join(patterns["common_themes"][:3]))

    content = "\n".join(lines).rstrip()
    return _box("📚 Voice History", content)


# =============================================================================
# Transition Formatter
# =============================================================================


def format_transition(chosen_item: dict[str, Any] | None = None) -> str:
    """
    Format the transition message when beginning work.

    This is the culmination of the ritual — the bridge into work state.
    """
    lines = [
        "☕ Transitioning to work...",
        "",
    ]

    if chosen_item:
        label = chosen_item.get("label", "")
        agentese_path = chosen_item.get("agentese_path", "")

        lines.append(f"   → Selected: {label}")

        if agentese_path:
            lines.append(f"   → Path: {agentese_path}")

        # If there's a relevant file, show it
        source = chosen_item.get("source", "")
        if source and source != "todo":
            lines.append(f"   → Source: {source}")

        lines.append("")

    lines.append("☀️ Ready. The morning is yours.")

    return "\n".join(lines)


# =============================================================================
# Full Ritual Formatter
# =============================================================================


def format_ritual_start() -> str:
    """Header for starting the full ritual."""
    return """
☕ Morning Coffee

"The musician doesn't start with the hardest passage.
 She tunes, breathes, plays a scale."

Press Ctrl+C to exit at any time.
"""


def format_movement_separator(movement_name: str) -> str:
    """Separator between movements."""
    return f"\n{'─' * 40}\n{movement_name}\n{'─' * 40}\n"


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Box utilities
    "DEFAULT_WIDTH",
    # Formatters
    "format_garden_view",
    "format_weather",
    "format_menu",
    "format_capture_questions",
    "format_captured_voice",
    "format_manifest",
    "format_history",
    "format_transition",
    "format_ritual_start",
    "format_movement_separator",
]
