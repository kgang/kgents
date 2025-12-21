"""
Menu Generator: What suits my taste this morning?

Movement 3 of the Morning Coffee ritual. Presents challenge gradients —
invitations, not assignments. Kent picks based on how he feels *right now*.

Challenge Levels:
- GENTLE: Warmup, low stakes
- FOCUSED: Clear objective, moderate depth
- INTENSE: Deep work, high cognitive load
- SERENDIPITOUS: Follow curiosity (always available)

Inputs:
- TODO items from plans and NOW.md
- Garden/Weather context (what's active)
- Optional: Gardener season, Muse story arc

Patterns Applied:
- Multiplied Context (Pattern 3): context × item → placement
- Enum Property (Pattern 2): ChallengeLevel with metadata
- Signal Aggregation (Pattern 4): multiple sources → menu

See: spec/services/morning-coffee.md
"""

from __future__ import annotations

import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .types import (
    ChallengeLevel,
    ChallengeMenu,
    ConceptualWeather,
    GardenView,
    MenuItem,
)

# =============================================================================
# TODO Extraction
# =============================================================================


def extract_todos_from_plans(
    plans_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """
    Extract TODO items from plan files.

    Looks for:
    - [ ] unchecked markdown checkboxes
    - Lines starting with "TODO:"
    - Items in "## Next" or "## Tasks" sections

    Returns list of {text, source, section} dicts.
    """
    if plans_path is None:
        plans_path = Path.cwd() / "plans"

    path = Path(plans_path)
    if not path.exists():
        return []

    todos: list[dict[str, Any]] = []

    for md_file in path.glob("*.md"):
        if md_file.name.startswith("_"):
            continue

        content = md_file.read_text()
        plan_name = md_file.stem.replace("-", " ").title()

        # Extract unchecked checkboxes
        for match in re.finditer(r"- \[ \] (.+)", content):
            todos.append(
                {
                    "text": match.group(1).strip(),
                    "source": plan_name,
                    "section": "task",
                }
            )

        # Extract TODO: lines
        for match in re.finditer(r"TODO:\s*(.+)", content, re.IGNORECASE):
            todos.append(
                {
                    "text": match.group(1).strip(),
                    "source": plan_name,
                    "section": "inline",
                }
            )

    return todos


def extract_todos_from_now(
    now_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """
    Extract actionable items from NOW.md.

    Looks for:
    - [ ] unchecked checkboxes
    - "Next:" or "Focus:" sections
    """
    if now_path is None:
        now_path = Path.cwd() / "NOW.md"

    path = Path(now_path)
    if not path.exists():
        return []

    content = path.read_text()
    todos: list[dict[str, Any]] = []

    # Extract unchecked checkboxes
    for match in re.finditer(r"- \[ \] (.+)", content):
        todos.append(
            {
                "text": match.group(1).strip(),
                "source": "NOW.md",
                "section": "task",
            }
        )

    return todos


# =============================================================================
# Challenge Classification
# =============================================================================


def classify_challenge(item: str) -> ChallengeLevel:
    """
    Classify an item into a challenge level based on heuristics.

    Uses text analysis to estimate cognitive load:
    - Short, specific tasks → GENTLE
    - Clear objectives → FOCUSED
    - Complex, deep work → INTENSE
    """
    item_lower = item.lower()

    # Gentle indicators: small, quick, documentation
    gentle_keywords = [
        "test",
        "document",
        "comment",
        "cleanup",
        "typo",
        "fix minor",
        "update readme",
        "add log",
        "rename",
        "format",
        "lint",
        "small",
    ]
    if any(kw in item_lower for kw in gentle_keywords):
        return ChallengeLevel.GENTLE

    # Intense indicators: complex, design, architecture
    intense_keywords = [
        "architect",
        "design",
        "implement",
        "bootstrap",
        "regenerat",
        "refactor major",
        "rewrite",
        "solve",
        "optimize",
        "performance",
        "deep",
        "complex",
        "fundamental",
    ]
    if any(kw in item_lower for kw in intense_keywords):
        return ChallengeLevel.INTENSE

    # Default to focused (moderate complexity)
    return ChallengeLevel.FOCUSED


def estimate_cognitive_load(item: str) -> float:
    """
    Estimate cognitive load (0.0-1.0) for an item.

    Used for sorting within challenge levels.
    """
    item_lower = item.lower()

    # Start with base load
    load = 0.5

    # Increase for complexity indicators
    if any(kw in item_lower for kw in ["implement", "design", "architect"]):
        load += 0.2
    if any(kw in item_lower for kw in ["test", "verify", "validate"]):
        load += 0.1
    if len(item) > 80:  # Long descriptions = complex
        load += 0.1

    # Decrease for simplicity indicators
    if any(kw in item_lower for kw in ["fix", "update", "add"]):
        load -= 0.1
    if len(item) < 30:  # Short = simple
        load -= 0.1

    return max(0.0, min(1.0, load))


# =============================================================================
# Menu Generation
# =============================================================================


def generate_menu(
    plans_path: Path | str | None = None,
    now_path: Path | str | None = None,
    garden_view: GardenView | None = None,
    weather: ConceptualWeather | None = None,
    max_per_level: int = 3,
) -> ChallengeMenu:
    """
    Generate the challenge menu for Morning Coffee.

    Presents invitations grouped by challenge level.
    Serendipitous option is always available.

    Args:
        plans_path: Path to plans directory
        now_path: Path to NOW.md
        garden_view: Optional GardenView for context
        weather: Optional ConceptualWeather for context
        max_per_level: Max items per challenge level

    Returns:
        ChallengeMenu with gentle, focused, and intense options
    """
    # Collect TODOs from all sources
    plan_todos = extract_todos_from_plans(plans_path)
    now_todos = extract_todos_from_now(now_path)

    all_todos = plan_todos + now_todos

    # Add items derived from weather patterns if available
    if weather:
        weather_items = _items_from_weather(weather)
        all_todos.extend(weather_items)

    # Classify and group by level
    gentle_items: list[MenuItem] = []
    focused_items: list[MenuItem] = []
    intense_items: list[MenuItem] = []

    for todo in all_todos:
        level = classify_challenge(todo["text"])
        item = MenuItem(
            label=_truncate(todo["text"], 60),
            description=f"From {todo['source']}",
            level=level,
            source=todo["source"],
        )

        if level == ChallengeLevel.GENTLE:
            gentle_items.append(item)
        elif level == ChallengeLevel.FOCUSED:
            focused_items.append(item)
        elif level == ChallengeLevel.INTENSE:
            intense_items.append(item)

    # Sort by estimated cognitive load and limit
    gentle_items.sort(key=lambda x: estimate_cognitive_load(x.label))
    focused_items.sort(key=lambda x: estimate_cognitive_load(x.label))
    intense_items.sort(key=lambda x: estimate_cognitive_load(x.label), reverse=True)

    # Generate serendipitous prompt based on context
    serendipitous_prompt = _generate_serendipitous_prompt(garden_view, weather)

    return ChallengeMenu(
        gentle=tuple(gentle_items[:max_per_level]),
        focused=tuple(focused_items[:max_per_level]),
        intense=tuple(intense_items[:max_per_level]),
        serendipitous_prompt=serendipitous_prompt,
        generated_at=datetime.now(),
    )


def _items_from_weather(weather: ConceptualWeather) -> list[dict[str, Any]]:
    """Extract actionable items from weather patterns."""
    items: list[dict[str, Any]] = []

    # Scaffolding patterns suggest active work
    for pattern in weather.scaffolding:
        items.append(
            {
                "text": f"Continue: {pattern.label}",
                "source": "Weather",
                "section": "scaffolding",
            }
        )

    # Tension patterns suggest resolution needed
    for pattern in weather.tension:
        items.append(
            {
                "text": f"Address: {pattern.label}",
                "source": "Weather",
                "section": "tension",
            }
        )

    return items


def _generate_serendipitous_prompt(
    garden: GardenView | None,
    weather: ConceptualWeather | None,
) -> str:
    """Generate a contextual serendipitous prompt."""
    prompts = [
        "What caught your eye in the garden view?",
        "What's pulling your curiosity this morning?",
        "Follow the thread that's tugging at you.",
    ]

    # If we have garden context, make it specific
    if garden and not garden.is_empty:
        if garden.seeds:
            return "Which seed wants to sprout today?"
        if garden.sprouting:
            return "What's ready to grow a little more?"

    # If we have weather context
    if weather and weather.emerging:
        return "What new pattern wants to emerge?"

    # Default
    return prompts[0]


def _truncate(text: str, max_len: int) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


# =============================================================================
# Async Variant
# =============================================================================


async def generate_menu_async(
    plans_path: Path | str | None = None,
    now_path: Path | str | None = None,
    garden_view: GardenView | None = None,
    weather: ConceptualWeather | None = None,
    max_per_level: int = 3,
) -> ChallengeMenu:
    """
    Async version of generate_menu.

    Runs sync operations in thread pool for non-blocking IO.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: generate_menu(
            plans_path=plans_path,
            now_path=now_path,
            garden_view=garden_view,
            weather=weather,
            max_per_level=max_per_level,
        ),
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "extract_todos_from_plans",
    "extract_todos_from_now",
    "classify_challenge",
    "estimate_cognitive_load",
    "generate_menu",
    "generate_menu_async",
]
