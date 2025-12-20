"""
Alive Workshop Aesthetic: Sympathetic error handling with Studio Ghibli warmth.

The formal verification system should feel like an alive workshop — organic,
warm, and breathing. Errors are learning opportunities, not failures.

> "The stream finds a way around the boulder."

This module provides:
- Sympathetic error messages with educational content
- Living Earth color palette for visualizations
- Progressive disclosure patterns
- Celebration of success
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ErrorCategory(str, Enum):
    """Categories of verification errors."""

    TOPOLOGY = "topology"
    CATEGORICAL = "categorical"
    SHEAF = "sheaf"
    TRACE = "trace"
    SEMANTIC = "semantic"
    DERIVATION = "derivation"
    HOTT = "hott"
    SYSTEM = "system"


class Severity(str, Enum):
    """Error severity levels."""

    INFO = "info"
    GENTLE = "gentle"  # Not "warning" — we're sympathetic
    CONCERN = "concern"  # Not "error" — we care
    CRITICAL = "critical"


# =============================================================================
# Living Earth Color Palette
# =============================================================================

class LivingEarthPalette:
    """
    Color palette inspired by Studio Ghibli's living worlds.
    
    Warm earth tones, living greens, and gentle glows.
    """

    # Earth tones (grounding, stability)
    WARM_EARTH = "#8B7355"
    RICH_SOIL = "#5C4033"
    CLAY = "#B87333"
    SANDSTONE = "#D2B48C"

    # Living greens (growth, health)
    MOSS = "#8A9A5B"
    FERN = "#4F7942"
    SPRING_LEAF = "#A8D08D"
    FOREST_DEEP = "#228B22"

    # Water (flow, clarity)
    STREAM = "#87CEEB"
    POND = "#5F9EA0"
    MIST = "#B0E0E6"

    # Ghibli glow (magic, warmth)
    SUNSET_GLOW = "#FFB347"
    LANTERN = "#FFD700"
    FIREFLY = "#F0E68C"
    SPIRIT_LIGHT = "#FFFACD"

    # Status colors (gentle, not alarming)
    SUCCESS = "#90EE90"  # Soft green, not harsh
    GENTLE_WARNING = "#FFE4B5"  # Moccasin, warm
    CONCERN = "#FFA07A"  # Light salmon, caring
    CRITICAL = "#CD5C5C"  # Indian red, serious but not angry

    # Text colors
    TEXT_PRIMARY = "#2F4F4F"  # Dark slate gray
    TEXT_SECONDARY = "#696969"  # Dim gray
    TEXT_MUTED = "#A9A9A9"  # Dark gray


# =============================================================================
# Sympathetic Messages
# =============================================================================

SYMPATHETIC_MESSAGES: dict[str, dict[str, str]] = {
    # Categorical law violations
    "composition_associativity": {
        "title": "Composition Order Matters Here",
        "message": (
            "These agents don't quite compose the way we expected. "
            "When we group them differently, we get different results. "
            "Let me show you what's happening."
        ),
        "encouragement": (
            "This often happens when agents have hidden state or side effects. "
            "The good news: once we find the cause, the fix is usually straightforward."
        ),
    },
    "identity_law": {
        "title": "Identity Isn't Quite Invisible",
        "message": (
            "The identity morphism should be invisible — composing with it "
            "shouldn't change anything. But something's shifting here."
        ),
        "encouragement": (
            "Identity violations often reveal subtle assumptions in our code. "
            "Finding them makes the whole system more robust."
        ),
    },
    "functor_preservation": {
        "title": "Structure Got Lost in Translation",
        "message": (
            "This functor should preserve the shape of compositions, "
            "but something's getting rearranged along the way."
        ),
        "encouragement": (
            "Functors are like careful translators — they should preserve meaning. "
            "Let's find where the translation went astray."
        ),
    },

    # Sheaf and topology
    "sheaf_conflict": {
        "title": "Local Views Don't Quite Align",
        "message": (
            "I found some perspectives that don't quite agree where they overlap. "
            "It's like two maps of the same territory with different details."
        ),
        "encouragement": (
            "Sheaf conflicts often reveal hidden assumptions or missing constraints. "
            "Resolving them usually leads to deeper understanding."
        ),
    },
    "topology_malformed": {
        "title": "The Shape Needs Some Adjustment",
        "message": (
            "The topological structure has some gaps or inconsistencies. "
            "Think of it like a puzzle piece that doesn't quite fit."
        ),
        "encouragement": (
            "Topology issues are usually about boundaries and connections. "
            "Once we see the shape clearly, the fix often becomes obvious."
        ),
    },

    # Derivation and semantic
    "orphaned_implementation": {
        "title": "This Code Is Floating Free",
        "message": (
            "This implementation doesn't seem to connect back to any principle. "
            "It's working, but we can't trace why it should work."
        ),
        "encouragement": (
            "Orphaned code isn't necessarily wrong — it might just need "
            "a clearer connection to the spec. Let me suggest some links."
        ),
    },
    "semantic_inconsistency": {
        "title": "The Story Has Some Contradictions",
        "message": (
            "Different parts of the specification are saying different things "
            "about the same concept. Let's find where they diverge."
        ),
        "encouragement": (
            "Semantic conflicts often emerge as systems grow. "
            "Resolving them is an opportunity to clarify our thinking."
        ),
    },

    # Trace and behavioral
    "trace_violation": {
        "title": "Behavior Didn't Match Expectations",
        "message": (
            "The agent's actual behavior diverged from what the spec predicted. "
            "Here's what we observed versus what we expected."
        ),
        "encouragement": (
            "Behavioral mismatches are valuable data. They either reveal "
            "bugs in the code or gaps in the spec — both worth knowing."
        ),
    },

    # HoTT
    "path_construction_failed": {
        "title": "Couldn't Find a Path Between These",
        "message": (
            "I tried to show these two things are equivalent, "
            "but couldn't construct a path connecting them."
        ),
        "encouragement": (
            "Sometimes things that look similar are genuinely different. "
            "Or we might need a more creative path. Let's explore."
        ),
    },

    # System
    "system_error": {
        "title": "Something Unexpected Happened",
        "message": (
            "The verification system encountered an issue it wasn't prepared for. "
            "This is on us, not your specification."
        ),
        "encouragement": (
            "System errors help us improve. If you can share what you were doing, "
            "we can make the system more resilient."
        ),
    },
}


# =============================================================================
# Educational Content
# =============================================================================

EDUCATIONAL_CONTENT: dict[str, str] = {
    "composition_associativity": """
