"""
Chat PolicyTrace (Witness Walk) Integration.

Every chat turn creates a witnessed ChatMark in a PolicyTrace.

Philosophy:
    "The proof IS the decision. The mark IS the witness."

    Every chat turn is a state transition:
    - state_before: user message + context
    - action: assistant response generation
    - state_after: assistant response + updated context

    The ChatPolicyTrace is the complete conversation witness trail.

Integration Points:
    - ChatSession uses ChatPolicyTrace to record all turns
    - Each turn creates a ChatMark with constitutional scores
    - Traces can be persisted for session replay
    - Evidence snapshot captures context at turn time

See: spec/protocols/witness-primitives.md
See: services/categorical/dp_bridge.py (PolicyTrace pattern)
See: services/witness/mark.py (Mark pattern)

Teaching:
    gotcha: ChatMark mimics Mark but is chat-specific. We don't inherit
            from Mark because chat has different fields (user_message,
            assistant_response) than generic stimulus/response.
            (Evidence: This file's design)

    gotcha: constitutional_scores is optional. Early implementation may
            not compute scores for every turn (performance consideration).
            Defaults to None, can be added later.
            (Evidence: ChatMark.constitutional_scores field)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from services.categorical.dp_bridge import PrincipleScore

# =============================================================================
# ChatMark: Witness for a Single Chat Turn
# =============================================================================


@dataclass(frozen=True)
class ChatMark:
    """
    Witness mark for a chat turn.

    Records:
    - WHAT was said (user + assistant messages)
    - WHEN it was said (timestamp)
    - HOW it was generated (tools used)
    - WHY it was generated (reasoning)
    - HOW WELL it aligned with principles (constitutional scores)
    - WHAT the context was (evidence snapshot)

    Example:
        >>> mark = ChatMark(
        ...     session_id="sess-abc",
        ...     turn_number=1,
        ...     user_message="Hello",
        ...     assistant_response="Hi there!",
        ...     reasoning="Friendly greeting",
        ... )
    """

    session_id: str
    turn_number: int
    user_message: str
    assistant_response: str
    tools_used: tuple[str, ...] = ()
    constitutional_scores: PrincipleScore | None = None  # Optional for now
    evidence_snapshot: dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""  # Why this response was generated
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def summary(self) -> str:
        """One-line summary of this turn."""
        user_preview = self.user_message[:40] + "..." if len(self.user_message) > 40 else self.user_message
        assistant_preview = self.assistant_response[:40] + "..." if len(self.assistant_response) > 40 else self.assistant_response
        return f"Turn {self.turn_number}: '{user_preview}' -> '{assistant_preview}'"

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize to dictionary.

        Used for persistence and API serialization.
        """
        return {
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "user_message": self.user_message,
            "assistant_response": self.assistant_response,
            "tools_used": list(self.tools_used),
            "constitutional_scores": (
                self.constitutional_scores.to_dict()
                if self.constitutional_scores and hasattr(self.constitutional_scores, "to_dict")
                else None
            ),
            "evidence_snapshot": self.evidence_snapshot,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChatMark:
        """
        Deserialize from dictionary.

        Note: constitutional_scores reconstruction is deferred because we'd
        need to import PrincipleScore. For now, we store as dict and let
        the caller reconstruct if needed.
        """
        return cls(
            session_id=data["session_id"],
            turn_number=data["turn_number"],
            user_message=data["user_message"],
            assistant_response=data["assistant_response"],
            tools_used=tuple(data.get("tools_used", [])),
            constitutional_scores=None,  # TODO: Reconstruct from dict if needed
            evidence_snapshot=data.get("evidence_snapshot", {}),
            reasoning=data.get("reasoning", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


# =============================================================================
# ChatPolicyTrace: PolicyTrace for Chat Sessions
# =============================================================================


@dataclass(frozen=True)
class ChatPolicyTrace:
    """
    PolicyTrace for a chat session.

    Maintains the complete witness trail for a conversation:
    - All turns in chronological order
    - Constitutional scores per turn (if available)
    - Evidence snapshots for context replay

    This is chat's view of the Writer monad pattern from dp_bridge.PolicyTrace.
    The log is append-only and immutable.

    Example:
        >>> trace = ChatPolicyTrace(session_id="sess-abc")
        >>> mark1 = ChatMark(session_id="sess-abc", turn_number=1, ...)
        >>> trace2 = trace.add_mark(mark1)
        >>> len(trace2.marks)  # 1
    """

    session_id: str
    marks: tuple[ChatMark, ...] = ()

    def add_mark(self, mark: ChatMark) -> ChatPolicyTrace:
        """
        Add a mark to the trace (immutable append).

        Returns new ChatPolicyTrace with the mark appended.
        This is the immutable append-only pattern.
        """
        return ChatPolicyTrace(
            session_id=self.session_id,
            marks=self.marks + (mark,),
        )

    def get_marks(self) -> tuple[ChatMark, ...]:
        """Get all marks (readonly)."""
        return self.marks

    def get_mark(self, turn_number: int) -> ChatMark | None:
        """Get a specific mark by turn number."""
        for mark in self.marks:
            if mark.turn_number == turn_number:
                return mark
        return None

    def get_recent_marks(self, n: int) -> tuple[ChatMark, ...]:
        """Get the N most recent marks."""
        return self.marks[-n:] if len(self.marks) >= n else self.marks

    @property
    def turn_count(self) -> int:
        """Total number of turns in this trace."""
        return len(self.marks)

    @property
    def latest_mark(self) -> ChatMark | None:
        """Get the most recent mark."""
        return self.marks[-1] if self.marks else None

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the trace.

        Used for persistence and API serialization.
        """
        return {
            "session_id": self.session_id,
            "turn_count": self.turn_count,
            "marks": [mark.to_dict() for mark in self.marks],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChatPolicyTrace:
        """
        Deserialize from dictionary.

        Reconstructs the full trace from persisted data.
        """
        marks = tuple(ChatMark.from_dict(mark_data) for mark_data in data.get("marks", []))
        return cls(
            session_id=data["session_id"],
            marks=marks,
        )

    def __repr__(self) -> str:
        """Concise representation."""
        return f"ChatPolicyTrace(session_id={self.session_id}, turns={self.turn_count})"


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ChatMark",
    "ChatPolicyTrace",
]
