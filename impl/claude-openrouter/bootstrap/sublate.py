"""
Sublate (↑) - The Hegelian move.

Type: Tension → Synthesis | HoldTension
Returns: {preserve, negate, elevate} | "too soon"

Takes a contradiction and attempts synthesis—or recognizes
that the tension should be held.

Why irreducible: The creative leap from thesis+antithesis to synthesis
                 is not mechanical. What gets preserved, what gets negated,
                 what new level emerges—this requires judgment.
What it grounds: H-hegel. System evolution. Growth through contradiction.

The Three Moments of Aufhebung:
1. PRESERVE (aufbewahren) - Keep what's valuable from both sides
2. NEGATE (negieren) - Eliminate what's contradictory
3. ELEVATE (erheben) - Transcend to a higher synthesis

The Wisdom to Hold:
Sometimes the tension should NOT be resolved. Premature synthesis
is worse than held tension. The "too soon" response is valid.
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional, Union

from .types import (
    Agent,
    HoldTension,
    ResolutionType,
    Synthesis,
    Tension,
    TensionMode,
)


SublateResult = Union[Synthesis, HoldTension]


class Sublate(Agent[Tension, SublateResult]):
    """
    The synthesizer: resolves tensions or consciously holds them.

    Usage:
        sublate = Sublate()

        # Given a tension from Contradict
        result = await sublate.invoke(tension)

        if isinstance(result, Synthesis):
            # Tension was resolved
            match result.resolution_type:
                case ResolutionType.PRESERVE:
                    # Both sides kept in different contexts
                case ResolutionType.NEGATE:
                    # One side was wrong
                case ResolutionType.ELEVATE:
                    # New synthesis transcends both
        else:
            # HoldTension: not ready to resolve
            print(f"Holding: {result.reason}")
            print(f"Revisit when: {result.revisit_conditions}")
    """

    def __init__(
        self,
        resolver: Optional[Callable[[Tension], SublateResult]] = None,
    ):
        """
        Initialize with optional custom resolution logic.

        The default resolver handles common patterns. For domain-specific
        synthesis, provide a custom resolver.
        """
        self._resolver = resolver or self._default_resolve

    @property
    def name(self) -> str:
        return "Sublate"

    async def invoke(self, tension: Tension) -> SublateResult:
        """
        Attempt to resolve a tension.

        May return:
        - Synthesis: The tension was resolved
        - HoldTension: The tension should be held for now
        """
        return self._resolver(tension)

    def _default_resolve(self, tension: Tension) -> SublateResult:
        """Default resolution strategies by tension mode."""

        # High-severity tensions need careful consideration
        if tension.severity >= 0.9:
            return self._attempt_resolution(tension)

        # Medium severity: try to resolve
        if tension.severity >= 0.5:
            return self._attempt_resolution(tension)

        # Low severity: often can preserve both
        return Synthesis(
            resolution_type=ResolutionType.PRESERVE,
            result={
                "context_a": tension.thesis,
                "context_b": tension.antithesis,
            },
            explanation="Low-severity tension: both valid in different contexts",
            preserved=[tension.thesis, tension.antithesis],
            negated=[],
        )

    def _attempt_resolution(self, tension: Tension) -> SublateResult:
        """Attempt to resolve based on tension mode."""

        if tension.mode == TensionMode.LOGICAL:
            # Logical contradictions usually require negation
            return self._resolve_logical(tension)

        elif tension.mode == TensionMode.PRAGMATIC:
            # Pragmatic conflicts might be contextual
            return self._resolve_pragmatic(tension)

        elif tension.mode == TensionMode.AXIOLOGICAL:
            # Value conflicts often need to be held
            return self._hold_for_reflection(tension)

        elif tension.mode == TensionMode.TEMPORAL:
            # Temporal conflicts: usually the present wins
            return self._resolve_temporal(tension)

        # Unknown mode: hold for human judgment
        return self._hold_for_reflection(tension)

    def _resolve_logical(self, tension: Tension) -> SublateResult:
        """Resolve logical contradiction: one side must be negated."""
        # Without additional context, we can't know which side is correct
        # Return a synthesis that acknowledges the contradiction
        return Synthesis(
            resolution_type=ResolutionType.NEGATE,
            result=None,  # Requires external judgment
            explanation="Logical contradiction requires external judgment to resolve",
            preserved=[],
            negated=[],  # Unknown which to negate
        )

    def _resolve_pragmatic(self, tension: Tension) -> SublateResult:
        """Resolve pragmatic conflict: find contextual separation."""
        return Synthesis(
            resolution_type=ResolutionType.PRESERVE,
            result={
                "when_a": f"Use {tension.thesis} in context A",
                "when_b": f"Use {tension.antithesis} in context B",
            },
            explanation="Pragmatic conflict resolved by context separation",
            preserved=[tension.thesis, tension.antithesis],
            negated=[],
        )

    def _resolve_temporal(self, tension: Tension) -> SublateResult:
        """Resolve temporal conflict: present usually supersedes past."""
        return Synthesis(
            resolution_type=ResolutionType.NEGATE,
            result=tension.antithesis,  # Present (antithesis by convention)
            explanation="Temporal conflict: present supersedes past",
            preserved=[tension.antithesis],
            negated=[tension.thesis],
        )

    def _hold_for_reflection(self, tension: Tension) -> HoldTension:
        """When resolution would be premature, hold the tension."""
        return HoldTension(
            tension=tension,
            reason="This tension requires reflection before resolution",
            revisit_conditions=[
                "More context is available",
                "Stakes become clearer",
                "Human judgment is provided",
            ],
        )


# Specialized sublaters for common scenarios

class MergeConfigSublate(Agent[Tension, SublateResult]):
    """Resolve configuration conflicts with explicit merge rules."""

    def __init__(self, prefer: str = "newer"):
        """
        prefer: "newer" | "older" | "explicit" (require manual resolution)
        """
        self._prefer = prefer

    @property
    def name(self) -> str:
        return "MergeConfigSublate"

    async def invoke(self, tension: Tension) -> SublateResult:
        if self._prefer == "newer":
            return Synthesis(
                resolution_type=ResolutionType.NEGATE,
                result=tension.antithesis,
                explanation="Merge conflict: newer config wins",
                preserved=[tension.antithesis],
                negated=[tension.thesis],
            )
        elif self._prefer == "older":
            return Synthesis(
                resolution_type=ResolutionType.NEGATE,
                result=tension.thesis,
                explanation="Merge conflict: older config preserved",
                preserved=[tension.thesis],
                negated=[tension.antithesis],
            )
        else:
            return HoldTension(
                tension=tension,
                reason="Explicit merge resolution required",
                revisit_conditions=["Manual resolution provided"],
            )