**Why Associativity Matters**

In category theory, composition must be associative: (f ∘ g) ∘ h = f ∘ (g ∘ h).
This means we can write f ∘ g ∘ h without parentheses — the grouping doesn't matter.

When associativity fails, it usually means:
- **Side effects**: One morphism changes state that another reads
- **Resource contention**: Different groupings use resources differently  
- **Timing dependencies**: Order of execution matters beyond composition

**Common fixes**:
1. Make morphisms pure (no side effects)
2. Explicitly manage shared state through the type system
3. Use monads to sequence effects properly
""",

    "identity_law": """
**Why Identity Laws Matter**

The identity morphism id should satisfy: f ∘ id = f and id ∘ f = f.
It's the "do nothing" operation that leaves everything unchanged.

When identity laws fail, it usually means:
- **Hidden transformations**: The "identity" is secretly doing something
- **Type coercion**: Implicit conversions during composition
- **Metadata pollution**: Extra data being added or removed

**Common fixes**:
1. Ensure identity truly returns its input unchanged
2. Check for implicit type conversions
3. Verify no logging, metrics, or side effects in identity
""",

    "sheaf_gluing": """
**Why Sheaf Gluing Matters**

Sheaves ensure local perspectives cohere into global meaning.
If you have consistent local data on overlapping regions,
there should be exactly one way to glue them into global data.

When gluing fails, it usually means:
- **Inconsistent overlaps**: Local sections disagree where they meet
- **Missing constraints**: Not enough information to determine global section
- **Ambiguous gluing**: Multiple valid global sections exist

**Common fixes**:
1. Add constraints to ensure overlap agreement
2. Refine the cover to reduce ambiguity
3. Check that restriction maps are well-defined
""",

    "functor_preservation": """
**Why Functor Laws Matter**

Functors are structure-preserving maps between categories.
They must satisfy: F(id) = id and F(g ∘ f) = F(g) ∘ F(f).

When functor laws fail, it usually means:
- **Structure loss**: The functor flattens or reorganizes data
- **Composition mismatch**: F doesn't distribute over composition
- **Identity drift**: F(id) does something other than identity

