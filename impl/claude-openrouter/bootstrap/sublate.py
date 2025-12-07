"""
Sublate Agent (↑)

Sublate: Tension → Synthesis | HoldTension
Sublate(tension) = {preserve, negate, elevate} | "too soon"

The Hegelian move. Takes a contradiction and attempts synthesis—or recognizes
that the tension should be held.

Why irreducible: The creative leap from thesis+antithesis to synthesis is not
                 mechanical. What gets preserved, what gets negated, what new
                 level emerges—this requires judgment. And the wisdom to *not*
                 synthesize prematurely is equally irreducible.

What it grounds: H-hegel. System evolution. The ability to grow through
                 contradiction rather than being paralyzed by it.
"""

from dataclasses import dataclass
from typing import Any
from .types import (
    Agent,
    Tension,
    TensionMode,
    Synthesis,
    HoldTension,
    SynthesisResult,
)


@dataclass
class SublateConfig:
    """Configuration for sublation behavior"""
    prefer_hold: bool = False  # If True, prefer holding tension over forcing synthesis
    min_tension_age: float = 0  # Minimum time (seconds) before allowing synthesis


class Sublate(Agent[Tension, SynthesisResult]):
    """
    The Hegelian move.

    Type signature: Sublate: Tension → Synthesis | HoldTension

    Takes a contradiction and attempts synthesis (Aufhebung):
        - preserve: what is kept from both thesis and antithesis
        - negate: what is rejected from both
        - elevate: the new understanding that transcends both

    Or, recognizes that the tension should be held:
        - "too soon": not enough information to synthesize
        - "generative": the tension itself is valuable
    """

    def __init__(self, config: SublateConfig | None = None):
        self._config = config or SublateConfig()

    @property
    def name(self) -> str:
        return "Sublate"

    @property
    def genus(self) -> str:
        return "bootstrap"

    @property
    def purpose(self) -> str:
        return "Hegelian synthesis; resolves or holds tension"

    async def invoke(self, tension: Tension) -> SynthesisResult:
        """
        Attempt to sublate the tension.

        Default implementation uses mode-specific heuristics.
        Override with LLM-backed synthesis for sophisticated resolution.
        """
        # Check if we should hold
        if self._should_hold(tension):
            return HoldTension(
                reason="Tension is generative; holding for now",
                tension=tension
            )

        # Attempt synthesis based on mode
        return await self._synthesize(tension)

    def _should_hold(self, tension: Tension) -> bool:
        """Determine if tension should be held rather than resolved"""

        if self._config.prefer_hold:
            return True

        # Some tensions are generative by nature
        generative_descriptions = [
            "creative", "exploratory", "open question",
            "both valid", "context-dependent"
        ]

        for keyword in generative_descriptions:
            if keyword in tension.description.lower():
                return True

        return False

    async def _synthesize(self, tension: Tension) -> SynthesisResult:
        """Perform synthesis based on tension mode"""

        match tension.mode:
            case TensionMode.LOGICAL:
                return await self._synthesize_logical(tension)
            case TensionMode.PRAGMATIC:
                return await self._synthesize_pragmatic(tension)
            case TensionMode.AXIOLOGICAL:
                return await self._synthesize_axiological(tension)
            case TensionMode.TEMPORAL:
                return await self._synthesize_temporal(tension)

    async def _synthesize_logical(self, tension: Tension) -> SynthesisResult:
        """
        Synthesize logical contradiction.

        Strategy: Find the context where each is true.
        """
        return Synthesis(
            preserved=(
                f"Context where thesis holds: {tension.thesis}",
                f"Context where antithesis holds: {tension.antithesis}",
            ),
            negated=(
                "The assumption that only one can be true",
            ),
            synthesis={
                "resolution": "Both are true in their respective contexts",
                "elevated_understanding": "The contradiction reveals a hidden context-dependency",
                "thesis": tension.thesis,
                "antithesis": tension.antithesis,
            }
        )

    async def _synthesize_pragmatic(self, tension: Tension) -> SynthesisResult:
        """
        Synthesize pragmatic contradiction (conflicting recommendations).

        Strategy: Find higher-order principle that reconciles.
        """
        return Synthesis(
            preserved=(
                f"Intent behind thesis: {tension.thesis}",
                f"Intent behind antithesis: {tension.antithesis}",
            ),
            negated=(
                "The specific implementations that conflict",
            ),
            synthesis={
                "resolution": "A new approach that serves both intents",
                "elevated_understanding": "The conflict reveals different stakeholder needs",
                "thesis": tension.thesis,
                "antithesis": tension.antithesis,
            }
        )

    async def _synthesize_axiological(self, tension: Tension) -> SynthesisResult:
        """
        Synthesize value contradiction.

        Strategy: Find the meta-value that encompasses both.
        """
        return Synthesis(
            preserved=(
                f"Value from thesis: {tension.thesis}",
                f"Value from antithesis: {tension.antithesis}",
            ),
            negated=(
                "The framing that puts these values in opposition",
            ),
            synthesis={
                "resolution": "A meta-value that honors both",
                "elevated_understanding": "The apparent conflict stems from incomplete framing",
                "thesis": tension.thesis,
                "antithesis": tension.antithesis,
            }
        )

    async def _synthesize_temporal(self, tension: Tension) -> SynthesisResult:
        """
        Synthesize temporal contradiction (position changed over time).

        Strategy: Understand the evolution as growth.
        """
        return Synthesis(
            preserved=(
                f"Past position: {tension.thesis}",
                f"Present position: {tension.antithesis}",
            ),
            negated=(
                "The expectation of perfect consistency over time",
            ),
            synthesis={
                "resolution": "The evolution represents growth, not inconsistency",
                "elevated_understanding": "Changed positions reflect new information or maturity",
                "thesis": tension.thesis,
                "antithesis": tension.antithesis,
            }
        )


# Singleton instance
sublate_agent = Sublate()


async def sublate(tension: Tension) -> SynthesisResult:
    """Convenience function to sublate a tension"""
    return await sublate_agent.invoke(tension)
