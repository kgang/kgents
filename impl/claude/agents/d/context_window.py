"""
ContextWindow: Turn-level Store Comonad for agent context management.

The context window is a comonad that tracks conversation turns with:
- Resource linearity (what can be dropped, what must be preserved)
- Position-based focus (current turn vs history)
- Comonadic operations (extract, extend, duplicate)

Store Comonad Structure: (S -> A, S)
    S = Position (index in turn history)
    A = Turn (message with linearity metadata)
    S -> A = Peek function (access any historical turn)

Comonad Laws:
1. Left Identity:  extract . duplicate = id
2. Right Identity: fmap extract . duplicate = id
3. Associativity:  duplicate . duplicate = fmap duplicate . duplicate

AGENTESE: self.stream.*
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Callable, Generic, TypeVar

from .linearity import (
    LinearityMap,
    ResourceClass,
    classify_by_content,
    classify_by_role,
)

A = TypeVar("A")
B = TypeVar("B")


class TurnRole(str, Enum):
    """Role of a conversation turn."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass(frozen=True)
class Turn:
    """
    A single conversation turn with linearity metadata.

    Immutable to preserve comonad law compliance.
    """

    role: TurnRole
    content: str
    timestamp: datetime
    resource_id: str  # Reference to LinearityMap entry
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def token_estimate(self) -> int:
        """Rough token count estimate (4 chars per token heuristic)."""
        return len(self.content) // 4 + 1


@dataclass
class ContextMeta:
    """
    Metadata about the context window's state.

    Tracks token pressure, compression state, and linearity stats.
    """

    total_tokens: int = 0
    max_tokens: int = 100_000
    compression_count: int = 0
    last_compression: datetime | None = None

    @property
    def pressure(self) -> float:
        """Context pressure: ratio of used tokens to max."""
        if self.max_tokens == 0:
            return 0.0
        return min(1.0, self.total_tokens / self.max_tokens)

    @property
    def needs_compression(self) -> bool:
        """True if pressure exceeds 70% threshold."""
        return self.pressure > 0.7


@dataclass
class ContextSnapshot(Generic[A]):
    """
    A snapshot of the context at a particular position.

    Used by duplicate() to provide nested context views.
    """

    value: A
    position: int
    timestamp: datetime | None
    linearity_map: LinearityMap