**Common fixes**:
1. Ensure F maps identity to identity explicitly
2. Verify F distributes over composition step by step
3. Check that F preserves the categorical structure, not just values
""",
}


# =============================================================================
# Verification Error
# =============================================================================

@dataclass(frozen=True)
class VerificationError:
    """
    Sympathetic error with learning opportunities.
    
    Errors are not failures — they're moments of discovery.
    """

    category: ErrorCategory
    error_type: str
    severity: Severity
    context: dict[str, Any] = field(default_factory=dict)
    counter_example: Any | None = None

    @property
    def title(self) -> str:
        """Get sympathetic title for this error."""
        messages = SYMPATHETIC_MESSAGES.get(self.error_type, {})
        return messages.get("title", f"Verification Issue: {self.error_type}")

    @property
    def message(self) -> str:
        """Get sympathetic message for this error."""
        messages = SYMPATHETIC_MESSAGES.get(self.error_type, {})
        return messages.get(
            "message",
            "Something didn't work as expected. Let me help you understand what happened."
        )

    @property
    def encouragement(self) -> str:
        """Get encouraging follow-up message."""
        messages = SYMPATHETIC_MESSAGES.get(self.error_type, {})
        return messages.get(
            "encouragement",
            "Every issue we find makes the system stronger."
        )

    @property
    def educational_content(self) -> str | None:
        """Get educational content for this error type."""
        return EDUCATIONAL_CONTENT.get(self.error_type)

    def format_for_display(self, verbose: bool = False) -> str:
        """Format error for human-readable display."""
        lines = [
            f"## {self.title}",
            "",
            self.message,
            "",
        ]

        if self.counter_example:
            lines.extend([
                "**What I observed:**",
                f"- Input: `{self.counter_example.test_input}`" if hasattr(self.counter_example, 'test_input') else "",
                f"- Expected: `{self.counter_example.expected_result}`" if hasattr(self.counter_example, 'expected_result') else "",
                f"- Actual: `{self.counter_example.actual_result}`" if hasattr(self.counter_example, 'actual_result') else "",
                "",
            ])

        lines.extend([
            f"*{self.encouragement}*",
            "",
        ])

        if verbose and self.educational_content:
            lines.extend([
                "---",
                self.educational_content,
            ])

        return "\n".join(filter(None, lines))


# =============================================================================
# Success Celebrations
# =============================================================================

SUCCESS_CELEBRATIONS: dict[str, str] = {
    "composition_verified": "✨ Composition laws hold beautifully. Your agents compose like music.",
    "identity_verified": "🌿 Identity laws verified. The foundation is solid.",
    "functor_verified": "🌊 Functor laws hold. Structure flows through transformation.",
    "sheaf_verified": "🍃 Sheaf conditions satisfied. Local and global cohere.",
    "trace_verified": "🌸 Behavior matches specification. The system does what it says.",
    "semantic_consistent": "🌻 Semantic consistency verified. The story is coherent.",
    "full_verification": "🌳 Full verification complete. The garden is healthy.",
}


def celebrate_success(verification_type: str) -> str:
    """Get a celebration message for successful verification."""
    return SUCCESS_CELEBRATIONS.get(
        verification_type,
        "✨ Verification successful. Well done."
    )


# =============================================================================
# Progressive Disclosure
# =============================================================================

@dataclass
class ProgressiveResult:
    """
    Result with progressive disclosure levels.
    
    Shows simple results by default, with detailed analysis available on demand.
    """

    summary: str
    details: str | None = None
    technical: str | None = None
    educational: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)

    def at_level(self, level: int) -> str:
        """Get result at specified disclosure level (0-3)."""
        if level == 0:
            return self.summary
        elif level == 1:
            return f"{self.summary}\n\n{self.details or ''}"
        elif level == 2:
            parts = [self.summary, self.details, self.technical]
            return "\n\n".join(filter(None, parts))
        else:
            parts = [self.summary, self.details, self.technical, self.educational]
            return "\n\n".join(filter(None, parts))


def create_progressive_result(
    success: bool,
    verification_type: str,
    details: dict[str, Any] | None = None,
    error: VerificationError | None = None,
) -> ProgressiveResult:
    """Create a progressive result from verification outcome."""

    if success:
        return ProgressiveResult(
            summary=celebrate_success(verification_type),
            details=f"Verified {details.get('test_count', 'multiple')} test cases." if details else None,
            technical=str(details) if details else None,
            educational=EDUCATIONAL_CONTENT.get(verification_type),
        )
    else:
        return ProgressiveResult(
            summary=error.title if error else "Verification issue detected",
            details=error.message if error else None,
            technical=error.format_for_display(verbose=False) if error else None,
            educational=error.educational_content if error else None,
            raw_data={"error": error, "details": details},
        )
