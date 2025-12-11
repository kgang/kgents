"""
Contradict Agent - Tension detection between two outputs.

Contradict: (A, B) → Tension | None
Contradict(a, b) = Tension(thesis=a, antithesis=b) | None

The contradiction-recognizer. Examines two outputs and surfaces if
they are in tension. The recognition that "something's off" precedes
logic. You must *see* the contradiction before you can formalize it.

Modes:
- Logical: A and ¬A
- Pragmatic: A recommends X, B recommends ¬X
- Axiological: This serves value V, that serves value ¬V
- Temporal: Past-self said X, present-self says ¬X
- Aesthetic: Style/taste conflicts

See spec/bootstrap.md lines 145-163.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Optional, Protocol, Sequence

from .types import (
    Agent,
    ContradictInput,
    ContradictResult,
    Tension,
    TensionMode,
)

# --- Tension Detector Protocol ---


class TensionDetector(Protocol):
    """
    Protocol for tension detection strategies.

    Each detector focuses on a specific type of tension
    (logical, pragmatic, etc.). Multiple detectors can be
    composed for comprehensive contradiction analysis.
    """

    @property
    def name(self) -> str:
        """Name of this detector."""
        ...

    async def detect(self, a: Any, b: Any) -> Optional[Tension]:
        """
        Detect tension between two values.

        Returns Tension if contradiction found, None otherwise.
        """
        ...


# --- Built-in Detectors ---


@dataclass
class LogicalDetector:
    """Detects direct logical contradictions (A and ¬A)."""

    @property
    def name(self) -> str:
        return "logical"

    async def detect(self, a: Any, b: Any) -> Optional[Tension]:
        """
        Detect if a and b are logical opposites.

        Simple heuristics:
        - Boolean opposites
        - Negation patterns in strings
        """
        # Boolean opposites
        if isinstance(a, bool) and isinstance(b, bool):
            if a != b:
                return Tension(
                    thesis=a,
                    antithesis=b,
                    mode=TensionMode.LOGICAL,
                    severity=1.0,
                    description=f"Boolean contradiction: {a} vs {b}",
                )

        # String negation patterns
        if isinstance(a, str) and isinstance(b, str):
            a_lower = a.lower().strip()
            b_lower = b.lower().strip()

            # Check for "not X" vs "X" patterns
            if a_lower.startswith("not ") and a_lower[4:] == b_lower:
                return Tension(
                    thesis=a,
                    antithesis=b,
                    mode=TensionMode.LOGICAL,
                    severity=0.9,
                    description=f"Negation pattern: '{a}' vs '{b}'",
                )
            if b_lower.startswith("not ") and b_lower[4:] == a_lower:
                return Tension(
                    thesis=a,
                    antithesis=b,
                    mode=TensionMode.LOGICAL,
                    severity=0.9,
                    description=f"Negation pattern: '{a}' vs '{b}'",
                )

        return None


@dataclass
class EqualityDetector:
    """Detects when values should be equal but aren't."""

    @property
    def name(self) -> str:
        return "equality"

    async def detect(self, a: Any, b: Any) -> Optional[Tension]:
        """
        Detect if a and b differ when they share structure.

        For dictionaries, checks overlapping keys.
        For sequences, checks overlapping positions.
        """
        # Dict key overlap with different values
        if isinstance(a, dict) and isinstance(b, dict):
            common_keys = set(a.keys()) & set(b.keys())
            conflicts = [k for k in common_keys if a[k] != b[k]]
            if conflicts:
                return Tension(
                    thesis=a,
                    antithesis=b,
                    mode=TensionMode.LOGICAL,
                    severity=0.7,
                    description=f"Dict conflict on keys: {conflicts}",
                )

        return None


@dataclass
class PragmaticDetector:
    """Detects pragmatic contradictions (conflicting recommendations)."""

    @property
    def name(self) -> str:
        return "pragmatic"

    async def detect(self, a: Any, b: Any) -> Optional[Tension]:
        """
        Detect if a and b recommend conflicting actions.

        Looks for recommendation patterns in strings:
        - "should X" vs "should not X"
        - "do X" vs "don't X"
        """
        if isinstance(a, str) and isinstance(b, str):
            a_lower = a.lower()
            b_lower = b.lower()

            # Check "should" patterns
            if "should " in a_lower and "should not " in b_lower:
                return Tension(
                    thesis=a,
                    antithesis=b,
                    mode=TensionMode.PRAGMATIC,
                    severity=0.8,
                    description="Conflicting 'should' recommendations",
                )
            if "should not " in a_lower and "should " in b_lower:
                return Tension(
                    thesis=a,
                    antithesis=b,
                    mode=TensionMode.PRAGMATIC,
                    severity=0.8,
                    description="Conflicting 'should' recommendations",
                )

        return None


