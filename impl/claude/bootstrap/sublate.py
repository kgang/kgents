"""
Sublate Agent - Hegelian synthesis of tensions.

Sublate: Tension → Synthesis | HoldTension
Sublate(tension) = {preserve, negate, elevate} | "too soon"

The Hegelian move. Takes a contradiction and attempts synthesis—or
recognizes that the tension should be held.

The creative leap from thesis+antithesis to synthesis is not mechanical.
What gets preserved, what gets negated, what new level emerges—this
requires judgment. And the wisdom to *not* synthesize prematurely
is equally irreducible.

See spec/bootstrap.md lines 166-178, spec/h-gents/hegel.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, Sequence

from agents.poly.types import (
    Agent,
    HoldTension,
    SublateInput,
    SublateResult,
    Synthesis,
    Tension,
    TensionMode,
)

# --- Resolution Strategy Protocol ---


class ResolutionStrategy(Protocol):
    """
    Protocol for synthesis strategies.

    Different strategies handle different tension modes.
    """

    @property
    def name(self) -> str:
        """Name of this strategy."""
        ...

    async def attempt(self, tension: Tension) -> Optional[Synthesis]:
        """
        Attempt to synthesize the tension.

        Returns Synthesis if successful, None if cannot synthesize.
        """
        ...


# --- Built-in Strategies ---


@dataclass
class PreserveBothStrategy:
    """
    Strategy that preserves elements from both sides.

    Best for tensions where both thesis and antithesis have value.
    """

    @property
    def name(self) -> str:
        return "preserve_both"

    async def attempt(self, tension: Tension) -> Optional[Synthesis]:
        """
        Try to preserve elements from both sides.

        Applicable when severity is low to moderate.
        """
        if tension.severity > 0.7:
            # Too severe for simple preservation
            return None

        # For dict-like tensions, merge
        if isinstance(tension.thesis, dict) and isinstance(tension.antithesis, dict):
            merged = {**tension.thesis, **tension.antithesis}
            return Synthesis(
                resolution_type="preserve",
                result=merged,
                explanation="Merged both dicts, antithesis values take precedence",
                preserved_from_thesis=tuple(tension.thesis.keys()),
                preserved_from_antithesis=tuple(tension.antithesis.keys()),
            )

        return None


@dataclass
class ElevateStrategy:
    """
    Strategy that elevates to a higher abstraction.

    Best for tensions that represent different levels of abstraction.
    """

    @property
    def name(self) -> str:
        return "elevate"

    async def attempt(self, tension: Tension) -> Optional[Synthesis]:
        """
        Try to find a higher-level abstraction.

        Looks for common patterns in thesis and antithesis.
        """
        # String tensions: find common prefix/suffix
        if isinstance(tension.thesis, str) and isinstance(tension.antithesis, str):
            thesis = tension.thesis
            antithesis = tension.antithesis

            # Find common prefix
            common_prefix = ""
            for t, a in zip(thesis, antithesis):
                if t == a:
                    common_prefix += t
                else:
                    break

            if len(common_prefix) > 3:
                return Synthesis(
                    resolution_type="elevate",
                    result=f"{common_prefix}*",
                    explanation="Elevated to common prefix pattern",
                    preserved_from_thesis=(thesis,),
                    preserved_from_antithesis=(antithesis,),
                )

        return None


@dataclass
class NegateStrategy:
    """
    Strategy that negates one side in favor of the other.

    Used when one side is clearly superior.
    """

    @property
    def name(self) -> str:
        return "negate"

    async def attempt(self, tension: Tension) -> Optional[Synthesis]:
        """
        Negate one side when severity is high.

        Only applies to high-severity logical tensions.
        """
        if tension.mode != TensionMode.LOGICAL:
            return None

        if tension.severity < 0.9:
            return None

        # For booleans, the true one "wins"
        if isinstance(tension.thesis, bool) and isinstance(tension.antithesis, bool):
            winner = tension.thesis if tension.thesis else tension.antithesis
            loser = "antithesis" if tension.thesis else "thesis"
            return Synthesis(
                resolution_type="negate",
                result=winner,
                explanation=f"Negated {loser}, boolean resolution",
                preserved_from_thesis=() if loser == "thesis" else (str(tension.thesis),),
                preserved_from_antithesis=()
                if loser == "antithesis"
                else (str(tension.antithesis),),
            )

        return None


# --- Hold Conditions ---


def should_hold(tension: Tension) -> tuple[bool, str, tuple[str, ...]]:
    """
    Determine if a tension should be held rather than resolved.

    Returns:
        (should_hold, reason, revisit_conditions)
    """
    # High-severity aesthetic tensions should be held
    if tension.mode == TensionMode.AESTHETIC and tension.severity > 0.5:
        return (
            True,
            "Aesthetic tensions require deeper reflection",
            (
                "When more context is available",
                "After user preference clarification",
            ),
        )

    # Temporal tensions often resolve themselves
    if tension.mode == TensionMode.TEMPORAL:
        return (
            True,
            "Temporal tensions may resolve with time",
            (
                "After the temporal context changes",
                "When the past context is no longer relevant",
            ),
        )

    # Very severe tensions need careful handling
    if tension.severity > 0.95:
        return (
            True,
            "Tension too severe for automatic synthesis",
            (
                "After human review",
                "When more information is available",
            ),
        )

    return (False, "", ())


# --- Sublate Agent ---


class Sublate(Agent[SublateInput, SublateResult]):
    """
    The Hegelian synthesis agent.

    Takes tensions and attempts to synthesize them into a higher
    resolution, or consciously holds them for later resolution.

    Usage:
        sublate = Sublate()
        result = await sublate.invoke(SublateInput(tensions=(tension,)))

        if isinstance(result, Synthesis):
            print(f"Resolved: {result.explanation}")
        else:
            print(f"Holding: {result.why_held}")

    Pattern: Sublate, don't overwrite - merge defaults, preserve both sides.
    """

    def __init__(
        self,
        strategies: Optional[Sequence[ResolutionStrategy]] = None,
    ):
        """
        Initialize with resolution strategies.

        Args:
            strategies: Ordered list of strategies to try
        """
        self._strategies: list[ResolutionStrategy] = list(
            strategies if strategies is not None else default_strategies()
        )

    @property
    def name(self) -> str:
        return "Sublate"

    async def invoke(self, input: SublateInput) -> SublateResult:
        """
        Attempt to synthesize the tensions.

        Tries each tension with each strategy until one succeeds,
        or holds if none can synthesize.
        """
        if not input.tensions:
            # No tensions to resolve - return empty synthesis
            return Synthesis(
                resolution_type="preserve",
                result=None,
                explanation="No tensions to synthesize",
            )

        # Process first tension (primary focus)
        tension = input.tensions[0]

        # Check if we should hold
        hold, reason, conditions = should_hold(tension)
        if hold:
            return HoldTension(
                tension=tension,
                why_held=reason,
                revisit_conditions=conditions,
            )

        # Try strategies in order
        for strategy in self._strategies:
            synthesis = await strategy.attempt(tension)
            if synthesis is not None:
                return synthesis

        # No strategy worked - hold the tension
        return HoldTension(
            tension=tension,
            why_held="No resolution strategy succeeded",
            revisit_conditions=(
                "When new synthesis strategies are available",
                "After context clarification",
            ),
        )


def default_strategies() -> list[ResolutionStrategy]:
    """Return the default set of resolution strategies."""
    return [
        PreserveBothStrategy(),
        ElevateStrategy(),
        NegateStrategy(),
    ]


# --- Convenience Functions ---


async def sublate(tensions: tuple[Tension, ...]) -> SublateResult:
    """
    Attempt to synthesize tensions.

    Convenience function for Sublate().invoke(...).
    """
    return await Sublate().invoke(SublateInput(tensions=tensions))


async def resolve_or_hold(tension: Tension) -> SublateResult:
    """
    Resolve a single tension or hold it.

    Convenience function for single-tension sublation.
    """
    return await sublate((tension,))
