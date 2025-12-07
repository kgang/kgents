"""
Contradict Agent (≢)

Contradict: (Output, Output) → Tension | None
Contradict(a, b) = Tension(thesis=a, antithesis=b) | None

The contradiction-recognizer. Examines two outputs and surfaces if they are in tension.

Why irreducible: The recognition that "something's off" precedes logic. You must
                 *see* the contradiction before you can formalize it. This seeing
                 cannot be fully algorithmized—it requires judgment about what
                 counts as contradiction.

What it grounds: H-gents dialectic. Quality assurance. The ability to catch inconsistency.

Modes:
    - Logical: A and ¬A
    - Pragmatic: A recommends X, B recommends ¬X
    - Axiological: This serves value V, that serves value ¬V
    - Temporal: Past-self said X, present-self says ¬X
"""

from dataclasses import dataclass
from typing import Any
from .types import Agent, Tension, TensionMode


@dataclass
class ContradictInput:
    """Input to the Contradict agent"""
    thesis: Any
    antithesis: Any
    mode: TensionMode | None = None  # None means detect mode automatically


class Contradict(Agent[ContradictInput, Tension | None]):
    """
    The contradiction-recognizer.

    Type signature: Contradict: (Output, Output) → Tension | None

    Examines two outputs and surfaces if they are in tension.
    Returns None if no contradiction detected.
    """

    @property
    def name(self) -> str:
        return "Contradict"

    @property
    def genus(self) -> str:
        return "bootstrap"

    @property
    def purpose(self) -> str:
        return "Recognizes tension between outputs; surfaces contradictions"

    async def invoke(self, input: ContradictInput) -> Tension | None:
        """
        Detect contradiction between thesis and antithesis.

        Default implementation uses structural comparison.
        Override with LLM-backed analysis for semantic contradictions.
        """
        thesis, antithesis = input.thesis, input.antithesis

        # Same thing cannot contradict itself
        if thesis == antithesis:
            return None

        # Try each mode or use specified mode
        if input.mode:
            return await self._check_mode(input.mode, thesis, antithesis)

        # Auto-detect: try modes in order
        for mode in TensionMode:
            tension = await self._check_mode(mode, thesis, antithesis)
            if tension:
                return tension

        return None

    async def _check_mode(
        self,
        mode: TensionMode,
        thesis: Any,
        antithesis: Any
    ) -> Tension | None:
        """Check for contradiction in a specific mode"""

        match mode:
            case TensionMode.LOGICAL:
                return await self._check_logical(thesis, antithesis)
            case TensionMode.PRAGMATIC:
                return await self._check_pragmatic(thesis, antithesis)
            case TensionMode.AXIOLOGICAL:
                return await self._check_axiological(thesis, antithesis)
            case TensionMode.TEMPORAL:
                return await self._check_temporal(thesis, antithesis)

    async def _check_logical(self, thesis: Any, antithesis: Any) -> Tension | None:
        """Check for logical contradiction: A and ¬A"""

        # Boolean negation
        if isinstance(thesis, bool) and isinstance(antithesis, bool):
            if thesis != antithesis:
                return Tension(
                    mode=TensionMode.LOGICAL,
                    thesis=thesis,
                    antithesis=antithesis,
                    description=f"Logical contradiction: {thesis} vs {antithesis}"
                )

        # String negation patterns
        if isinstance(thesis, str) and isinstance(antithesis, str):
            negation_pairs = [
                ("yes", "no"), ("true", "false"), ("accept", "reject"),
                ("should", "should not"), ("is", "is not"), ("can", "cannot"),
            ]
            t_lower, a_lower = thesis.lower(), antithesis.lower()
            for pos, neg in negation_pairs:
                if (pos in t_lower and neg in a_lower) or (neg in t_lower and pos in a_lower):
                    return Tension(
                        mode=TensionMode.LOGICAL,
                        thesis=thesis,
                        antithesis=antithesis,
                        description=f"Logical contradiction detected"
                    )

        return None

    async def _check_pragmatic(self, thesis: Any, antithesis: Any) -> Tension | None:
        """Check for pragmatic contradiction: A recommends X, B recommends ¬X"""

        # Check if both are recommendations that conflict
        if hasattr(thesis, 'recommendation') and hasattr(antithesis, 'recommendation'):
            if thesis.recommendation != antithesis.recommendation:
                return Tension(
                    mode=TensionMode.PRAGMATIC,
                    thesis=thesis,
                    antithesis=antithesis,
                    description="Conflicting recommendations"
                )

        return None

    async def _check_axiological(self, thesis: Any, antithesis: Any) -> Tension | None:
        """Check for value contradiction: serves V vs serves ¬V"""

        # Check if both reference values
        thesis_values = getattr(thesis, 'values', None) or []
        antithesis_values = getattr(antithesis, 'values', None) or []

        if thesis_values and antithesis_values:
            # Look for opposing values
            for tv in thesis_values:
                for av in antithesis_values:
                    if self._are_opposing_values(tv, av):
                        return Tension(
                            mode=TensionMode.AXIOLOGICAL,
                            thesis=thesis,
                            antithesis=antithesis,
                            description=f"Value tension: {tv} vs {av}"
                        )

        return None

    async def _check_temporal(self, thesis: Any, antithesis: Any) -> Tension | None:
        """Check for temporal contradiction: past said X, now says ¬X"""

        # Check timestamps if available
        thesis_time = getattr(thesis, 'timestamp', None)
        antithesis_time = getattr(antithesis, 'timestamp', None)

        if thesis_time and antithesis_time and thesis_time != antithesis_time:
            # Different times + different content = potential temporal tension
            thesis_content = getattr(thesis, 'content', thesis)
            antithesis_content = getattr(antithesis, 'content', antithesis)

            if thesis_content != antithesis_content:
                return Tension(
                    mode=TensionMode.TEMPORAL,
                    thesis=thesis,
                    antithesis=antithesis,
                    description="Position changed over time"
                )

        return None

    def _are_opposing_values(self, v1: str, v2: str) -> bool:
        """Check if two values are in opposition"""
        opposing_pairs = [
            ("freedom", "control"),
            ("privacy", "surveillance"),
            ("simplicity", "complexity"),
            ("openness", "secrecy"),
            ("autonomy", "dependence"),
        ]
        v1_lower, v2_lower = v1.lower(), v2.lower()
        for a, b in opposing_pairs:
            if (a in v1_lower and b in v2_lower) or (b in v1_lower and a in v2_lower):
                return True
        return False


# Singleton instance
contradict_agent = Contradict()


async def contradict(thesis: Any, antithesis: Any, mode: TensionMode | None = None) -> Tension | None:
    """Convenience function to check for contradiction"""
    return await contradict_agent.invoke(ContradictInput(
        thesis=thesis,
        antithesis=antithesis,
        mode=mode
    ))
