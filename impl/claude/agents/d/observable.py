"""
ObservableDataAgent: Reactive subscriptions and change notifications.

Provides reactive patterns for state changes:
- Subscribe to all changes
- Subscribe to specific paths
- Debounced notifications
- Change diffing

Enables reactive UI updates and inter-agent communication.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
)

from .errors import StateError
from .protocol import DataAgent


class ObservableError(StateError):
    """Observable operation failed."""


class SubscriptionError(ObservableError):
    """Subscription operation failed."""


S = TypeVar("S")


class ChangeType(Enum):
    """Type of state change."""

    SET = auto()  # Full state replacement
    UPDATE = auto()  # Partial update
    DELETE = auto()  # Path deleted


@dataclass
class Change(Generic[S]):
    """A recorded state change."""

    id: str
    change_type: ChangeType
    path: Optional[str]  # None = root state
    old_value: Any
    new_value: Any
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Subscription:
    """A subscription to state changes."""

    id: str
    path: Optional[str]  # None = all changes
    callback: Callable[[Change], Awaitable[None]]
    debounce_ms: int = 0
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    # Internal state for debouncing
    _pending_changes: List[Change] = field(default_factory=list)
    _debounce_task: Optional[asyncio.Task] = None


class ObservableDataAgent(Generic[S]):
    """
    D-gent with reactive change notifications.

    Features:
    - subscribe(): Register for change notifications
    - subscribe_path(): Subscribe to specific paths
    - batch(): Batch multiple changes into one notification
    - diff(): Compute differences between states
    - replay_changes(): Re-emit historical changes

    Example:
        >>> memory = VolatileAgent(_state={"count": 0})
        >>> obs = ObservableDataAgent(memory)
        >>>
        >>> async def on_change(change):
        ...     print(f"Changed: {change.old_value} -> {change.new_value}")
        >>>
        >>> sub_id = await obs.subscribe(on_change)
        >>> await obs.save({"count": 1})  # Prints: Changed: {'count': 0} -> {'count': 1}
        >>> await obs.unsubscribe(sub_id)
    """

    def __init__(
        self,
        underlying: DataAgent[S],
        max_history: int = 100,
    ):
        """
        Wrap a D-gent with observability.

        Args:
            underlying: The D-gent to wrap
            max_history: Maximum change history to retain
        """
        self._underlying = underlying
        self._max_history = max_history

        self._subscriptions: Dict[str, Subscription] = {}
        self._change_history: List[Change[S]] = []
        self._batch_mode = False
        self._batched_changes: List[Change[S]] = []
        self._last_state: Optional[S] = None

    # === DataAgent Protocol ===

    async def load(self) -> S:
        """Load current state."""
        state = await self._underlying.load()
        self._last_state = state
        return state

    async def save(self, state: S) -> None:
        """Save state and notify subscribers."""
        old_state = self._last_state

        await self._underlying.save(state)
        self._last_state = state

        change = Change(
            id=str(uuid.uuid4()),
            change_type=ChangeType.SET,
            path=None,
            old_value=old_state,
            new_value=state,
            timestamp=datetime.now(),
        )

        await self._record_and_notify(change)

    async def history(self, limit: int | None = None) -> List[S]:
        """Get state history."""
        return await self._underlying.history(limit)

    # === Subscription Operations ===

    async def subscribe(
        self,
        callback: Callable[[Change], Awaitable[None]],
        debounce_ms: int = 0,
    ) -> str:
        """
        Subscribe to all state changes.

        Args:
            callback: Async function called on each change
            debounce_ms: Debounce window (0 = immediate)

        Returns:
            Subscription ID for unsubscribing
        """
        sub_id = str(uuid.uuid4())
        self._subscriptions[sub_id] = Subscription(
            id=sub_id,
            path=None,
            callback=callback,
            debounce_ms=debounce_ms,
        )
        return sub_id

    async def subscribe_path(
        self,
        path: str,
        callback: Callable[[Change], Awaitable[None]],
        debounce_ms: int = 0,
    ) -> str:
        """
        Subscribe to changes at a specific path.

        Args:
            path: Dot-notation path to watch
            callback: Async function called on changes
            debounce_ms: Debounce window

        Returns:
            Subscription ID
        """
        sub_id = str(uuid.uuid4())
        self._subscriptions[sub_id] = Subscription(
            id=sub_id,
            path=path,
            callback=callback,
            debounce_ms=debounce_ms,
        )
        return sub_id

    async def unsubscribe(self, sub_id: str) -> bool:
        """
        Remove a subscription.

        Returns:
            True if subscription was found and removed
        """
        if sub_id in self._subscriptions:
            sub = self._subscriptions.pop(sub_id)
            sub.active = False
            if sub._debounce_task:
                sub._debounce_task.cancel()
            return True
        return False

    def subscription_count(self) -> int:
        """Get number of active subscriptions."""
        return len(self._subscriptions)

    def list_subscriptions(self) -> List[Dict[str, Any]]:
        """List all active subscriptions."""
        return [
            {
                "id": s.id,
                "path": s.path,
                "debounce_ms": s.debounce_ms,
                "active": s.active,
                "created_at": s.created_at.isoformat(),
            }
            for s in self._subscriptions.values()
        ]

    # === Batch Operations ===

    async def batch_start(self) -> None:
        """
        Start batching changes.

        Changes are collected but not notified until batch_end().
        """
        self._batch_mode = True
        self._batched_changes = []

    async def batch_end(self) -> None:
        """
        End batch and notify subscribers of all changes.
        """
        if not self._batch_mode:
            return

        self._batch_mode = False

        # Notify with batched changes
        for change in self._batched_changes:
            await self._notify_subscribers(change)

        self._batched_changes = []

    async def batch_cancel(self) -> None:
        """Cancel batch without notifying."""
        self._batch_mode = False
        self._batched_changes = []

    # === Path-Based Updates ===

    async def update_path(
        self,
        path: str,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Update a specific path in state.

        Creates a targeted change notification.
        """
        state = await self._underlying.load()

        if not isinstance(state, dict):
            raise ObservableError("update_path only works on dict states")

        # Extract old value
        old_value = self._get_path(state, path)

        # Update path
        new_state = self._set_path(dict(state), path, value)
        await self._underlying.save(new_state)
        self._last_state = new_state

        change = Change(
            id=str(uuid.uuid4()),
            change_type=ChangeType.UPDATE,
            path=path,
            old_value=old_value,
            new_value=value,
            timestamp=datetime.now(),
            metadata=metadata or {},
        )

        await self._record_and_notify(change)

    async def delete_path(self, path: str) -> None:
        """Delete a path from state."""
        state = await self._underlying.load()

        if not isinstance(state, dict):
            raise ObservableError("delete_path only works on dict states")

        old_value = self._get_path(state, path)

        # Delete path
        new_state = self._delete_path(dict(state), path)
        await self._underlying.save(new_state)
        self._last_state = new_state

        change = Change(
            id=str(uuid.uuid4()),
            change_type=ChangeType.DELETE,
            path=path,
            old_value=old_value,
            new_value=None,
            timestamp=datetime.now(),
        )

        await self._record_and_notify(change)

    # === Change History ===

    def change_history(self, limit: Optional[int] = None) -> List[Change[S]]:
        """Get recent change history."""
        changes = list(self._change_history)
        changes.reverse()
        return changes[:limit] if limit else changes

    def changes_since(self, timestamp: datetime) -> List[Change[S]]:
        """Get changes since timestamp."""
        return [c for c in self._change_history if c.timestamp >= timestamp]

    def changes_at_path(
        self, path: str, limit: Optional[int] = None
    ) -> List[Change[S]]:
        """Get changes at a specific path."""
        changes = [
            c
            for c in self._change_history
            if c.path == path or (c.path and c.path.startswith(path + "."))
        ]
        changes.reverse()
        return changes[:limit] if limit else changes

    async def replay_changes(
        self,
        changes: List[Change[S]],
        to_subscriber: Optional[str] = None,
    ) -> None:
        """
        Replay historical changes to subscribers.

        Args:
            changes: Changes to replay
            to_subscriber: Specific subscriber ID (None = all)
        """
        for change in changes:
            if to_subscriber:
                if to_subscriber in self._subscriptions:
                    sub = self._subscriptions[to_subscriber]
                    await sub.callback(change)
            else:
                await self._notify_subscribers(change)

    # === Diffing ===

    def diff(self, old_state: S, new_state: S) -> List[Dict[str, Any]]:
        """
        Compute differences between two states.

        Returns list of changes in format:
            {"path": "...", "type": "add|remove|change", "old": ..., "new": ...}
        """
        return self._compute_diff(old_state, new_state, "")

    # === Internal Methods ===

    async def _record_and_notify(self, change: Change[S]) -> None:
        """Record change and notify subscribers."""
        # Record
        self._change_history.append(change)
        if len(self._change_history) > self._max_history:
            self._change_history = self._change_history[-self._max_history :]

        # Batch or notify
        if self._batch_mode:
            self._batched_changes.append(change)
        else:
            await self._notify_subscribers(change)

    async def _notify_subscribers(self, change: Change[S]) -> None:
        """Notify relevant subscribers of a change."""
        for sub in list(self._subscriptions.values()):
            if not sub.active:
                continue

            # Check path match
            if sub.path is not None:
                if change.path is None:
                    # Full state change - check if sub.path was affected
                    pass  # Always notify on full state change
                elif not (
                    change.path == sub.path
                    or change.path.startswith(sub.path + ".")
                    or sub.path.startswith(change.path + ".")
                ):
                    continue

            # Debounce or notify immediately
            if sub.debounce_ms > 0:
                await self._debounced_notify(sub, change)
            else:
                try:
                    await sub.callback(change)
                except Exception:
                    pass  # Don't let subscriber errors break the agent

    async def _debounced_notify(self, sub: Subscription, change: Change[S]) -> None:
        """Debounce notifications for a subscription."""
        sub._pending_changes.append(change)

        # Cancel existing debounce task
        if sub._debounce_task and not sub._debounce_task.done():
            sub._debounce_task.cancel()

        # Create new debounce task
        async def flush():
            await asyncio.sleep(sub.debounce_ms / 1000)
            if sub.active and sub._pending_changes:
                # Notify with most recent change
                latest = sub._pending_changes[-1]
                sub._pending_changes = []
                try:
                    await sub.callback(latest)
                except Exception:
                    pass

        sub._debounce_task = asyncio.create_task(flush())

    def _get_path(self, data: Any, path: str) -> Any:
        """Get value at path."""
        if not path:
            return data

        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return None
        return current

    def _set_path(self, data: Dict, path: str, value: Any) -> Dict:
        """Set value at path (immutable)."""
        if not path:
            return value

        parts = path.split(".")
        result = dict(data)
        current = result

        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            else:
                current[part] = dict(current[part])
            current = current[part]

        current[parts[-1]] = value
        return result

    def _delete_path(self, data: Dict, path: str) -> Dict:
        """Delete value at path (immutable)."""
        if not path:
            return {}

        parts = path.split(".")
        result = dict(data)
        current = result

        for part in parts[:-1]:
            if part not in current:
                return result  # Path doesn't exist
            current[part] = dict(current[part])
            current = current[part]

        if parts[-1] in current:
            del current[parts[-1]]

        return result

    def _compute_diff(
        self,
        old: Any,
        new: Any,
        path: str,
    ) -> List[Dict[str, Any]]:
        """Recursively compute diff between two values."""
        diffs = []

        if type(old) is not type(new):
            diffs.append(
                {
                    "path": path or ".",
                    "type": "change",
                    "old": old,
                    "new": new,
                }
            )
        elif isinstance(old, dict):
            # Check for removed keys
            for key in old:
                if key not in new:
                    diffs.append(
                        {
                            "path": f"{path}.{key}" if path else key,
                            "type": "remove",
                            "old": old[key],
                            "new": None,
                        }
                    )

            # Check for added/changed keys
            for key in new:
                child_path = f"{path}.{key}" if path else key
                if key not in old:
                    diffs.append(
                        {
                            "path": child_path,
                            "type": "add",
                            "old": None,
                            "new": new[key],
                        }
                    )
                elif old[key] != new[key]:
                    if isinstance(old[key], dict) and isinstance(new[key], dict):
                        diffs.extend(self._compute_diff(old[key], new[key], child_path))
                    else:
                        diffs.append(
                            {
                                "path": child_path,
                                "type": "change",
                                "old": old[key],
                                "new": new[key],
                            }
                        )
        elif isinstance(old, list):
            # Simple list comparison
            if old != new:
                diffs.append(
                    {
                        "path": path or ".",
                        "type": "change",
                        "old": old,
                        "new": new,
                    }
                )
        elif old != new:
            diffs.append(
                {
                    "path": path or ".",
                    "type": "change",
                    "old": old,
                    "new": new,
                }
            )

        return diffs


# === Convenience Functions ===


def on_change(
    observable: ObservableDataAgent,
    callback: Callable[[Change], Awaitable[None]],
) -> Callable[[], Awaitable[None]]:
    """
    Convenience decorator for subscribing to changes.

    Returns an unsubscribe function.
    """
    sub_id = None

    async def subscribe():
        nonlocal sub_id
        sub_id = await observable.subscribe(callback)

    async def unsubscribe():
        if sub_id:
            await observable.unsubscribe(sub_id)

    # Auto-subscribe
    asyncio.create_task(subscribe())

    return unsubscribe
