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


# Resolution strategies as composable morphisms
class LogicalResolver(Agent[Tension, SublateResult]):
    """Resolve logical contradictions: one side must be negated."""

    @property
    def name(self) -> str:
        return "LogicalResolver"

    async def invoke(self, tension: Tension) -> SublateResult:
        return Synthesis(
            resolution_type=ResolutionType.NEGATE,
            result=None,  # Requires external judgment
            explanation="Logical contradiction requires external judgment to resolve",
            preserved=[],
            negated=[],  # Unknown which to negate
        )


class PragmaticResolver(Agent[Tension, SublateResult]):
    """Resolve pragmatic conflicts via contextual separation."""

    @property
    def name(self) -> str:
        return "PragmaticResolver"

    async def invoke(self, tension: Tension) -> SublateResult:
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


class TemporalResolver(Agent[Tension, SublateResult]):
    """Resolve temporal conflicts: present supersedes past."""

    @property
    def name(self) -> str:
        return "TemporalResolver"

    async def invoke(self, tension: Tension) -> SublateResult:
        return Synthesis(
            resolution_type=ResolutionType.NEGATE,
            result=tension.antithesis,  # Present (antithesis by convention)
            explanation="Temporal conflict: present supersedes past",
            preserved=[tension.antithesis],
            negated=[tension.thesis],
        )


class AxiologicalResolver(Agent[Tension, SublateResult]):
    """Resolve value conflicts: usually hold for reflection."""

    @property
    def name(self) -> str:
        return "AxiologicalResolver"

    async def invoke(self, tension: Tension) -> SublateResult:
        return HoldTension(
            tension=tension,
            reason="Value conflict requires reflection before resolution",
            revisit_conditions=[
                "More context is available",
                "Stakes become clearer",
                "Human judgment is provided",
            ],
        )


class LowSeverityResolver(Agent[Tension, SublateResult]):
    """Resolve low-severity tensions by preserving both."""

    @property
    def name(self) -> str:
        return "LowSeverityResolver"

    async def invoke(self, tension: Tension) -> SublateResult:
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


class Sublate(Agent[Tension, SublateResult]):
    """
    The synthesizer: resolves tensions or consciously holds them.

    Usage:
        # Default routing by severity and mode
        sublate = Sublate()

        # Custom resolver
        sublate = Sublate(resolver=my_custom_resolver)

        # Custom strategy per mode
        sublate = Sublate(
            logical_resolver=MyLogicalResolver(),
            pragmatic_resolver=MyPragmaticResolver(),
        )

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
        resolver: Optional[Agent[Tension, SublateResult]] = None,
        logical_resolver: Optional[Agent[Tension, SublateResult]] = None,
        pragmatic_resolver: Optional[Agent[Tension, SublateResult]] = None,
        temporal_resolver: Optional[Agent[Tension, SublateResult]] = None,
        axiological_resolver: Optional[Agent[Tension, SublateResult]] = None,
        low_severity_resolver: Optional[Agent[Tension, SublateResult]] = None,
    ):
        """
        Initialize with optional custom resolution strategies.

        If resolver is provided, it overrides mode-specific resolvers.
        Otherwise, mode-specific resolvers are used (with defaults).
        """
        self._resolver = resolver
        self._logical = logical_resolver or LogicalResolver()
        self._pragmatic = pragmatic_resolver or PragmaticResolver()
        self._temporal = temporal_resolver or TemporalResolver()
        self._axiological = axiological_resolver or AxiologicalResolver()
        self._low_severity = low_severity_resolver or LowSeverityResolver()

    @property
    def name(self) -> str:
        return "Sublate"

    async def invoke(self, tension: Tension) -> SublateResult:
        """
        Attempt to resolve a tension.

        Routes to appropriate strategy based on severity and mode.
        """
        # If custom resolver provided, use it
        if self._resolver:
            return await self._resolver.invoke(tension)

        # Low severity: preserve both
        if tension.severity < 0.5:
            return await self._low_severity.invoke(tension)

        # Route by tension mode
        resolver_map = {
            TensionMode.LOGICAL: self._logical,
            TensionMode.PRAGMATIC: self._pragmatic,
            TensionMode.TEMPORAL: self._temporal,
            TensionMode.AXIOLOGICAL: self._axiological,
        }

        resolver = resolver_map.get(tension.mode, self._axiological)
        return await resolver.invoke(tension)


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
