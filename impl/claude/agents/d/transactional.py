"""
TransactionalDataAgent: ACID transactions for D-gent state.

Provides transactional guarantees for state operations:
- Atomicity: All operations succeed or none do
- Consistency: State always valid between transactions
- Isolation: Concurrent transactions don't interfere
- Durability: Committed changes persist

Enables time-travel debugging via savepoints.
"""

from typing import TypeVar, Generic, List, Optional, Any, Dict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from contextlib import asynccontextmanager
import uuid

from .protocol import DataAgent
from .errors import StateError


class TransactionState(Enum):
    """Transaction lifecycle states."""

    ACTIVE = auto()
    COMMITTED = auto()
    ROLLED_BACK = auto()
    ABORTED = auto()


class TransactionError(StateError):
    """Transaction operation failed."""


class SavepointError(TransactionError):
    """Savepoint operation failed."""


class RollbackError(TransactionError):
    """Rollback operation failed."""


class IsolationViolationError(TransactionError):
    """Isolation level was violated."""


S = TypeVar("S")


@dataclass
class Savepoint(Generic[S]):
    """A named snapshot for rollback."""

    id: str
    name: str
    state: S
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class Transaction(Generic[S]):
    """
    An active transaction context.

    Tracks pending changes and savepoints for atomic operations.
    """

    id: str
    started_at: datetime
    state: TransactionState = TransactionState.ACTIVE
    initial_state: Optional[S] = None
    pending_state: Optional[S] = None
    savepoints: List[Savepoint[S]] = field(default_factory=list)
    operations: List[str] = field(default_factory=list)  # Operation log

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