@dataclass
class ContextWindow:
    """
    Store Comonad for agent context management.

    The context window maintains a history of conversation turns with
    resource linearity tracking. It provides comonadic operations for
    context-aware computation.

    Example:
        # Create window
        window = ContextWindow(max_tokens=8000)

        # Add turns
        window.append(TurnRole.USER, "What is 2+2?")
        window.append(TurnRole.ASSISTANT, "2+2 equals 4.")

        # Get current focus
        current = window.extract()  # Returns the assistant turn

        # Compute at each position
        def turn_length(w: ContextWindow) -> int:
            return len(w.extract().content)
        lengths = window.extend(turn_length)  # [14, 12]

        # Get nested views
        snapshots = window.duplicate()  # List of ContextSnapshot

    AGENTESE Operations:
        self.stream.focus   -> extract()
        self.stream.map     -> extend()
        self.stream.seek    -> seek()
        self.stream.project -> ContextProjector.compress()
    """

    max_tokens: int = 100_000

    # Turn history
    _turns: list[Turn] = field(default_factory=list)
    _position: int = 0  # Current focus (usually points to most recent)

    # Resource tracking
    _linearity: LinearityMap = field(default_factory=LinearityMap)

    # Context metadata
    _meta: ContextMeta = field(default_factory=ContextMeta)

    def __post_init__(self) -> None:
        """Initialize metadata with max_tokens."""
        self._meta.max_tokens = self.max_tokens

    # === Comonad Operations ===

    def extract(self) -> Turn | None:
        """
        W a -> a

        Extract the current focus (turn at position).
        Returns None if context is empty.
        """
        if not self._turns or self._position <= 0:
            return None
        # Position 1 = first turn, etc.
        idx = min(self._position, len(self._turns)) - 1
        return self._turns[idx] if 0 <= idx < len(self._turns) else None

    def extend(self, f: Callable[["ContextWindow"], B]) -> list[B]:
        """
        (W a -> b) -> W a -> W b

        Apply function f at each position in history.

        The function receives the full context window positioned at
        each historical point, enabling context-aware computation.

        Example:
            def summarize_at_position(w: ContextWindow) -> str:
                turn = w.extract()
                return f"Turn {w.position}: {turn.role.value}" if turn else "empty"
            summaries = window.extend(summarize_at_position)
        """
        results: list[B] = []
        original_position = self._position

        # Apply f at each position (including position 0 which gives None)
        for pos in range(len(self._turns) + 1):
            self._position = pos
            results.append(f(self))

        self._position = original_position
        return results

    def duplicate(self) -> list[ContextSnapshot[Turn | None]]:
        """
        W a -> W (W a)

        Create nested structure showing context at each position.

        Returns snapshots that preserve the full context state at
        each point in history, enabling "time travel" debugging.
        """
        snapshots: list[ContextSnapshot[Turn | None]] = []
        original_position = self._position

        for pos in range(len(self._turns) + 1):
            self._position = pos
            turn = self.extract()
            ts = turn.timestamp if turn else None

            snapshots.append(
                ContextSnapshot(
                    value=turn,
                    position=pos,
                    timestamp=ts,
                    linearity_map=self._linearity,  # Shared reference
                )
            )

        self._position = original_position
        return snapshots

    # === Store-specific Operations ===

    def seek(self, new_position: int) -> "ContextWindow":
        """
        Move focus to a specific position.

        Returns self for chaining.
        """
        self._position = max(0, min(new_position, len(self._turns)))
        return self

    def seeks(self, f: Callable[[int], int]) -> "ContextWindow":
        """
        Move focus by applying a function to current position.

        Example:
            window.seeks(lambda p: p - 1)  # Move back one turn
        """
        new_pos = f(self._position)
        return self.seek(new_pos)

    @property
    def position(self) -> int:
        """Current position in history."""
        return self._position

    # === Turn Operations ===

    def append(
        self,
        role: TurnRole | str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> Turn:
        """
        Append a new turn to the context.

        Automatically classifies the turn's resource class based on
        role and content heuristics.
        """
        if isinstance(role, str):
            role = TurnRole(role.lower())

        # Classify the turn
        role_class = classify_by_role(role.value)
        content_class = classify_by_content(content)
        resource_class = max(role_class, content_class)  # Higher wins

        # Create resource entry
        resource_id = self._linearity.tag(
            content,
            resource_class,
            provenance=f"turn_{role.value}",
            rationale=f"auto-classified from {role.value} message",
        )

        turn = Turn(
            role=role,
            content=content,
            timestamp=datetime.now(UTC),
            resource_id=resource_id,
            metadata=metadata or {},
        )

        self._turns.append(turn)
        self._position = len(self._turns)  # Focus on newest

        # Update token count
        self._meta.total_tokens += turn.token_estimate

        return turn

    def append_turn(self, turn: Turn) -> Turn:
        """Append a pre-constructed turn."""
        self._turns.append(turn)
        self._position = len(self._turns)
        self._meta.total_tokens += turn.token_estimate
        return turn

    # === Query Operations ===

    def all_turns(self) -> list[Turn]:
        """Get all turns in history."""
        return list(self._turns)

    def turns_up_to(self, position: int | None = None) -> list[Turn]:
        """Get turns up to a position (defaults to current)."""
        pos = position if position is not None else self._position
        return list(self._turns[:pos])

    def turns_from_role(self, role: TurnRole) -> list[Turn]:
        """Get all turns from a specific role."""
        return [t for t in self._turns if t.role == role]

    def droppable_turns(self) -> list[Turn]:
        """Get turns that can be safely dropped."""
        return [
            t
            for t in self._turns
            if self._linearity.get_class(t.resource_id) == ResourceClass.DROPPABLE
        ]

    def preserved_turns(self) -> list[Turn]:
        """Get turns that must be preserved verbatim."""
        return [
            t
            for t in self._turns
            if self._linearity.get_class(t.resource_id) == ResourceClass.PRESERVED
        ]

    def required_turns(self) -> list[Turn]:
        """Get turns that must flow to output."""
        return [
            t
            for t in self._turns
            if self._linearity.get_class(t.resource_id) == ResourceClass.REQUIRED
        ]

    # === Linearity Operations ===

    def promote_turn(
        self,
        turn: Turn,
        new_class: ResourceClass,
        rationale: str,
    ) -> bool:
        """Promote a turn to a higher resource class."""
        return self._linearity.promote(turn.resource_id, new_class, rationale)

    def get_resource_class(self, turn: Turn) -> ResourceClass | None:
        """Get the resource class of a turn."""
        return self._linearity.get_class(turn.resource_id)

    @property
    def linearity_stats(self) -> dict[str, int]:
        """Get linearity statistics."""
        return self._linearity.count()

    @property
    def linearity_map(self) -> LinearityMap:
        """Access the underlying linearity map."""
        return self._linearity

    # === Pressure & Compression ===

    @property
    def meta(self) -> ContextMeta:
        """Access context metadata."""
        return self._meta

    @property
    def pressure(self) -> float:
        """Current context pressure."""
        return self._meta.pressure

    @property
    def needs_compression(self) -> bool:
        """True if context needs compression."""
        return self._meta.needs_compression

    @property
    def total_tokens(self) -> int:
        """Total estimated tokens."""
        return self._meta.total_tokens

    def recalculate_tokens(self) -> int:
        """Recalculate total tokens from turns."""
        self._meta.total_tokens = sum(t.token_estimate for t in self._turns)
        return self._meta.total_tokens

    # === Serialization ===

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for persistence."""
        return {
            "max_tokens": self.max_tokens,
            "position": self._position,
            "turns": [
                {
                    "role": t.role.value,
                    "content": t.content,
                    "timestamp": t.timestamp.isoformat(),
                    "resource_id": t.resource_id,
                    "metadata": t.metadata,
                }
                for t in self._turns
            ],
            "linearity": self._linearity.to_dict(),
            "meta": {
                "total_tokens": self._meta.total_tokens,
                "max_tokens": self._meta.max_tokens,
                "compression_count": self._meta.compression_count,
                "last_compression": (
                    self._meta.last_compression.isoformat()
                    if self._meta.last_compression
                    else None
                ),
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContextWindow":
        """Deserialize from dict."""
        window = cls(max_tokens=data.get("max_tokens", 100_000))

        # Restore linearity map first
        window._linearity = LinearityMap.from_dict(data.get("linearity", {}))

        # Restore turns
        for t in data.get("turns", []):
            turn = Turn(
                role=TurnRole(t["role"]),
                content=t["content"],
                timestamp=datetime.fromisoformat(t["timestamp"]),
                resource_id=t["resource_id"],
                metadata=t.get("metadata", {}),
            )
            window._turns.append(turn)

        window._position = data.get("position", len(window._turns))

        # Restore metadata
        meta = data.get("meta", {})
        window._meta.total_tokens = meta.get("total_tokens", 0)
        window._meta.compression_count = meta.get("compression_count", 0)
        if meta.get("last_compression"):
            window._meta.last_compression = datetime.fromisoformat(
                meta["last_compression"]
            )

        return window

    # === Comonad Law Helpers ===

    def __len__(self) -> int:
        """Number of turns."""
        return len(self._turns)

    def __bool__(self) -> bool:
        """True if context has any turns."""
        return len(self._turns) > 0


# === Factory Functions ===


def create_context_window(
    max_tokens: int = 100_000,
    initial_system: str | None = None,
) -> ContextWindow:
    """
    Create a new context window with optional system prompt.

    Args:
        max_tokens: Maximum token budget
        initial_system: Optional system message to prepend

    Returns:
        Configured ContextWindow
    """
    window = ContextWindow(max_tokens=max_tokens)

    if initial_system:
        # System messages are REQUIRED by default
        window.append(TurnRole.SYSTEM, initial_system)
        # Promote to PRESERVED since it's the root context
        if window._turns:
            window.promote_turn(
                window._turns[0],
                ResourceClass.PRESERVED,
                "system prompt - root context",
            )

    return window


def from_messages(
    messages: list[dict[str, str]],
    max_tokens: int = 100_000,
) -> ContextWindow:
    """
    Create a context window from a list of messages.

    Each message should have 'role' and 'content' keys.
    """
    window = ContextWindow(max_tokens=max_tokens)

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        window.append(role, content)

    return window
