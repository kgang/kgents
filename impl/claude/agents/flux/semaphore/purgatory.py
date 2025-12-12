"""
Purgatory: The waiting room for ejected events.

Tokens wait here until humans provide context.
Crash-resistant via D-gent backing (Phase 3).

Pheromone Signals:
- purgatory.ejected: Token ejected to purgatory
- purgatory.resolved: Token resolved by human
- purgatory.cancelled: Token cancelled
- purgatory.voided: Token deadline expired (defaulted on promise)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Awaitable, Callable

from .reentry import ReentryContext
from .token import SemaphoreToken

# Type alias for pheromone emission callback
PheromoneEmitter = Callable[[str, dict[str, Any]], Awaitable[None]]


@dataclass
class Purgatory:
    """
    The waiting room for ejected events.

    Crash-resistant: survives server restarts via D-gent backing (Phase 3).
    For Phase 1, in-memory only.

    Key Insight: We pickle DATA (frozen_state), not GENERATORS.
    This is what makes Purgatory crash-safe when D-gent is wired.

    Design Decisions:
    1. Cancelled tokens remain in _pending (marked), not removed.
       This preserves audit trail and prevents double-resolution.
    2. resolve() is idempotent: calling twice returns None on second call.
    3. No polling. Resolution is explicit via resolve() call.
    4. No events emitted on state change (deferred to Phase 2 integration).

    Usage:
        >>> purgatory = Purgatory()
        >>>
        >>> # Agent returns SemaphoreToken, FluxAgent detects and ejects
        >>> await purgatory.save(token)
        >>>
        >>> # Stream continues, human eventually resolves
        >>> reentry = await purgatory.resolve(token.id, human_input)
        >>>
        >>> # reentry is injected as Perturbation
        >>> # Agent.resume() receives it

    Example workflow:
        >>> # 1. Agent encounters situation needing human input
        >>> token = SemaphoreToken(
        ...     reason=SemaphoreReason.APPROVAL_NEEDED,
        ...     frozen_state=pickle.dumps(agent_state),
        ...     prompt="Delete 47 records?",
        ... )
        >>>
        >>> # 2. Eject to Purgatory
        >>> await purgatory.save(token)
        >>>
        >>> # 3. Human reviews and resolves
        >>> reentry = await purgatory.resolve(token.id, "Approve")
        >>>
        >>> # 4. Agent resumes with context
        >>> restored_state = pickle.loads(reentry.frozen_state)
        >>> agent.resume(restored_state, reentry.human_input)
    """

    _pending: dict[str, SemaphoreToken[Any]] = field(default_factory=dict)
    """Map of token_id → SemaphoreToken. Includes resolved/cancelled/voided tokens."""

    _memory: Any = None
    """D-gent memory adapter (Phase 3). None for in-memory only."""

    _emit_pheromone: PheromoneEmitter | None = None
    """Optional callback for pheromone emission. Best-effort: failures are ignored."""

    async def save(self, token: SemaphoreToken[Any]) -> None:
        """
        Eject an event to Purgatory.

        Called by FluxAgent when inner.invoke() returns SemaphoreToken.

        Args:
            token: The SemaphoreToken to store

        Note:
            If a token with the same ID already exists, it will be overwritten.
            This is intentional to support token updates (e.g., deadline changes).
        """
        self._pending[token.id] = token
        if self._memory:
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
        Resolve a pending semaphore with human-provided context.

        Returns ReentryContext to be injected as Perturbation.
        Returns None if token not found or already resolved/cancelled.

        Idempotent: calling twice on same token returns None on second call.

        Args:
            token_id: ID of the token to resolve
            human_input: The context provided by human

        Returns:
            ReentryContext if successfully resolved, None otherwise

        Example:
            >>> reentry = await purgatory.resolve("sem-abc12345", "Approve")
            >>> if reentry:
            ...     perturbation = create_perturbation(reentry, priority=200)
            ...     await flux._perturbation_queue.put(perturbation)
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

        if self._memory:
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
        Cancel a pending semaphore. Event is discarded.

        Returns True if cancelled, False if not found or already resolved/cancelled.

        Cancelled tokens remain in _pending (marked) to preserve audit trail.

        Args:
            token_id: ID of the token to cancel

        Returns:
            True if successfully cancelled, False otherwise
        """
        token = self._pending.get(token_id)
        if token is None:
            return False
        if not token.is_pending:
            return False

        token.cancelled_at = datetime.now()

        if self._memory:
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

    def get(self, token_id: str) -> SemaphoreToken[Any] | None:
        """
        Get a token by ID (any state).

        Args:
            token_id: ID of the token to retrieve

        Returns:
            SemaphoreToken if found, None otherwise
        """
        return self._pending.get(token_id)

    def list_pending(self) -> list[SemaphoreToken[Any]]:
        """
        List all pending (unresolved) semaphores.

        Returns:
            List of tokens that are still awaiting resolution
        """
        return [t for t in self._pending.values() if t.is_pending]

    def list_all(self) -> list[SemaphoreToken[Any]]:
        """
        List all semaphores (any state).

        Returns:
            List of all tokens (pending, resolved, and cancelled)
        """
        return list(self._pending.values())

    async def recover(self) -> list[SemaphoreToken[Any]]:
        """
        Recover pending semaphores after restart.

        Called during FluxAgent initialization (Phase 3).
        For Phase 1, returns empty list (no persistence).

        Returns:
            List of pending tokens recovered from persistence
        """
        if self._memory:
            state = await self._memory.load()
            if state:
                self._pending = state.get("pending", {})
        return self.list_pending()

    def clear(self) -> None:
        """Clear all tokens (for testing)."""
        self._pending.clear()

    async def void_expired(self) -> list[SemaphoreToken[Any]]:
        """
        Void all tokens whose deadlines have passed.

        This is the "default on a promise" operation - tokens that
        weren't resolved in time are marked as voided.

        Returns:
            List of tokens that were voided

        Note:
            Call this periodically or on startup to enforce deadlines.
            Voided tokens remain in _pending for audit trail.
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

        if voided and self._memory:
            await self._persist()

        return voided

    async def _persist(self) -> None:
        """
        Persist state to D-gent (Phase 3).

        For Phase 1/2, this is a no-op placeholder.
        """
        if self._memory:
            await self._memory.save({"pending": self._pending})

    async def _signal(self, signal: str, data: dict[str, Any]) -> None:
        """
        Emit a pheromone signal (best-effort).

        Args:
            signal: Signal name (e.g., "purgatory.ejected")
            data: Signal payload

        Note:
            Failures are silently ignored - pheromones are observability,
            not control flow.
        """
        if self._emit_pheromone is not None:
            try:
                await self._emit_pheromone(signal, data)
            except Exception:
                pass  # Best-effort: failures are ignored
