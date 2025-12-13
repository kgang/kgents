"""
Turn - A Causal Event in the Turn-gents Protocol.

A Turn extends Event with:
- TurnType: What kind of interaction (Speech, Action, Thought, Yield, Silence)
- State hashes: For debugging and replay
- Confidence: Meta-cognition score
- Entropy cost: Thermodynamic accounting (Accursed Share)

This is the atomic unit of the Turn-gents "Chronos-Kairos Protocol."

Mathematical Foundation:
- Turns are morphisms: (S_pre × Input) → (S_post × Output)
- Composition via TraceMonoid yields partial order
- Causal cone projection replaces window-based context

References:
- Lamport, "Time, Clocks, and the Ordering of Events" (1978)
- Spivak, "Polynomial Functors" (2023-2024)
- Abramsky, "Game Semantics" (1994-present)
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Generic, TypeVar

from .event import Event

T = TypeVar("T")


class TurnType(Enum):
    """
    The five types of turns in Turn-gents.

    These form an interface contract (game-semantic "moves"),
    not a taxonomy explosion.

    | Type    | Game Move | Governance      | Description                    |
    |---------|-----------|-----------------|--------------------------------|
    | SPEECH  | Output    | Inspectable     | Utterance to user/agent        |
    | ACTION  | Effect    | Interceptable   | Tool call, side effect         |
    | THOUGHT | Internal  | Hidden default  | Chain-of-thought               |
    | YIELD   | Pause     | Blocks          | Request for human approval     |
    | SILENCE | Pass      | Logged          | Intentional non-action         |
    """

    SPEECH = auto()  # Utterance to user/agent
    ACTION = auto()  # Tool call, side effect
    THOUGHT = auto()  # Internal chain-of-thought
    YIELD = auto()  # Request for approval (blocks)
    SILENCE = auto()  # Intentional non-action (pass)


@dataclass(frozen=True)
class Turn(Event[T], Generic[T]):
    """
    A Turn is an Event with causal structure and governance metadata.

    Turns extend Events with:
    - turn_type: What kind of interaction this represents
    - state_hash_pre: Hash of state before turn (for debugging)
    - state_hash_post: Hash of state after turn (for debugging)
    - confidence: Meta-cognition score [0.0, 1.0]
    - entropy_cost: Thermodynamic cost (Accursed Share accounting)

    Turn IS-A Event, so all Weave operations work unchanged.
    This is the generative principle: specification compiles to implementation.

    Example:
        turn = Turn.create_turn(
            content="Hello, world!",
            source="agent-a",
            turn_type=TurnType.SPEECH,
            state_pre={"mode": "idle"},
            state_post={"mode": "conversing"},
            confidence=0.95,
        )
    """

    # Turn-specific fields (frozen for immutability)
    turn_type: TurnType
    state_hash_pre: str
    state_hash_post: str
    confidence: float
    entropy_cost: float

    @classmethod
    def create_turn(
        cls,
        content: T,
        source: str,
        turn_type: TurnType,
        *,
        state_pre: Any | None = None,
        state_post: Any | None = None,
        confidence: float = 1.0,
        entropy_cost: float = 0.0,
        turn_id: str | None = None,
        timestamp: float | None = None,
    ) -> Turn[T]:
        """
        Factory method to create a Turn.

        Args:
            content: The turn payload (generic)
            source: Agent that emitted this turn
            turn_type: Type of turn (Speech, Action, etc.)
            state_pre: State before turn (hashed for storage)
            state_post: State after turn (hashed for storage)
            confidence: Meta-cognition score [0.0, 1.0]
            entropy_cost: Thermodynamic cost
            turn_id: Optional ID (generated if not provided)
            timestamp: Optional timestamp (current time if not provided)

        Returns:
            A new Turn instance
        """
        return cls(
            id=turn_id or str(uuid.uuid4()),
            content=content,
            timestamp=timestamp or time.time(),
            source=source,
            turn_type=turn_type,
            state_hash_pre=_hash_state(state_pre),
            state_hash_post=_hash_state(state_post),
            confidence=max(0.0, min(1.0, confidence)),  # Clamp to [0, 1]
            entropy_cost=max(0.0, entropy_cost),  # Non-negative
        )

    @classmethod
    def from_event(
        cls,
        event: Event[T],
        turn_type: TurnType,
        *,
        state_pre: Any | None = None,
        state_post: Any | None = None,
        confidence: float = 1.0,
        entropy_cost: float = 0.0,
    ) -> Turn[T]:
        """
        Lift an existing Event to a Turn.

        Preserves the Event's id, content, timestamp, and source.

        Args:
            event: The Event to lift
            turn_type: Type of turn
            state_pre: State before turn
            state_post: State after turn
            confidence: Meta-cognition score
            entropy_cost: Thermodynamic cost

        Returns:
            A new Turn with the Event's data
        """
        return cls(
            id=event.id,
            content=event.content,
            timestamp=event.timestamp,
            source=event.source,
            turn_type=turn_type,
            state_hash_pre=_hash_state(state_pre),
            state_hash_post=_hash_state(state_post),
            confidence=max(0.0, min(1.0, confidence)),
            entropy_cost=max(0.0, entropy_cost),
        )

    def is_observable(self) -> bool:
        """Check if this turn is externally observable (not THOUGHT)."""
        return self.turn_type != TurnType.THOUGHT

    def is_blocking(self) -> bool:
        """Check if this turn blocks until resolved (YIELD)."""
        return self.turn_type == TurnType.YIELD

    def is_effectful(self) -> bool:
        """Check if this turn has side effects (ACTION)."""
        return self.turn_type == TurnType.ACTION

    def requires_governance(self) -> bool:
        """Check if this turn requires governance review."""
        return self.turn_type in {TurnType.ACTION, TurnType.YIELD}


@dataclass(frozen=True)
class YieldTurn(Turn[T], Generic[T]):
    """
    A Yield turn that blocks until approval is granted.

    Extends Turn with:
    - yield_reason: Why approval is needed
    - required_approvers: Who must approve (agent IDs)
    - status: Current approval status

    Yield turns are the governance intercept points in Turn-gents.
    They operationalize the "ethical" principle: preserve human agency.
    """

    yield_reason: str
    required_approvers: frozenset[str]
    approved_by: frozenset[str]  # Who has approved so far

    @classmethod
    def create_yield(
        cls,
        content: T,
        source: str,
        yield_reason: str,
        required_approvers: set[str],
        *,
        state_pre: Any | None = None,
        state_post: Any | None = None,
        confidence: float = 1.0,
        entropy_cost: float = 0.0,
        turn_id: str | None = None,
        timestamp: float | None = None,
    ) -> YieldTurn[T]:
        """
        Create a Yield turn requesting approval.

        Args:
            content: The proposed action/content
            source: Agent requesting approval
            yield_reason: Why approval is needed
            required_approvers: Set of agent IDs that must approve
            state_pre: State before turn
            state_post: State after turn (if approved)
            confidence: Meta-cognition score
            entropy_cost: Thermodynamic cost
            turn_id: Optional ID
            timestamp: Optional timestamp

        Returns:
            A new YieldTurn in PENDING status
        """
        return cls(
            id=turn_id or str(uuid.uuid4()),
            content=content,
            timestamp=timestamp or time.time(),
            source=source,
            turn_type=TurnType.YIELD,
            state_hash_pre=_hash_state(state_pre),
            state_hash_post=_hash_state(state_post),
            confidence=max(0.0, min(1.0, confidence)),
            entropy_cost=max(0.0, entropy_cost),
            yield_reason=yield_reason,
            required_approvers=frozenset(required_approvers),
            approved_by=frozenset(),
        )

    def approve(self, approver: str) -> YieldTurn[T]:
        """
        Record an approval (returns new YieldTurn—immutable).

        Args:
            approver: Agent ID granting approval

        Returns:
            New YieldTurn with updated approvals
        """
        if approver not in self.required_approvers:
            raise ValueError(f"{approver} is not in required_approvers")

        new_approved = self.approved_by | {approver}

        return YieldTurn(
            id=self.id,
            content=self.content,
            timestamp=self.timestamp,
            source=self.source,
            turn_type=self.turn_type,
            state_hash_pre=self.state_hash_pre,
            state_hash_post=self.state_hash_post,
            confidence=self.confidence,
            entropy_cost=self.entropy_cost,
            yield_reason=self.yield_reason,
            required_approvers=self.required_approvers,
            approved_by=frozenset(new_approved),
        )

    def is_approved(self) -> bool:
        """Check if all required approvals have been granted."""
        return self.required_approvers <= self.approved_by

    def is_rejected(self) -> bool:
        """Check if explicitly rejected (not implemented yet)."""
        # Future: track rejections separately
        return False

    def pending_approvers(self) -> frozenset[str]:
        """Get approvers who haven't approved yet."""
        return self.required_approvers - self.approved_by


def _hash_state(state: Any | None) -> str:
    """
    Compute a hash of the state for debugging/replay.

    This is NOT cryptographically secure—it's for debugging.
    Uses repr() for determinism within a session.
    """
    if state is None:
        return "empty"

    try:
        state_repr = repr(state)
        return hashlib.sha256(state_repr.encode()).hexdigest()[:16]
    except Exception:
        return "unhashable"
