"""
Contradict (≢) - The contradiction-recognizer.

Type: (A, B) → Tension | None
Returns: Tension(thesis=a, antithesis=b) | None

Examines two outputs and surfaces if they are in tension.

Why irreducible: The recognition that "something's off" precedes logic.
                 You must *see* the contradiction before you can formalize it.
What it grounds: H-gents dialectic. Quality assurance. Consistency checking.

Modes:
- Logical:    A and ¬A
- Pragmatic:  A recommends X, B recommends ¬X
- Axiological: This serves value V, that serves value ¬V
- Temporal:   Past-self said X, present-self says ¬X

IDIOM: Conflict is Data
> Tensions should be first-class citizens.

The Contradict/Sublate pattern generalizes to system robustness:
1. Detect tensions explicitly (don't let them surface as runtime errors)
2. Surface them to the appropriate resolver
3. Resolve or hold—premature synthesis is worse than held tension

Anti-pattern: Silent failures, swallowed exceptions, "last write wins".
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Callable, Protocol
import time

from .types import Agent, Tension, TensionMode


# Protocol for extensible tension detection
class TensionDetector(Protocol):
    """
    Protocol for custom tension detectors.

    Allows extending Contradict with domain-specific contradiction logic
    without modifying the core agent.

    Example:
        class SemanticTensionDetector:
            async def detect(self, a: Any, b: Any, mode: TensionMode) -> Optional[Tension]:
                # Use LLM to check semantic contradiction
                ...

        contradict = Contradict(detectors=[
            SemanticTensionDetector(),
            LogicalTensionDetector(),
        ])
    """

    async def detect(self, a: Any, b: Any, mode: TensionMode) -> Optional[Tension]:
        """
        Detect tension between a and b for the given mode.

        Returns Tension if contradiction detected, None otherwise.
        """
        ...


@dataclass
class ContradictInput:
    """Two things to check for contradiction."""
    a: Any
    b: Any
    mode: Optional[TensionMode] = None  # If None, check all modes


@dataclass
class ContradictResult:
    """
    Result of contradiction detection with observability metadata.
    
    This wraps Optional[Tension] with diagnostic information useful for
    debugging why contradictions were/weren't detected.
    
    Usage:
        result = await contradict.invoke(input)
        
        if result.tension:
            # Handle the conflict
            await sublate.invoke(result.tension)
        
        # Debug observability
        print(f"Checked modes: {result.checked_modes}")
        print(f"Execution time: {result.execution_time_ms}ms")
    """
    tension: Optional[Tension]
    checked_modes: list[TensionMode] = field(default_factory=list)
    execution_time_ms: float = 0.0
    
    def __bool__(self) -> bool:
        """Allow 'if result:' to check for tension presence."""
        return self.tension is not None


class Contradict(Agent[ContradictInput, ContradictResult]):
    """
    The contradiction-recognizer: surfaces tensions between two things.

    Usage:
        # Default detectors
        contradict = Contradict()

        # Custom detectors
        contradict = Contradict(detectors=[
            SemanticTensionDetector(),
            CustomLogicDetector(),
        ])

        # Check for logical contradiction
        result = await contradict.invoke(ContradictInput(
            a="The sky is blue",
            b="The sky is not blue",
            mode=TensionMode.LOGICAL,
        ))

        if result.tension:
            # Handle the conflict explicitly
            resolution = await sublate.invoke(result.tension)

        # Observability: see what was checked
        print(f"Checked {len(result.checked_modes)} modes in {result.execution_time_ms}ms")

    The key insight: detect conflicts BEFORE they become runtime errors.
    """

    def __init__(
        self,
        detectors: Optional[list[TensionDetector]] = None,
    ):
        """
        Initialize with optional custom tension detectors.

        If no detectors provided, uses DefaultTensionDetector.

        Args:
            detectors: List of TensionDetector implementations to use
        """
        self._detectors: list[TensionDetector]
        if detectors is None:
            self._detectors = [DefaultTensionDetector()]
        else:
            self._detectors = detectors

    @property
    def name(self) -> str:
        return "Contradict"

    async def invoke(self, input: ContradictInput) -> ContradictResult:
        """
        Check for contradiction between a and b using registered detectors.

        Returns ContradictResult with tension (if found) and metadata.
        """
        start_time = time.perf_counter()

        modes = [input.mode] if input.mode else list(TensionMode)
        checked_modes = []
        found_tension = None

        # Try each detector in sequence
        for detector in self._detectors:
            for mode in modes:
                if mode not in checked_modes:
                    checked_modes.append(mode)

                tension = await detector.detect(input.a, input.b, mode)
                if tension:
                    found_tension = tension
                    break

            if found_tension:
                break

        execution_time_ms = (time.perf_counter() - start_time) * 1000

        return ContradictResult(
            tension=found_tension,
            checked_modes=checked_modes,
            execution_time_ms=execution_time_ms,
        )


# Default tension detector implementation
class DefaultTensionDetector:
    """
    Default implementation of TensionDetector protocol.

    Handles common contradiction cases:
    - LOGICAL: Boolean opposites, string negations
    - PRAGMATIC: Conflicting dict values
    - AXIOLOGICAL: Value conflicts (requires Ground context)
    - TEMPORAL: Past vs present conflicts (requires history)
    """

    async def detect(self, a: Any, b: Any, mode: TensionMode) -> Optional[Tension]:
        """Detect tension using default logic."""
        if mode == TensionMode.LOGICAL:
            return self._check_logical(a, b)
        elif mode == TensionMode.PRAGMATIC:
            return self._check_pragmatic(a, b)
        elif mode == TensionMode.AXIOLOGICAL:
            return self._check_axiological(a, b)
        elif mode == TensionMode.TEMPORAL:
            return self._check_temporal(a, b)

        return None

    def _check_logical(self, a: Any, b: Any) -> Optional[Tension]:
        """Check for direct logical contradiction."""
        # Simple case: boolean opposites
        if isinstance(a, bool) and isinstance(b, bool) and a != b:
            return Tension(
                mode=TensionMode.LOGICAL,
                thesis=a,
                antithesis=b,
                description=f"Boolean contradiction: {a} vs {b}",
                severity=1.0,
            )

        # String negation patterns
        if isinstance(a, str) and isinstance(b, str):
            a_lower, b_lower = a.lower(), b.lower()
            if f"not {a_lower}" == b_lower or f"not {b_lower}" == a_lower:
                return Tension(
                    mode=TensionMode.LOGICAL,
                    thesis=a,
                    antithesis=b,
                    description=f"Negation: '{a}' vs '{b}'",
                    severity=0.9,
                )

        return None

    def _check_pragmatic(self, a: Any, b: Any) -> Optional[Tension]:
        """Check for conflicting recommendations."""
        # Dict-based recommendations
        if isinstance(a, dict) and isinstance(b, dict):
            for key in set(a.keys()) & set(b.keys()):
                if a[key] != b[key]:
                    return Tension(
                        mode=TensionMode.PRAGMATIC,
                        thesis=a,
                        antithesis=b,
                        description=f"Different values for '{key}': {a[key]} vs {b[key]}",
                        severity=0.7,
                    )

        return None

    def _check_axiological(self, a: Any, b: Any) -> Optional[Tension]:
        """Check for value conflicts."""
        # Would need Ground context to know values
        # Placeholder for value-aware checking
        return None

    def _check_temporal(self, a: Any, b: Any) -> Optional[Tension]:
        """Check for past-self vs present-self conflicts."""
        # Would need history context
        # Placeholder for temporal checking
        return None


# Specific contradiction checkers for common scenarios

class NameCollisionChecker(Agent[tuple[str, set[str]], Optional[Tension]]):
    """Check if a name collides with existing names."""

    @property
    def name(self) -> str:
        return "NameCollisionChecker"

    async def invoke(
        self, input: tuple[str, set[str]]
    ) -> Optional[Tension]:
        proposed_name, existing_names = input

        if proposed_name in existing_names:
            return Tension(
                mode=TensionMode.LOGICAL,
                thesis=proposed_name,
                antithesis=f"Already exists: {proposed_name}",
                description=f"Name collision: '{proposed_name}' already exists",
                severity=0.8,
            )

        return None


class ConfigConflictChecker(Agent[tuple[dict[str, Any], dict[str, Any]], Optional[Tension]]):
    """Check for conflicting configuration values."""

    @property
    def name(self) -> str:
        return "ConfigConflictChecker"

    async def invoke(
        self, input: tuple[dict[str, Any], dict[str, Any]]
    ) -> Optional[Tension]:
        config_a, config_b = input

        # Find conflicting keys
        for key in set(config_a.keys()) & set(config_b.keys()):
            if config_a[key] != config_b[key]:
                return Tension(
                    mode=TensionMode.PRAGMATIC,
                    thesis={key: config_a[key]},
                    antithesis={key: config_b[key]},
                    description=f"Config conflict on '{key}'",
                    severity=0.7,
                )

        return None
