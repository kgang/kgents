"""
BrainPolynomial: Memory Operations as State Machine.

The brain polynomial models memory operations as a dynamical system:
- IDLE: Ready for new operations
- CAPTURING: Storing content to holographic memory
- SEARCHING: Semantic search in progress
- SURFACING: Drawing serendipitous memories from void
- HEALING: Repairing ghost memories (coherency maintenance)

The Insight (from Barad):
    Memory is not retrieval but *re-constitution*.
    Each search makes a different agential cut on stored experience.
    The crystal does not contain the memory—it enables its re-emergence.

Example:
    >>> poly = BRAIN_POLYNOMIAL
    >>> state, output = poly.invoke(BrainPhase.IDLE, CaptureInput(content="..."))
    >>> print(state, output)
    BrainPhase.CAPTURING CaptureOutput(...)

See: spec/m-gents/holographic-memory.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent

# =============================================================================
# Brain Phase (Positions in the Polynomial)
# =============================================================================


class BrainPhase(Enum):
    """
    Positions in the brain polynomial.

    These are operational modes, not internal states.
    The phase determines which operations are valid (directions).

    From Barad: The transition reconfigures the memory phenomenon.
    We don't "read from" memory—we reconstitute experience.
    """

    IDLE = auto()
    CAPTURING = auto()
    SEARCHING = auto()
    SURFACING = auto()
    HEALING = auto()


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class CaptureInput:
    """Input for memory capture."""

    content: str
    tags: tuple[str, ...] = ()
    source_type: str = "capture"
    source_ref: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class SearchInput:
    """Input for semantic search."""

    query: str
    limit: int = 10
    tags: tuple[str, ...] | None = None


@dataclass(frozen=True)
class SurfaceInput:
    """Input for serendipitous surfacing."""

    context: str | None = None
    entropy: float = 0.7  # Higher = more random


@dataclass(frozen=True)
class HealInput:
    """Input for ghost healing."""

    pass


@dataclass(frozen=True)
class IdleInput:
    """Input for returning to idle."""

    pass


class BrainInput:
    """Factory for brain inputs."""

    @staticmethod
    def capture(
        content: str,
        tags: tuple[str, ...] = (),
        source_type: str = "capture",
    ) -> CaptureInput:
        """Create a capture input."""
        return CaptureInput(content=content, tags=tags, source_type=source_type)

    @staticmethod
    def search(
        query: str, limit: int = 10, tags: tuple[str, ...] | None = None
    ) -> SearchInput:
        """Create a search input."""
        return SearchInput(query=query, limit=limit, tags=tags)

    @staticmethod
    def surface(context: str | None = None, entropy: float = 0.7) -> SurfaceInput:
        """Create a surface input (draw from the void)."""
        return SurfaceInput(context=context, entropy=entropy)

    @staticmethod
    def heal() -> HealInput:
        """Create a heal input (repair ghosts)."""
        return HealInput()

    @staticmethod
    def idle() -> IdleInput:
        """Create an idle input (return to ready state)."""
        return IdleInput()


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class BrainOutput:
    """Output from brain transitions."""

    phase: BrainPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CaptureOutput(BrainOutput):
    """Output from a capture operation."""

    crystal_id: str | None = None
    has_embedding: bool = False


@dataclass
class SearchOutput(BrainOutput):
    """Output from a search operation."""

    query: str = ""
    result_count: int = 0


@dataclass
class SurfaceOutput(BrainOutput):
    """Output from a surface operation."""

    crystal_id: str | None = None
    entropy: float = 0.0


@dataclass
class HealOutput(BrainOutput):
    """Output from a heal operation."""

    ghosts_healed: int = 0


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def brain_directions(phase: BrainPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each brain phase.

    This encodes the mode-dependent behavior:
    - IDLE: Can do any operation
    - CAPTURING: Can only return to idle (operation in progress)
    - SEARCHING: Can only return to idle (operation in progress)
    - SURFACING: Can only return to idle (operation in progress)
    - HEALING: Can only return to idle (operation in progress)
    """
    match phase:
        case BrainPhase.IDLE:
            return frozenset(
                {CaptureInput, SearchInput, SurfaceInput, HealInput, type, Any}
            )
        case BrainPhase.CAPTURING:
            return frozenset({IdleInput, type, Any})
        case BrainPhase.SEARCHING:
            return frozenset({IdleInput, type, Any})
        case BrainPhase.SURFACING:
            return frozenset({IdleInput, type, Any})
        case BrainPhase.HEALING:
            return frozenset({IdleInput, type, Any})
        case _:
            return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def brain_transition(phase: BrainPhase, input: Any) -> tuple[BrainPhase, BrainOutput]:
    """
    Brain state transition function.

    This is the polynomial core:
    transition: Phase × Input → (NewPhase, Output)

    From Barad: Memory operations reconfigure the experiential phenomenon.
    Capture doesn't store—it crystallizes. Search doesn't retrieve—it surfaces.
    """
    match phase:
        case BrainPhase.IDLE:
            if isinstance(input, CaptureInput):
                return BrainPhase.CAPTURING, CaptureOutput(
                    phase=BrainPhase.CAPTURING,
                    success=True,
                    message="Capturing to holographic memory",
                    metadata={
                        "content_preview": input.content[:100],
                        "tags": list(input.tags),
                        "source_type": input.source_type,
                    },
                )
            elif isinstance(input, SearchInput):
                return BrainPhase.SEARCHING, SearchOutput(
                    phase=BrainPhase.SEARCHING,
                    success=True,
                    message=f"Searching for: {input.query}",
                    query=input.query,
                    metadata={
                        "limit": input.limit,
                        "tags": list(input.tags) if input.tags else None,
                    },
                )
            elif isinstance(input, SurfaceInput):
                return BrainPhase.SURFACING, SurfaceOutput(
                    phase=BrainPhase.SURFACING,
                    success=True,
                    message="Surfacing from the void",
                    entropy=input.entropy,
                    metadata={
                        "context": input.context,
                        "entropy": input.entropy,
                    },
                )
            elif isinstance(input, HealInput):
                return BrainPhase.HEALING, HealOutput(
                    phase=BrainPhase.HEALING,
                    success=True,
                    message="Healing ghost memories",
                )
            else:
                return BrainPhase.IDLE, BrainOutput(
                    phase=BrainPhase.IDLE,
                    success=False,
                    message=f"Unknown input type: {type(input).__name__}",
                )

        case BrainPhase.CAPTURING:
            if isinstance(input, IdleInput):
                return BrainPhase.IDLE, BrainOutput(
                    phase=BrainPhase.IDLE,
                    success=True,
                    message="Capture complete, returning to idle",
                )
            else:
                return BrainPhase.CAPTURING, BrainOutput(
                    phase=BrainPhase.CAPTURING,
                    success=False,
                    message="Capture in progress, wait or send idle",
                )

        case BrainPhase.SEARCHING:
            if isinstance(input, IdleInput):
                return BrainPhase.IDLE, BrainOutput(
                    phase=BrainPhase.IDLE,
                    success=True,
                    message="Search complete, returning to idle",
                )
            else:
                return BrainPhase.SEARCHING, BrainOutput(
                    phase=BrainPhase.SEARCHING,
                    success=False,
                    message="Search in progress, wait or send idle",
                )

        case BrainPhase.SURFACING:
            if isinstance(input, IdleInput):
                return BrainPhase.IDLE, BrainOutput(
                    phase=BrainPhase.IDLE,
                    success=True,
                    message="Surfacing complete, returning to idle",
                )
            else:
                return BrainPhase.SURFACING, BrainOutput(
                    phase=BrainPhase.SURFACING,
                    success=False,
                    message="Surfacing in progress, wait or send idle",
                )

        case BrainPhase.HEALING:
            if isinstance(input, IdleInput):
                return BrainPhase.IDLE, BrainOutput(
                    phase=BrainPhase.IDLE,
                    success=True,
                    message="Healing complete, returning to idle",
                )
            else:
                return BrainPhase.HEALING, BrainOutput(
                    phase=BrainPhase.HEALING,
                    success=False,
                    message="Healing in progress, wait or send idle",
                )

        case _:
            return BrainPhase.IDLE, BrainOutput(
                phase=BrainPhase.IDLE,
                success=False,
                message=f"Unknown phase: {phase}",
            )


# =============================================================================
# The Polynomial Agent
# =============================================================================


BRAIN_POLYNOMIAL: PolyAgent[BrainPhase, Any, BrainOutput] = PolyAgent(
    name="BrainPolynomial",
    positions=frozenset(BrainPhase),
    _directions=brain_directions,
    _transition=brain_transition,
)
"""
The Brain polynomial agent.

This models brain behavior as a polynomial state machine:
- positions: 5 phases (IDLE, CAPTURING, SEARCHING, SURFACING, HEALING)
- directions: phase-dependent valid inputs
- transition: memory operation transitions

Key Property:
    Operations are non-reentrant: you must complete one operation
    before starting another. This ensures crystal coherency.
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "BrainPhase",
    # Inputs
    "CaptureInput",
    "SearchInput",
    "SurfaceInput",
    "HealInput",
    "IdleInput",
    "BrainInput",
    # Outputs
    "BrainOutput",
    "CaptureOutput",
    "SearchOutput",
    "SurfaceOutput",
    "HealOutput",
    # Functions
    "brain_directions",
    "brain_transition",
    # Polynomial
    "BRAIN_POLYNOMIAL",
]
