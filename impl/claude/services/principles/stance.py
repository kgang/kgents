"""
Stance Detection: Determines principle consumption stance from context.

The Four Stances (from spec/principles/consumption.md):
- Genesis: Becoming - which principles apply?
- Poiesis: Making - how do I build according to principles?
- Krisis: Judgment - does this embody the principles?
- Therapeia: Healing - which principle was violated?

Detection uses signal matching against observer context and task.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from .types import STANCE_SLICES, Stance

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Detection Signals ===

# Priority: Therapeia > Krisis > Poiesis > Genesis
# (Healing is most specific; Genesis is default)

THERAPEIA_SIGNALS: frozenset[str] = frozenset(
    {
        "fix",
        "broken",
        "failing",
        "wrong",
        "help",
        "error",
        "debug",
        "issue",
        "problem",
        "violation",
        "bug",
        "failed",
        "doesn't work",
        "not working",
        "crashed",
        "healing",
        "repair",
        "restore",
    }
)

KRISIS_SIGNALS: frozenset[str] = frozenset(
    {
        "review",
        "check",
        "does this",
        "evaluate",
        "quality",
        "assess",
        "audit",
        "verify",
        "validate",
        "judgment",
        "judge",
        "criteria",
        "pass",
        "fail",
        "test",
        "critique",
        "examine",
    }
)

POIESIS_SIGNALS: frozenset[str] = frozenset(
    {
        "build",
        "add",
        "implement",
        "code",
        "make",
        "create",
        "develop",
        "construct",
        "write",
        "design",
        "architect",
        "engineer",
        "refactor",
        "modify",
        "extend",
        "integrate",
    }
)

GENESIS_SIGNALS: frozenset[str] = frozenset(
    {
        "start",
        "begin",
        "create",
        "new",
        "first",
        "initial",
        "inception",
        "origin",
        "genesis",
        "bootstrap",
        "seed",
        "what",
        "why",
        "which",
        "explore",
    }
)


def _score_signals(text: str, signals: frozenset[str]) -> int:
    """Count how many signals match in the text."""
    text_lower = text.lower()
    score = 0
    for signal in signals:
        if signal in text_lower:
            score += 1
    return score


def detect_stance(
    observer: "Umwelt[Any, Any] | Any | None" = None,
    task: str | None = None,
    context: str | None = None,
) -> Stance:
    """
    Detect stance from observer context and task.

    Resolution priority:
    1. Therapeia (healing signals - most specific)
    2. Krisis (judgment signals)
    3. Poiesis (building signals)
    4. Genesis (default / exploration signals)

    Args:
        observer: Optional Umwelt or Observer for context extraction
        task: Optional task description
        context: Optional additional context string

    Returns:
        Detected Stance
    """
    # Combine all context
    text_parts: list[str] = []

    if task:
        text_parts.append(task)

    if context:
        text_parts.append(context)

    if observer:
        # Check if it's a full Umwelt (has .dna) or lightweight Observer
        if hasattr(observer, "dna"):
            # Full Umwelt - extract context from DNA
            dna = observer.dna
            if hasattr(dna, "context"):
                text_parts.append(str(dna.context))
            if hasattr(dna, "task"):
                text_parts.append(str(dna.task))
            if hasattr(dna, "archetype"):
                # Some archetypes imply stances
                archetype = dna.archetype
                if archetype == "reviewer":
                    return Stance.KRISIS
                elif archetype == "debugger":
                    return Stance.THERAPEIA
                elif archetype == "builder" or archetype == "engineer":
                    return Stance.POIESIS
        elif hasattr(observer, "archetype"):
            # Lightweight Observer - just check archetype
            archetype = observer.archetype
            if archetype == "reviewer":
                return Stance.KRISIS
            elif archetype == "debugger":
                return Stance.THERAPEIA
            elif archetype == "builder" or archetype == "engineer":
                return Stance.POIESIS

    # No text to analyze - default to Genesis
    if not text_parts:
        return Stance.GENESIS

    combined_text = " ".join(text_parts)

    # Score each stance
    scores = {
        Stance.THERAPEIA: _score_signals(combined_text, THERAPEIA_SIGNALS),
        Stance.KRISIS: _score_signals(combined_text, KRISIS_SIGNALS),
        Stance.POIESIS: _score_signals(combined_text, POIESIS_SIGNALS),
        Stance.GENESIS: _score_signals(combined_text, GENESIS_SIGNALS),
    }

    # Find highest score with priority ordering
    # Priority: Therapeia > Krisis > Poiesis > Genesis
    priority_order = [Stance.THERAPEIA, Stance.KRISIS, Stance.POIESIS, Stance.GENESIS]

    max_score = 0
    best_stance = Stance.GENESIS

    for stance in priority_order:
        if scores[stance] > max_score:
            max_score = scores[stance]
            best_stance = stance

    return best_stance


def get_stance_slices(stance: Stance) -> tuple[str, ...]:
    """
    Get principle file slices for a stance.

    Args:
        stance: The stance

    Returns:
        Tuple of filenames to load
    """
    return STANCE_SLICES[stance]


def get_task_ad_slices(task: str) -> tuple[str, ...]:
    """
    Get AD file slices relevant to a task (for Poiesis stance).

    Args:
        task: Task description

    Returns:
        Tuple of AD filenames to include
    """
    from .types import AD_TASK_MAPPING

    task_lower = task.lower()

    # Find matching task patterns
    matching_ads: set[int] = set()
    for pattern, ads in AD_TASK_MAPPING.items():
        if pattern in task_lower or any(word in task_lower for word in pattern.split("-")):
            matching_ads.update(ads)

    if not matching_ads:
        return ()

    # Convert to filenames
    return tuple(f"decisions/AD-{ad:03d}*.md" for ad in sorted(matching_ads))


def stance_from_aspect(aspect: str) -> Stance:
    """
    Infer stance from the aspect being invoked.

    Some aspects imply a specific stance:
    - check -> Krisis
    - heal -> Therapeia
    - manifest -> depends on observer

    Args:
        aspect: AGENTESE aspect name

    Returns:
        Inferred stance (or Genesis as default)
    """
    aspect_stance_map: dict[str, Stance] = {
        "check": Stance.KRISIS,
        "heal": Stance.THERAPEIA,
        "teach": Stance.GENESIS,  # Teaching usually starts fresh
    }

    return aspect_stance_map.get(aspect, Stance.GENESIS)


def validate_stance_transition(from_stance: Stance, to_stance: Stance) -> bool:
    """
    Validate that a stance transition follows the consumption cycle.

    The cycle is:
    - Genesis -> Poiesis
    - Poiesis -> Krisis
    - Krisis -> Poiesis (success: refine)
    - Krisis -> Therapeia (failure: heal)
    - Therapeia -> Poiesis (healed: rebuild)

    Args:
        from_stance: Current stance
        to_stance: Desired stance

    Returns:
        True if transition is valid
    """
    valid_transitions: dict[Stance, set[Stance]] = {
        Stance.GENESIS: {Stance.POIESIS},
        Stance.POIESIS: {Stance.KRISIS},
        Stance.KRISIS: {Stance.POIESIS, Stance.THERAPEIA},
        Stance.THERAPEIA: {Stance.POIESIS},
    }

    return to_stance in valid_transitions.get(from_stance, set())


# === Exports ===

__all__ = [
    "detect_stance",
    "get_stance_slices",
    "get_task_ad_slices",
    "stance_from_aspect",
    "validate_stance_transition",
    # Signals for testing
    "GENESIS_SIGNALS",
    "POIESIS_SIGNALS",
    "KRISIS_SIGNALS",
    "THERAPEIA_SIGNALS",
]