# --- Detector Configuration ---


@dataclass(frozen=True)
class DetectorConfig:
    """Configuration for individual detector execution."""

    timeout_seconds: float = 5.0
    enabled: bool = True


@dataclass(frozen=True)
class CircuitBreaker:
    """
    Circuit breaker state for detector resilience.

    Tracks failures and can disable detector temporarily.
    """

    failure_count: int = 0
    failure_threshold: int = 3
    is_open: bool = False

    def record_failure(self) -> "CircuitBreaker":
        """Record a failure and potentially open the circuit."""
        new_count = self.failure_count + 1
        return CircuitBreaker(
            failure_count=new_count,
            failure_threshold=self.failure_threshold,
            is_open=new_count >= self.failure_threshold,
        )

    def reset(self) -> "CircuitBreaker":
        """Reset the circuit breaker after success."""
        return CircuitBreaker(
            failure_count=0,
            failure_threshold=self.failure_threshold,
            is_open=False,
        )


@dataclass
class TensionEvidence:
    """
    Evidence tracking for bidirectional learning.

    Records which detectors found what tensions for analysis.
    """

    detector_name: str
    tension: Tension
    execution_time_ms: float = 0.0


# --- Contradict Agent ---


class Contradict(Agent[ContradictInput, ContradictResult]):
    """
    The contradiction-recognizer agent.

    Examines two outputs and surfaces tensions between them.
    Uses multiple detection strategies (logical, pragmatic, etc.)
    with per-detector timeout and circuit breaker for robustness.

    Usage:
        contradict = Contradict()
        result = await contradict.invoke(ContradictInput(a=x, b=y))
        if not result.no_tension:
            for tension in result.tensions:
                print(f"Found: {tension.description}")
    """

    def __init__(
        self,
        detectors: Optional[Sequence[TensionDetector]] = None,
        detector_configs: Optional[dict[str, DetectorConfig]] = None,
    ):
        """
        Initialize with detectors and optional configs.

        Args:
            detectors: List of tension detectors to use
            detector_configs: Per-detector configuration
        """
        self._detectors: list[TensionDetector] = list(
            detectors if detectors is not None else default_detectors()
        )
        self._configs = detector_configs or {}
        self._circuit_breakers: dict[str, CircuitBreaker] = {}

    @property
    def name(self) -> str:
        return "Contradict"

    async def invoke(self, input: ContradictInput) -> ContradictResult:
        """
        Detect tensions between input.a and input.b.

        Runs all enabled detectors (respecting circuit breakers)
        and aggregates found tensions.
        """
        if input.a == input.b:
            # Identical inputs cannot be in tension
            return ContradictResult(tensions=(), no_tension=True)

        tensions: list[Tension] = []
        evidence: list[TensionEvidence] = []

        for detector in self._detectors:
            # Check circuit breaker
            breaker = self._circuit_breakers.get(detector.name, CircuitBreaker())
            if breaker.is_open:
                continue

            # Check config
            config = self._configs.get(detector.name, DetectorConfig())
            if not config.enabled:
                continue

            # Run detector with timeout
            try:
                tension = await asyncio.wait_for(
                    detector.detect(input.a, input.b),
                    timeout=config.timeout_seconds,
                )

                # Reset circuit breaker on success
                self._circuit_breakers[detector.name] = breaker.reset()

                if tension is not None:
                    tensions.append(tension)
                    evidence.append(
                        TensionEvidence(
                            detector_name=detector.name,
                            tension=tension,
                        )
                    )

            except asyncio.TimeoutError:
                # Record timeout as failure
                self._circuit_breakers[detector.name] = breaker.record_failure()
            except Exception:
                # Record exception as failure
                self._circuit_breakers[detector.name] = breaker.record_failure()

        return ContradictResult(
            tensions=tuple(tensions),
            no_tension=len(tensions) == 0,
        )


def default_detectors() -> list[TensionDetector]:
    """Return the default set of tension detectors."""
    return [
        LogicalDetector(),
        EqualityDetector(),
        PragmaticDetector(),
    ]


# Convenience function
async def contradict(a: Any, b: Any) -> ContradictResult:
    """
    Detect tensions between two values.

    Convenience function for Contradict().invoke(...).
    """
    return await Contradict().invoke(ContradictInput(a=a, b=b))
