"""
Artisan: The base class for atelier artisans.

Artisans are polynomial agents with streaming-first design.
Instead of request → response, they emit events into a flux.

State Machine:
    IDLE → CONTEMPLATING → WORKING → READY → IDLE
           (receive)      (work)    (yield)

Streaming Pattern:
    Each phase yields AtelierEvent instances that can be observed
    by subscribers (CLI progress, web dashboard, gallery persistence).

From Spivak: An artisan is a polynomial functor P(y) = Σ_{s ∈ State} y^{Direction(s)}
where Direction(IDLE) = {Commission} and Direction(WORKING) = {} (no interrupts).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, AsyncIterator
from uuid import uuid4

# =============================================================================
# State Machine
# =============================================================================


class ArtisanState(Enum):
    """
    Artisan work states.

    Polynomial positions: The artisan can be in exactly one state.
    Each state has different valid inputs (directions).
    """

    IDLE = auto()  # Waiting for commission
    CONTEMPLATING = auto()  # Received commission, thinking
    WORKING = auto()  # Actively creating
    READY = auto()  # Piece complete, ready to yield


# =============================================================================
# Core Data Types
# =============================================================================


@dataclass
class Commission:
    """
    A request to create something.

    Commissions are inputs to the artisan polynomial.
    They include the request, patron identity, and optional context.
    """

    request: str
    patron: str = "wanderer"
    context: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid4().hex[:8])
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for streaming/persistence."""
        return {
            "id": self.id,
            "request": self.request,
            "patron": self.patron,
            "context": dict(self.context),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Commission":
        """Deserialize from stored data."""
        return cls(
            id=data["id"],
            request=data["request"],
            patron=data.get("patron", "wanderer"),
            context=data.get("context", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


@dataclass
class Choice:
    """
    A creative decision made during work.

    Tracks the artisan's reasoning for provenance.
    """

    decision: str
    reason: str
    alternatives: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "reason": self.reason,
            "alternatives": list(self.alternatives),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Choice":
        return cls(
            decision=data["decision"],
            reason=data["reason"],
            alternatives=data.get("alternatives", []),
        )


@dataclass
class Provenance:
    """
    The creative history of a piece.

    Records how the artisan interpreted the request,
    what they considered, and what choices they made.
    """

    interpretation: str
    considerations: list[str]
    choices: list[Choice]
    inspirations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "interpretation": self.interpretation,
            "considerations": list(self.considerations),
            "choices": [c.to_dict() for c in self.choices],
            "inspirations": list(self.inspirations),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Provenance":
        return cls(
            interpretation=data["interpretation"],
            considerations=data.get("considerations", []),
            choices=[Choice.from_dict(c) for c in data.get("choices", [])],
            inspirations=data.get("inspirations", []),
        )


@dataclass
class Piece:
    """
    A completed work from an artisan.

    Pieces are the outputs of the artisan polynomial.
    They include the content, attribution, and full provenance.
    """

    content: Any
    artisan: str
    commission_id: str
    provenance: Provenance
    form: str = "reflection"  # haiku, letter, map, etc.
    id: str = field(default_factory=lambda: uuid4().hex[:8])
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "artisan": self.artisan,
            "commission_id": self.commission_id,
            "form": self.form,
            "provenance": self.provenance.to_dict(),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Piece":
        return cls(
            id=data["id"],
            content=data["content"],
            artisan=data["artisan"],
            commission_id=data["commission_id"],
            form=data.get("form", "reflection"),
            provenance=Provenance.from_dict(data["provenance"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


# =============================================================================
# Streaming Events
# =============================================================================


class AtelierEventType(Enum):
    """Event types for streaming."""

    COMMISSION_RECEIVED = "commission_received"
    CONTEMPLATING = "contemplating"
    WORKING = "working"
    FRAGMENT = "fragment"  # Partial content during streaming
    PIECE_COMPLETE = "piece_complete"
    ERROR = "error"


@dataclass
class AtelierEvent:
    """
    An event in the atelier flux.

    Events are emitted during artisan work and can be observed
    by any subscriber (CLI, web dashboard, gallery persistence).
    """

    event_type: AtelierEventType
    artisan: str
    commission_id: str | None
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "artisan": self.artisan,
            "commission_id": self.commission_id,
            "message": self.message,
            "data": dict(self.data),
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# Base Artisan Class
# =============================================================================


class Artisan:
    """
    Base class for atelier artisans.

    Artisans are streaming-first: instead of returning pieces,
    they yield events into a flux. This allows:
    - Real-time progress updates
    - Cancellation support
    - Multi-subscriber observation
    - Composition via wiring diagrams

    Subclasses must implement:
    - work(): AsyncIterator yielding events during creation
    """

    name: str = "Artisan"
    specialty: str = "creating"
    personality: str = ""

    def __init__(self) -> None:
        self.state = ArtisanState.IDLE
        self.current_commission: Commission | None = None
        self.memory: list[Piece] = []  # Recent pieces for inspiration

    async def receive(self, commission: Commission) -> AsyncIterator[AtelierEvent]:
        """
        Accept a commission and begin contemplating.

        Yields events as the artisan receives and processes the request.
        """
        if self.state != ArtisanState.IDLE:
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan=self.name,
                commission_id=commission.id,
                message=f"Cannot receive commission: artisan is {self.state.name}",
            )
            return

        self.current_commission = commission
        self.state = ArtisanState.CONTEMPLATING

        yield AtelierEvent(
            event_type=AtelierEventType.COMMISSION_RECEIVED,
            artisan=self.name,
            commission_id=commission.id,
            message=f"Received: {commission.request[:50]}...",
            data={"commission": commission.to_dict()},
        )

        yield AtelierEvent(
            event_type=AtelierEventType.CONTEMPLATING,
            artisan=self.name,
            commission_id=commission.id,
            message=f"{self.name} is contemplating...",
        )

    def work(self) -> AsyncIterator[AtelierEvent]:
        """
        Create the piece, yielding events as work progresses.

        Override in subclasses to implement specific artisan behavior.
        The final event should be PIECE_COMPLETE with the Piece in data.

        Note: Subclasses should implement this as an async generator.
        """
        raise NotImplementedError("Subclasses must implement work()")

    async def stream(self, commission: Commission) -> AsyncIterator[AtelierEvent]:
        """
        Full streaming workflow: receive → work → complete.

        This is the primary entry point for using an artisan.
        All events are yielded in order, allowing subscribers to
        observe the entire creation process.
        """
        # Receive phase
        async for event in self.receive(commission):
            yield event
            if event.event_type == AtelierEventType.ERROR:
                return

        # Work phase
        async for event in self.work():
            yield event

        # Reset state
        self.state = ArtisanState.IDLE

    def _build_prompt(self, commission: Commission) -> str:
        """Build the LLM prompt for this commission."""
        memory_context = ""
        if self.memory:
            recent = self.memory[-3:]
            memory_context = "\n\nRecent pieces you've made:\n" + "\n".join(
                f"- {p.provenance.interpretation}: {str(p.content)[:100]}"
                for p in recent
            )

        return f"""{self.personality}

You are {self.name}, an artisan who specializes in {self.specialty}.

The patron asks: "{commission.request}"
{memory_context}

Respond with JSON:
{{
  "interpretation": "how you understood this request",
  "considerations": ["what you thought about"],
  "content": "the piece itself",
  "form": "what form it took (e.g., haiku, letter, map)"
}}
"""

    def __repr__(self) -> str:
        return f"{self.name}(state={self.state.name})"


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # State machine
    "ArtisanState",
    # Core types
    "Commission",
    "Choice",
    "Provenance",
    "Piece",
    # Streaming
    "AtelierEvent",
    "AtelierEventType",
    # Base class
    "Artisan",
]
