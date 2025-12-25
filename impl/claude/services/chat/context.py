"""
Chat Context: Incremental Context Compression for Chat Sessions.

Implements the WorkingContext functor with LinearityMap tagging for
preservation priorities during compression.

Philosophy:
    "Not all context is equal. Tag for compression priority."

See: spec/protocols/chat-web.md §5.2, §5.4
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any
from uuid import uuid4

if TYPE_CHECKING:
    # Avoid circular import - only import API types for type hints
    from protocols.api.chat import Turn as ApiTurn


def generate_context_id() -> str:
    """Generate unique context ID."""
    return f"ctx-{uuid4().hex[:12]}"


# =============================================================================
# LinearityTag: Preservation Priority
# =============================================================================


class LinearityTag(Enum):
    """
    Linearity map tags for compression priority.

    Tags messages for compression priority during context management.

    See: spec/protocols/chat-web.md §5.4
    """

    REQUIRED = "required"  # Never drop (system prompt, key facts)
    PRESERVED = "preserved"  # Prefer to keep (recent turns, user emphasis)
    DROPPABLE = "droppable"  # Safe to summarize (routine responses)

    @property
    def priority(self) -> int:
        """Numeric priority (higher = more important)."""
        return {
            LinearityTag.REQUIRED: 3,
            LinearityTag.PRESERVED: 2,
            LinearityTag.DROPPABLE: 1,
        }[self]

    @property
    def can_drop(self) -> bool:
        """True if this can be dropped during compression."""
        return self == LinearityTag.DROPPABLE


# =============================================================================
# Turn: Single Conversation Turn
# =============================================================================


@dataclass
class Turn:
    """
    Single conversation turn (service model).

    Represents one complete exchange in the conversation.
    This is the simple service model with string fields for internal operations.
    The API layer uses a richer Turn model with Message objects.

    Conversion:
        - To API: self.to_api_turn()
        - From API: Turn.from_api_turn(api_turn)

    See: protocols.api.chat.Turn
    """

    # Identity
    id: str = field(default_factory=lambda: f"turn-{uuid4().hex[:12]}")
    turn_number: int = 0

    # Content
    user_message: str = ""
    assistant_response: str = ""

    # Metadata
    linearity_tag: LinearityTag = LinearityTag.PRESERVED
    in_context: bool = True  # Whether this turn is in active context
    trailing: bool = False  # Whether this is a trailing (crystallized) turn

    # Provenance
    derived_from: list[str] = field(default_factory=list)  # For summarized turns

    # Temporal
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None

    # Tools used
    tools_used: list[str] = field(default_factory=list)

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def content(self) -> str:
        """Combined content for hashing."""
        return f"{self.user_message}\n{self.assistant_response}"

    @property
    def token_estimate(self) -> int:
        """Rough token estimate (chars / 4)."""
        return len(self.content) // 4

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "turn_number": self.turn_number,
            "user_message": self.user_message,
            "assistant_response": self.assistant_response,
            "linearity_tag": self.linearity_tag.value,
            "in_context": self.in_context,
            "trailing": self.trailing,
            "derived_from": self.derived_from,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "tools_used": self.tools_used,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Turn:
        """Create from dictionary."""
        return cls(
            id=data.get("id", f"turn-{uuid4().hex[:12]}"),
            turn_number=data.get("turn_number", 0),
            user_message=data.get("user_message", ""),
            assistant_response=data.get("assistant_response", ""),
            linearity_tag=LinearityTag(data.get("linearity_tag", "preserved")),
            in_context=data.get("in_context", True),
            trailing=data.get("trailing", False),
            derived_from=data.get("derived_from", []),
            started_at=datetime.fromisoformat(data["started_at"])
            if data.get("started_at")
            else datetime.now(),
            completed_at=datetime.fromisoformat(data["completed_at"])
            if data.get("completed_at")
            else None,
            tools_used=data.get("tools_used", []),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_summary(cls, summary: str, source_turn_ids: list[str]) -> Turn:
        """
        Create a summary turn from multiple source turns.

        Args:
            summary: Summarized content
            source_turn_ids: IDs of turns that were summarized

        Returns:
            Turn with summary content and provenance
        """
        return cls(
            id=f"turn-summary-{uuid4().hex[:12]}",
            turn_number=-1,  # Summary turns don't have turn numbers
            user_message="[Summary of previous turns]",
            assistant_response=summary,
            linearity_tag=LinearityTag.PRESERVED,
            derived_from=source_turn_ids,
            metadata={"is_summary": True, "source_count": len(source_turn_ids)},
        )

    def to_api_turn(self) -> ApiTurn:
        """
        Convert service Turn to API Turn for serialization.

        Creates rich Message objects with role, content, mentions, linearity tags.
        Used at the API boundary when sending to frontend.

        Returns:
            API Turn with Message objects

        See: protocols.api.chat.Turn
        """
        from protocols.api.chat import EvidenceDelta, Message, Turn as ApiTurn

        user_message = Message(
            role="user",
            content=self.user_message,
            mentions=[],  # Service layer doesn't track mentions yet
            linearity_tag=self.linearity_tag.value,
        )

        assistant_message = Message(
            role="assistant",
            content=self.assistant_response,
            mentions=[],
            linearity_tag=self.linearity_tag.value,
        )

        # Create evidence delta (service Turn doesn't track this yet)
        evidence_delta = EvidenceDelta(
            tools_executed=len(self.tools_used),
            tools_succeeded=len(self.tools_used),  # Assume success for now
            confidence_change=0.0,
        )

        from protocols.api.chat import ToolUse

        # Convert tool names to minimal ToolUse objects
        tools_used = [
            ToolUse(
                name=tool_name,
                input={},
                output=None,
                success=True,  # Assume success if in tools_used
                duration_ms=0.0,
            )
            for tool_name in self.tools_used
        ]

        return ApiTurn(
            turn_number=self.turn_number,
            user_message=user_message,
            assistant_response=assistant_message,
            tools_used=tools_used,
            evidence_delta=evidence_delta,
            confidence=self.metadata.get("confidence", 0.8),
            started_at=self.started_at.isoformat(),
            completed_at=self.completed_at.isoformat() if self.completed_at else datetime.now().isoformat(),
        )

    @classmethod
    def from_api_turn(cls, api_turn: ApiTurn) -> Turn:
        """
        Convert API Turn to service Turn for internal operations.

        Extracts content from Message objects into simple strings.
        Used at the API boundary when receiving from frontend.

        Args:
            api_turn: API Turn with Message objects

        Returns:
            Service Turn with string fields

        See: protocols.api.chat.Turn
        """
        return cls(
            turn_number=api_turn.turn_number,
            user_message=api_turn.user_message.content,
            assistant_response=api_turn.assistant_response.content,
            linearity_tag=LinearityTag(api_turn.user_message.linearity_tag),
            tools_used=[tool.name for tool in api_turn.tools_used] if api_turn.tools_used else [],
            started_at=datetime.fromisoformat(api_turn.started_at),
            completed_at=datetime.fromisoformat(api_turn.completed_at),
            metadata={"confidence": api_turn.confidence},
        )


# =============================================================================
# WorkingContext: Compressed Context Window
# =============================================================================


@dataclass
class WorkingContext:
    """
    Working context for chat session.

    Represents the active context window with compression applied.
    Uses incremental summarization to maintain recent turns verbatim.

    Philosophy:
        Always keep recent turns verbatim. Only compress distant past.

    See: spec/protocols/chat-web.md §5.2
    """

    # Identity
    id: str = field(default_factory=generate_context_id)

    # Turns
    turns: list[Turn] = field(default_factory=list)

    # Context metrics
    context_window: int = 200_000  # Claude Opus 4.5 context
    compress_at: float = 0.80  # Start compression at 80%
    resume_at: float = 0.70  # Resume normal at 70%

    # Compression state
    is_compressing: bool = False
    last_compression: datetime | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def token_count(self) -> int:
        """Current token count estimate."""
        return sum(turn.token_estimate for turn in self.turns)

    @property
    def context_usage(self) -> float:
        """Context usage as fraction [0, 1]."""
        return self.token_count / self.context_window

    @property
    def should_compress(self) -> bool:
        """True if compression threshold reached."""
        if self.is_compressing:
            # Continue compressing until resume threshold
            return self.context_usage > self.resume_at
        else:
            # Start compressing at compress threshold
            return self.context_usage >= self.compress_at

    @property
    def turn_ids(self) -> list[str]:
        """List of turn IDs in context."""
        return [t.id for t in self.turns]

    def compress(self, tolerance: float = 0.05) -> WorkingContext:
        """
        Compress context using incremental summarization.

        Keeps REQUIRED turns, recent PRESERVED turns, and summarizes
        old PRESERVED + DROPPABLE turns.

        Args:
            tolerance: Semantic loss tolerance

        Returns:
            New WorkingContext with compression applied

        See: spec/protocols/chat-web.md §5.2
        """
        # Separate turns by priority
        required = [t for t in self.turns if t.linearity_tag == LinearityTag.REQUIRED]
        preserved = [t for t in self.turns if t.linearity_tag == LinearityTag.PRESERVED]
        droppable = [t for t in self.turns if t.linearity_tag == LinearityTag.DROPPABLE]

        # Always keep required
        compressed = required.copy()

        # Keep recent preserved (last 5 turns)
        compressed.extend(preserved[-5:])

        # Summarize old preserved + droppable
        old_turns = preserved[:-5] + droppable
        if old_turns:
            # TODO: Use LLM to generate summary
            summary_text = f"[Summary of {len(old_turns)} previous turns]"
            summary_turn = Turn.from_summary(
                summary=summary_text, source_turn_ids=[t.id for t in old_turns]
            )
            compressed.append(summary_turn)

        return WorkingContext(
            id=generate_context_id(),
            turns=compressed,
            context_window=self.context_window,
            compress_at=self.compress_at,
            resume_at=self.resume_at,
            is_compressing=True,
            last_compression=datetime.now(),
            metadata={**self.metadata, "compression_applied": True},
        )

    @classmethod
    def expand(cls, compressed: WorkingContext) -> WorkingContext:
        """
        Expand compressed context (partial inverse of compress).

        Note: This is a partial inverse - we can't fully reconstruct
        summarized content.

        Args:
            compressed: Compressed context

        Returns:
            WorkingContext with expansion applied
        """
        # For now, just return the compressed context
        # Full expansion would require fetching original turns from storage
        return compressed

    def content_hash_prefix(self) -> str:
        """
        Compute content hash prefix for naturality checking.

        Used in Galois connection tests.
        """
        content = "|".join(t.content for t in self.turns)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "turns": [t.to_dict() for t in self.turns],
            "context_window": self.context_window,
            "compress_at": self.compress_at,
            "resume_at": self.resume_at,
            "is_compressing": self.is_compressing,
            "last_compression": self.last_compression.isoformat()
            if self.last_compression
            else None,
            "token_count": self.token_count,
            "context_usage": self.context_usage,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkingContext:
        """Create from dictionary."""
        return cls(
            id=data.get("id", generate_context_id()),
            turns=[Turn.from_dict(t) for t in data.get("turns", [])],
            context_window=data.get("context_window", 200_000),
            compress_at=data.get("compress_at", 0.80),
            resume_at=data.get("resume_at", 0.70),
            is_compressing=data.get("is_compressing", False),
            last_compression=datetime.fromisoformat(data["last_compression"])
            if data.get("last_compression")
            else None,
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "LinearityTag",
    "Turn",
    "WorkingContext",
    "generate_context_id",
]
