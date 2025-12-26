"""
Trust Escalation System — Trust profile data model

From Kent's vision: "Allow users to opt-in to auto-approving each capability
and tool for the first time. Create a trust profile/document for the user."

Philosophy:
- Trust is earned, not granted
- First use: MUST approve
- After N successful uses: offer to escalate
- Trust can be revoked at any time
- Audit trail for all trust decisions

See: spec/protocols/chat-web.md Part VII.2 (Mutation Acknowledgment)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal

# =============================================================================
# Trust Levels
# =============================================================================


class TrustLevel(Enum):
    """
    Trust level for a tool.

    Progression:
    1. ASK (default) - Require approval each time
    2. TRUSTED - Auto-approve (user opted in)
    3. NEVER - Always require approval (explicit user choice)
    """

    NEVER = "never"      # Always require approval (user choice)
    ASK = "ask"          # Default: ask each time
    TRUSTED = "trusted"  # Auto-approve (user opted in)

    def allows_auto_approve(self) -> bool:
        """Check if this trust level allows auto-approval."""
        return self == TrustLevel.TRUSTED


# =============================================================================
# Trust Events
# =============================================================================


@dataclass
class TrustEvent:
    """
    A single trust decision event.

    Audit trail for transparency and debugging.
    """

    tool_name: str
    action: Literal["approved", "denied", "escalated", "revoked", "suggested"]
    timestamp: datetime
    context: str  # Why this happened

    # Metadata
    session_id: str | None = None
    turn_number: int | None = None

    def to_dict(self) -> dict:
        """Serialize to dict for storage."""
        return {
            "tool_name": self.tool_name,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "session_id": self.session_id,
            "turn_number": self.turn_number,
        }

    @classmethod
    def from_dict(cls, data: dict) -> TrustEvent:
        """Deserialize from dict."""
        return cls(
            tool_name=data["tool_name"],
            action=data["action"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            context=data["context"],
            session_id=data.get("session_id"),
            turn_number=data.get("turn_number"),
        )


# =============================================================================
# Tool Trust State
# =============================================================================


@dataclass
class ToolTrustState:
    """
    Trust state for a single tool.

    Tracks usage history and current trust level.
    """

    tool_name: str
    level: TrustLevel = TrustLevel.ASK

    # Usage statistics
    approval_count: int = 0
    denial_count: int = 0
    last_used: datetime | None = None

    # Escalation thresholds
    escalation_threshold: int = 5  # Suggest trust after N approvals
    escalation_offered: bool = False  # Has escalation been suggested?

    def should_suggest_escalation(self) -> bool:
        """
        Check if we should suggest trust escalation.

        Criteria:
        - User has approved this tool N times
        - Escalation hasn't been offered yet
        - Current level is ASK (not NEVER or already TRUSTED)
        """
        return (
            self.level == TrustLevel.ASK
            and self.approval_count >= self.escalation_threshold
            and not self.escalation_offered
        )

    def record_approval(self) -> None:
        """Record an approval."""
        self.approval_count += 1
        self.last_used = datetime.now()

    def record_denial(self) -> None:
        """Record a denial."""
        self.denial_count += 1
        self.last_used = datetime.now()

    def escalate(self) -> None:
        """Escalate to TRUSTED."""
        self.level = TrustLevel.TRUSTED
        self.escalation_offered = True

    def revoke(self) -> None:
        """Revoke trust back to ASK."""
        self.level = TrustLevel.ASK
        self.escalation_offered = False

    def set_never(self) -> None:
        """Set to NEVER (explicit user choice)."""
        self.level = TrustLevel.NEVER
        self.escalation_offered = True  # Don't offer again

    def to_dict(self) -> dict:
        """Serialize to dict for storage."""
        return {
            "tool_name": self.tool_name,
            "level": self.level.value,
            "approval_count": self.approval_count,
            "denial_count": self.denial_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "escalation_threshold": self.escalation_threshold,
            "escalation_offered": self.escalation_offered,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ToolTrustState:
        """Deserialize from dict."""
        state = cls(
            tool_name=data["tool_name"],
            level=TrustLevel(data["level"]),
            approval_count=data.get("approval_count", 0),
            denial_count=data.get("denial_count", 0),
            escalation_threshold=data.get("escalation_threshold", 5),
            escalation_offered=data.get("escalation_offered", False),
        )

        if data.get("last_used"):
            state.last_used = datetime.fromisoformat(data["last_used"])

        return state


# =============================================================================
# Trust Profile
# =============================================================================


@dataclass
class TrustProfile:
    """
    User's trust profile for tool auto-approval.

    Philosophy:
    - Trust is per-user, per-tool
    - Trust is earned through successful usage
    - Trust can be revoked at any time
    - Full audit trail for transparency

    Lifecycle:
    1. User uses tool for first time → ASK (manual approval)
    2. After N approvals → suggest escalation to TRUSTED
    3. User accepts → tool auto-approves from now on
    4. User can revoke at any time → back to ASK
    5. User can set NEVER → always require approval
    """

    user_id: str
    trusted_tools: dict[str, ToolTrustState] = field(default_factory=dict)
    trust_history: list[TrustEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Global settings
    default_escalation_threshold: int = 5  # Default for new tools

    def get_tool_state(self, tool_name: str) -> ToolTrustState:
        """
        Get trust state for a tool, creating it if it doesn't exist.
        """
        if tool_name not in self.trusted_tools:
            self.trusted_tools[tool_name] = ToolTrustState(
                tool_name=tool_name,
                escalation_threshold=self.default_escalation_threshold,
            )
        return self.trusted_tools[tool_name]

    def should_gate(self, tool_name: str) -> bool:
        """
        Check if tool needs approval (gating).

        Returns:
            True if approval required, False if auto-approved
        """
        state = self.get_tool_state(tool_name)
        return not state.level.allows_auto_approve()

    def record_approval(
        self,
        tool_name: str,
        context: str = "",
        session_id: str | None = None,
        turn_number: int | None = None,
    ) -> None:
        """Record a tool approval."""
        state = self.get_tool_state(tool_name)
        state.record_approval()

        event = TrustEvent(
            tool_name=tool_name,
            action="approved",
            timestamp=datetime.now(),
            context=context or f"User approved {tool_name}",
            session_id=session_id,
            turn_number=turn_number,
        )
        self.trust_history.append(event)
        self.updated_at = datetime.now()

    def record_denial(
        self,
        tool_name: str,
        context: str = "",
        session_id: str | None = None,
        turn_number: int | None = None,
    ) -> None:
        """Record a tool denial."""
        state = self.get_tool_state(tool_name)
        state.record_denial()

        event = TrustEvent(
            tool_name=tool_name,
            action="denied",
            timestamp=datetime.now(),
            context=context or f"User denied {tool_name}",
            session_id=session_id,
            turn_number=turn_number,
        )
        self.trust_history.append(event)
        self.updated_at = datetime.now()

    def escalate_trust(
        self,
        tool_name: str,
        context: str = "",
        session_id: str | None = None,
    ) -> None:
        """Escalate tool to TRUSTED."""
        state = self.get_tool_state(tool_name)
        state.escalate()

        event = TrustEvent(
            tool_name=tool_name,
            action="escalated",
            timestamp=datetime.now(),
            context=context or f"User escalated {tool_name} to TRUSTED",
            session_id=session_id,
        )
        self.trust_history.append(event)
        self.updated_at = datetime.now()

    def revoke_trust(
        self,
        tool_name: str,
        context: str = "",
        session_id: str | None = None,
    ) -> None:
        """Revoke tool trust back to ASK."""
        state = self.get_tool_state(tool_name)
        state.revoke()

        event = TrustEvent(
            tool_name=tool_name,
            action="revoked",
            timestamp=datetime.now(),
            context=context or f"User revoked trust for {tool_name}",
            session_id=session_id,
        )
        self.trust_history.append(event)
        self.updated_at = datetime.now()

    def set_never_trust(
        self,
        tool_name: str,
        context: str = "",
        session_id: str | None = None,
    ) -> None:
        """Set tool to NEVER (always require approval)."""
        state = self.get_tool_state(tool_name)
        state.set_never()

        event = TrustEvent(
            tool_name=tool_name,
            action="revoked",
            timestamp=datetime.now(),
            context=context or f"User set {tool_name} to NEVER",
            session_id=session_id,
        )
        self.trust_history.append(event)
        self.updated_at = datetime.now()

    def should_suggest_escalation(self, tool_name: str) -> bool:
        """Check if we should suggest trust escalation for this tool."""
        state = self.get_tool_state(tool_name)
        return state.should_suggest_escalation()

    def mark_escalation_suggested(
        self,
        tool_name: str,
        session_id: str | None = None,
    ) -> None:
        """Mark that escalation has been suggested (to avoid re-suggesting)."""
        state = self.get_tool_state(tool_name)
        state.escalation_offered = True

        event = TrustEvent(
            tool_name=tool_name,
            action="suggested",
            timestamp=datetime.now(),
            context=f"Suggested trust escalation for {tool_name}",
            session_id=session_id,
        )
        self.trust_history.append(event)
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Serialize to dict for storage."""
        return {
            "user_id": self.user_id,
            "trusted_tools": {
                name: state.to_dict()
                for name, state in self.trusted_tools.items()
            },
            "trust_history": [event.to_dict() for event in self.trust_history],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "default_escalation_threshold": self.default_escalation_threshold,
        }

    @classmethod
    def from_dict(cls, data: dict) -> TrustProfile:
        """Deserialize from dict."""
        profile = cls(
            user_id=data["user_id"],
            trusted_tools={
                name: ToolTrustState.from_dict(state_data)
                for name, state_data in data.get("trusted_tools", {}).items()
            },
            trust_history=[
                TrustEvent.from_dict(event_data)
                for event_data in data.get("trust_history", [])
            ],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            default_escalation_threshold=data.get("default_escalation_threshold", 5),
        )
        return profile


__all__ = [
    "TrustLevel",
    "TrustEvent",
    "ToolTrustState",
    "TrustProfile",
]
