"""
L0 Kernel Primitives

The five irreducible operations. Everything else derives from these.

- compose: Sequential composition (f >> g)
- apply: Function application (f(x))
- match: Structural pattern matching
- emit: Artifact generation
- witness: Full proof capture
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Generic, TypeVar

from .ast import L0Pattern
from .patterns import match as pattern_match

# =============================================================================
# Type Variables
# =============================================================================

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


# =============================================================================
# Artifact Type
# =============================================================================


@dataclass(frozen=True)
class Artifact:
    """
    Emitted artifact from L0 execution.

    Artifacts are the outputs of compilation.
    """

    artifact_type: str
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# Verification Status (matching services/verification)
# =============================================================================


class VerificationStatus(str, Enum):
    """Status of witness verification."""

    SUCCESS = "success"
    FAILURE = "failure"
    NEEDS_REVIEW = "needs_review"
    PENDING = "pending"


# =============================================================================
# Trace Witness Result (compatible with services/verification)
# =============================================================================


@dataclass(frozen=True)
class TraceWitnessResult:
    """
    Full witness capture. Compatible with services/verification.

    Per design decision: capture everything, no hash shortcuts.
    """

    witness_id: str
    agent_path: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    intermediate_steps: tuple[Any, ...] = ()  # L0 is atomic, no intermediate steps
    specification_id: str | None = None  # L0 is spec-agnostic
    properties_verified: tuple[str, ...] = ()
    violations_found: tuple[dict[str, Any], ...] = ()
    verification_status: VerificationStatus = VerificationStatus.SUCCESS
    execution_time_ms: float | None = None
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def pass_name(self) -> str:
        """Extract pass name from agent path."""
        # agent_path is "concept.compiler.l0.{pass_name}"
        parts = self.agent_path.split(".")
        return parts[-1] if parts else ""


# =============================================================================
# Composed Callable
# =============================================================================


@dataclass
class ComposedCallable(Generic[A, C]):
    """
    Result of composing two callables.

    (f >> g)(x) = g(f(x))
    """

    first: Callable[[A], Any]
    second: Callable[[Any], C]
    name: str = "composed"

    async def __call__(self, input: A) -> C:
        """Execute composed callable."""
        # Handle both sync and async callables
        intermediate = self.first(input)
        if hasattr(intermediate, "__await__"):
            intermediate = await intermediate

        result = self.second(intermediate)
        if hasattr(result, "__await__"):
            result = await result

        return result


# =============================================================================
# L0 Primitives
# =============================================================================


@dataclass
class L0Primitives:
    """
    The five irreducible operations.

    Everything in ASHC derives from these primitives.
    """

    def compose(
        self,
        f: Callable[[A], B],
        g: Callable[[B], C],
    ) -> ComposedCallable[A, C]:
        """
        Sequential composition: f >> g

        Returns a new callable that applies f then g.
        """
        return ComposedCallable(first=f, second=g)

    async def apply(
        self,
        f: Callable[[A], B],
        x: A,
    ) -> B:
        """
        Function application: f(x)

        Handles both sync and async callables.
        """
        result = f(x)
        if hasattr(result, "__await__"):
            result = await result
        return result

    def match(
        self,
        pattern: L0Pattern,
        value: Any,
    ) -> dict[str, Any] | None:
        """
        Structural pattern matching.

        Returns bindings if match succeeds, None if fails.
        Delegates to patterns.py.
        """
        return pattern_match(pattern, value)

    def emit(
        self,
        artifact_type: str,
        content: Any,
    ) -> Artifact:
        """
        Emit an artifact.

        Creates timestamped artifact for collection.
        """
        return Artifact(
            artifact_type=artifact_type,
            content=content,
            timestamp=datetime.now(),
        )

    def witness(
        self,
        pass_name: str,
        input_data: Any,
        output_data: Any,
    ) -> TraceWitnessResult:
        """
        Emit a full witness. Captures complete input/output.

        Per design decision: full capture, no hash shortcuts.
        Compatible with services/verification TraceWitnessResult.
        """
        return TraceWitnessResult(
            witness_id=str(uuid.uuid4()),
            agent_path=f"concept.compiler.l0.{pass_name}",
            input_data=self._serialize(input_data),
            output_data=self._serialize(output_data),
            intermediate_steps=(),
            specification_id=None,
            properties_verified=(),
            violations_found=(),
            verification_status=VerificationStatus.SUCCESS,
            execution_time_ms=None,
            created_at=datetime.now(),
        )

    def _serialize(self, value: Any) -> dict[str, Any]:
        """
        Serialize any value for witness capture.

        Full capture: preserves complete data for replay.
        """
        if value is None:
            return {"_type": "null", "_value": None}
        elif isinstance(value, dict):
            return {
                "_type": "dict",
                "_value": {k: self._serialize(v) for k, v in value.items()},
            }
        elif isinstance(value, (list, tuple)):
            return {
                "_type": "list" if isinstance(value, list) else "tuple",
                "_value": [self._serialize(v) for v in value],
            }
        elif isinstance(value, (str, int, float, bool)):
            return {"_type": type(value).__name__, "_value": value}
        elif hasattr(value, "__dict__"):
            return {
                "_type": type(value).__name__,
                "_value": {k: self._serialize(v) for k, v in vars(value).items()},
            }
        else:
            return {"_type": "repr", "_value": repr(value)}


# =============================================================================
# Default Primitives Instance
# =============================================================================


def get_primitives() -> L0Primitives:
    """Get the default L0 primitives instance."""
    return L0Primitives()
