"""
DurablePurgatory: Crash-resistant Purgatory with D-gent backing.

This module provides persistent storage for semaphore tokens using the
D-gent (Data Agent) pattern. Tokens survive server restarts and can be
recovered on startup.

The Symbiont Pattern:
    DurablePurgatory = Purgatory Logic + D-gent Memory

Usage:
    >>> from agents.d.volatile import VolatileAgent
    >>> from agents.flux.semaphore.durable import DurablePurgatory
    >>>
    >>> # Create with volatile memory (for testing)
    >>> memory = VolatileAgent(_state={"tokens": {}})
    >>> purgatory = DurablePurgatory(memory=memory)
    >>>
    >>> # Or use persistent D-gent (for production)
    >>> from agents.d.persistent import PersistentAgent
    >>> memory = PersistentAgent(path="/var/kgents/purgatory.json")
    >>> purgatory = DurablePurgatory(memory=memory)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypedDict

from agents.d.protocol import DataAgent

from .purgatory import PheromoneEmitter, Purgatory
from .reentry import ReentryContext
from .token import SemaphoreToken


class PurgatoryState(TypedDict):
    """Schema for persisted purgatory state."""

    tokens: dict[str, dict[str, Any]]  # token_id -> token.to_json()
    version: int  # Schema version for future migrations


DEFAULT_STATE: PurgatoryState = {"tokens": {}, "version": 1}


@dataclass
class DurablePurgatory(Purgatory):
    """
    Purgatory with D-gent backing for crash resistance.

    This extends Purgatory to persist token state to a D-gent.
    Tokens survive server restarts and can be recovered.

    Key Behaviors:
    1. All mutations (save, resolve, cancel, void) are persisted
    2. recover() loads tokens from D-gent on startup
    3. Tokens are stored as JSON dicts (via to_json/from_json)
    4. State includes schema version for future migrations

    Example:
        >>> from agents.d.volatile import VolatileAgent
        >>>
        >>> memory = VolatileAgent(_state=DEFAULT_STATE.copy())
        >>> purgatory = DurablePurgatory(memory=memory)
        >>>
        >>> # Save token
        >>> await purgatory.save(token)
        >>>
        >>> # Restart simulation: create new purgatory
        >>> purgatory2 = DurablePurgatory(memory=memory)
        >>> recovered = await purgatory2.recover()
        >>> assert len(recovered) == 1
    """

    memory: DataAgent[PurgatoryState] | None = field(default=None)
    """D-gent for persistent storage."""

    def __post_init__(self) -> None:
        """Wire memory to base class."""
        # Set _memory for base class compatibility
        self._memory = self.memory

    async def save(self, token: SemaphoreToken[Any]) -> None:
        """
        Eject an event to Purgatory (with persistence).

        Extends base class to persist after save.
        """
        self._pending[token.id] = token
        await self._persist()

        # Emit pheromone signal
        await self._signal(
            "purgatory.ejected",
            {
                "token_id": token.id,
                "reason": token.reason.value,
                "severity": token.severity,
                "prompt": token.prompt,
                "has_deadline": token.deadline is not None,
            },
        )

    async def resolve(
        self,
        token_id: str,
        human_input: Any,
    ) -> ReentryContext[Any] | None:
        """
        Resolve a pending semaphore (with persistence).

        Extends base class to persist after resolve.
        """
        token = self._pending.get(token_id)
        if token is None:
            return None
        if not token.is_pending:
            return None

        token.resolved_at = datetime.now()

        reentry: ReentryContext[Any] = ReentryContext(
            token_id=token_id,
            frozen_state=token.frozen_state,
            human_input=human_input,
            original_event=token.original_event,
        )

        await self._persist()

        # Emit pheromone signal
        await self._signal(
            "purgatory.resolved",
            {
                "token_id": token_id,
                "reason": token.reason.value,
                "severity": token.severity,
                "human_input_type": type(human_input).__name__,
            },
        )

        return reentry

    async def cancel(self, token_id: str) -> bool:
        """
        Cancel a pending semaphore (with persistence).

        Extends base class to persist after cancel.
        """
        token = self._pending.get(token_id)
        if token is None:
            return False
        if not token.is_pending:
            return False

        token.cancelled_at = datetime.now()

        await self._persist()

        # Emit pheromone signal
        await self._signal(
            "purgatory.cancelled",
            {
                "token_id": token_id,
                "reason": token.reason.value,
                "severity": token.severity,
            },
        )

        return True

    async def void_expired(self) -> list[SemaphoreToken[Any]]:
        """
        Void all tokens whose deadlines have passed (with persistence).

        Extends base class to persist after voiding.
        """
        voided: list[SemaphoreToken[Any]] = []

        for token in self._pending.values():
            if token.is_pending and token.check_deadline():
                voided.append(token)

                # Emit pheromone signal
                await self._signal(
                    "purgatory.voided",
                    {
                        "token_id": token.id,
                        "reason": token.reason.value,
                        "severity": token.severity,
                        "deadline": token.deadline.isoformat()
                        if token.deadline
                        else None,
                        "escalation": token.escalation,
                    },
                )

        if voided:
            await self._persist()

        return voided

    async def recover(self) -> list[SemaphoreToken[Any]]:
        """
        Recover pending semaphores after restart.

        Loads tokens from D-gent and populates _pending.
        Also checks for expired deadlines.

        Returns:
            List of pending tokens recovered (excluding voided)
        """
        if self.memory is None:
            return []

        try:
            state = await self.memory.load()
            if state and "tokens" in state:
                # Reconstruct tokens from JSON
                for token_id, token_data in state["tokens"].items():
                    token = SemaphoreToken.from_json(token_data)
                    self._pending[token_id] = token
        except Exception:
            # If loading fails, start fresh
            pass

        # Check for expired deadlines
        await self.void_expired()

        return self.list_pending()

    async def _persist(self) -> None:
        """
        Persist current state to D-gent.

        Serializes all tokens to JSON for storage.
        """
        if self.memory is None:
            return

        state: PurgatoryState = {
            "tokens": {
                token_id: token.to_json() for token_id, token in self._pending.items()
            },
            "version": 1,
        }

        await self.memory.save(state)

    def attach_memory(self, memory: DataAgent[PurgatoryState]) -> "DurablePurgatory":
        """
        Attach a D-gent memory adapter.

        Args:
            memory: The D-gent to use for persistence

        Returns:
            Self (for chaining)
        """
        self.memory = memory
        self._memory = memory
        return self


def create_durable_purgatory(
    memory: DataAgent[PurgatoryState] | None = None,
    emit_pheromone: PheromoneEmitter | None = None,
) -> DurablePurgatory:
    """
    Create a DurablePurgatory with optional memory and pheromone emitter.

    Args:
        memory: Optional D-gent for persistence
        emit_pheromone: Optional callback for pheromone signals

    Returns:
        Configured DurablePurgatory
    """
    purgatory = DurablePurgatory(memory=memory)
    if emit_pheromone is not None:
        purgatory._emit_pheromone = emit_pheromone
    return purgatory


async def create_and_recover_purgatory(
    memory: DataAgent[PurgatoryState] | None = None,
    emit_pheromone: PheromoneEmitter | None = None,
) -> DurablePurgatory:
    """
    Create a DurablePurgatory and recover state from memory.

    Convenience function for startup initialization.

    Args:
        memory: Optional D-gent for persistence (None for in-memory)
        emit_pheromone: Optional callback for pheromone signals

    Returns:
        Configured and recovered DurablePurgatory
    """
    purgatory = create_durable_purgatory(memory=memory, emit_pheromone=emit_pheromone)
    await purgatory.recover()
    return purgatory