class TransactionalDataAgent(Generic[S]):
    """
    D-gent with full transactional support.

    Features:
    - ACID transactions: begin/commit/rollback
    - Savepoints: named checkpoints within transactions
    - Time-travel: rollback to any savepoint
    - Operation logging: audit trail of changes
    - Isolation: pending changes invisible until commit

    Example:
        >>> memory = VolatileAgent(_state=0)
        >>> txn_agent = TransactionalDataAgent(memory)
        >>>
        >>> async with txn_agent.transaction() as txn:
        ...     await txn_agent.save(10)
        ...     txn_agent.savepoint("checkpoint1")
        ...     await txn_agent.save(20)
        ...     txn_agent.rollback_to("checkpoint1")
        ...     # State is now 10
        ...     await txn_agent.commit()
        >>>
        >>> state = await txn_agent.load()  # Returns 10
    """

    def __init__(self, underlying: DataAgent[S]):
        """
        Wrap a D-gent with transactional capabilities.

        Args:
            underlying: The D-gent to wrap
        """
        self._underlying = underlying
        self._current_txn: Optional[Transaction[S]] = None
        self._txn_history: List[Transaction[S]] = []

    # === DataAgent Protocol ===

    async def load(self) -> S:
        """
        Load state (pending if in transaction, committed otherwise).
        """
        if self._current_txn and self._current_txn.pending_state is not None:
            return self._current_txn.pending_state
        return await self._underlying.load()

    async def save(self, state: S) -> None:
        """
        Save state (to pending if in transaction, directly otherwise).
        """
        if self._current_txn:
            if self._current_txn.state != TransactionState.ACTIVE:
                raise TransactionError(
                    f"Cannot save in {self._current_txn.state.name} transaction"
                )
            self._current_txn.pending_state = state
            self._current_txn.operations.append(f"save({state})")
        else:
            await self._underlying.save(state)

    async def history(self, limit: int | None = None) -> List[S]:
        """Return historical states from underlying D-gent."""
        return await self._underlying.history(limit)

    # === Transaction Operations ===

    @asynccontextmanager
    async def transaction(self, name: Optional[str] = None):
        """
        Begin a new transaction.

        Usage:
            async with agent.transaction() as txn:
                await agent.save(new_state)
                # auto-commits on success, rollbacks on exception

        Args:
            name: Optional transaction name for debugging
        """
        txn = await self.begin(name)
        try:
            yield txn
            await self.commit()
        except Exception:
            await self.rollback()
            raise

    async def begin(self, name: Optional[str] = None) -> Transaction[S]:
        """
        Begin a new transaction explicitly.

        Returns:
            The new transaction object
        """
        if self._current_txn and self._current_txn.state == TransactionState.ACTIVE:
            raise TransactionError("Nested transactions not supported")

        initial_state = await self._underlying.load()

        self._current_txn = Transaction(
            id=str(uuid.uuid4()),
            started_at=datetime.now(),
            initial_state=initial_state,
            pending_state=initial_state,
            operations=[f"begin(name={name})"] if name else ["begin()"],
        )

        return self._current_txn

    async def commit(self) -> None:
        """
        Commit the current transaction.

        Persists all pending changes to underlying D-gent.
        """
        if not self._current_txn:
            raise TransactionError("No active transaction to commit")

        if self._current_txn.state != TransactionState.ACTIVE:
            raise TransactionError(
                f"Cannot commit {self._current_txn.state.name} transaction"
            )

        # Persist pending state
        if self._current_txn.pending_state is not None:
            await self._underlying.save(self._current_txn.pending_state)

        self._current_txn.state = TransactionState.COMMITTED
        self._current_txn.operations.append("commit()")
        self._txn_history.append(self._current_txn)
        self._current_txn = None

    async def rollback(self) -> None:
        """
        Rollback the entire transaction.

        Discards all pending changes.
        """
        if not self._current_txn:
            raise TransactionError("No active transaction to rollback")

        if self._current_txn.state != TransactionState.ACTIVE:
            raise TransactionError(
                f"Cannot rollback {self._current_txn.state.name} transaction"
            )

        self._current_txn.state = TransactionState.ROLLED_BACK
        self._current_txn.operations.append("rollback()")
        self._txn_history.append(self._current_txn)
        self._current_txn = None

    # === Savepoint Operations (Time-Travel) ===

    def savepoint(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a named savepoint within the current transaction.

        Savepoints enable time-travel debugging: you can rollback
        to any savepoint and explore alternative state paths.

        Args:
            name: Human-readable name for the savepoint
            metadata: Optional metadata (tags, context, reason)

        Returns:
            Savepoint ID for rollback

        Example:
            >>> txn_agent.savepoint("before_risky_operation")
            >>> # ... risky operations ...
            >>> txn_agent.rollback_to("before_risky_operation")
        """
        if not self._current_txn:
            raise SavepointError("No active transaction for savepoint")

        if self._current_txn.state != TransactionState.ACTIVE:
            raise SavepointError(
                f"Cannot create savepoint in {self._current_txn.state.name} transaction"
            )

        sp = Savepoint(
            id=str(uuid.uuid4()),
            name=name,
            state=self._current_txn.pending_state,
            created_at=datetime.now(),
            metadata=metadata or {},
        )

        self._current_txn.savepoints.append(sp)
        self._current_txn.operations.append(f"savepoint({name})")

        return sp.id

    def rollback_to(self, name_or_id: str) -> None:
        """
        Rollback to a named savepoint.

        Time-travel: state reverts to savepoint, but savepoint
        remains for repeated rollbacks (debugging).

        Args:
            name_or_id: Savepoint name or ID
        """
        if not self._current_txn:
            raise RollbackError("No active transaction for rollback")

        if self._current_txn.state != TransactionState.ACTIVE:
            raise RollbackError(
                f"Cannot rollback in {self._current_txn.state.name} transaction"
            )

        # Find savepoint
        sp = None
        for savepoint in self._current_txn.savepoints:
            if savepoint.name == name_or_id or savepoint.id == name_or_id:
                sp = savepoint
                break

        if sp is None:
            raise RollbackError(f"Savepoint not found: {name_or_id}")

        # Restore state
        self._current_txn.pending_state = sp.state
        self._current_txn.operations.append(f"rollback_to({name_or_id})")

    def release_savepoint(self, name_or_id: str) -> None:
        """
        Release (delete) a savepoint.

        Used to clean up savepoints that are no longer needed.
        """
        if not self._current_txn:
            raise SavepointError("No active transaction")

        idx = None
        for i, sp in enumerate(self._current_txn.savepoints):
            if sp.name == name_or_id or sp.id == name_or_id:
                idx = i
                break

        if idx is None:
            raise SavepointError(f"Savepoint not found: {name_or_id}")

        self._current_txn.savepoints.pop(idx)
        self._current_txn.operations.append(f"release_savepoint({name_or_id})")

    def list_savepoints(self) -> List[Savepoint[S]]:
        """List all savepoints in current transaction."""
        if not self._current_txn:
            return []
        return list(self._current_txn.savepoints)

    # === Introspection ===

    @property
    def in_transaction(self) -> bool:
        """Check if a transaction is active."""
        return (
            self._current_txn is not None
            and self._current_txn.state == TransactionState.ACTIVE
        )

    @property
    def current_transaction(self) -> Optional[Transaction[S]]:
        """Get current transaction (if any)."""
        return self._current_txn

    def transaction_log(self) -> List[str]:
        """Get operation log for current transaction."""
        if not self._current_txn:
            return []
        return list(self._current_txn.operations)

    def recent_transactions(self, limit: int = 10) -> List[Transaction[S]]:
        """Get recent completed transactions."""
        return self._txn_history[-limit:]

    # === Time-Travel Debugging ===

    async def debug_at_savepoint(
        self,
        name_or_id: str,
        inspector: Any = None,
    ) -> S:
        """
        Inspect state at a specific savepoint without modifying current state.

        For debugging: peek at historical states.

        Args:
            name_or_id: Savepoint name or ID
            inspector: Optional callback to inspect state

        Returns:
            State at savepoint
        """
        if not self._current_txn:
            raise SavepointError("No active transaction")

        for sp in self._current_txn.savepoints:
            if sp.name == name_or_id or sp.id == name_or_id:
                if inspector:
                    inspector(sp.state, sp.metadata)
                return sp.state

        raise SavepointError(f"Savepoint not found: {name_or_id}")

    def savepoint_diff(
        self,
        from_name: str,
        to_name: str,
    ) -> Dict[str, Any]:
        """
        Compare state between two savepoints.

        Useful for understanding what changed between checkpoints.

        Returns:
            Dict with from_state, to_state, and basic diff info
        """
        if not self._current_txn:
            raise SavepointError("No active transaction")

        from_sp = None
        to_sp = None

        for sp in self._current_txn.savepoints:
            if sp.name == from_name or sp.id == from_name:
                from_sp = sp
            if sp.name == to_name or sp.id == to_name:
                to_sp = sp

        if from_sp is None:
            raise SavepointError(f"From savepoint not found: {from_name}")
        if to_sp is None:
            raise SavepointError(f"To savepoint not found: {to_name}")

        return {
            "from_name": from_sp.name,
            "from_state": from_sp.state,
            "from_time": from_sp.created_at,
            "to_name": to_sp.name,
            "to_state": to_sp.state,
            "to_time": to_sp.created_at,
            "states_equal": from_sp.state == to_sp.state,
        }
