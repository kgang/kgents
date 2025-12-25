"""
Trust Manager — Trust profile management and persistence

Provides:
- should_gate(user_id, tool_name) - Check if tool needs approval
- record_approval(user_id, tool_name, approved) - Record decision
- suggest_escalation(user_id, tool_name) - After N approvals, suggest trust
- escalate_trust(user_id, tool_name) - User opts into auto-approve
- revoke_trust(user_id, tool_name) - User revokes trust

Architecture:
- In-memory storage for now (will migrate to D-gent persistence)
- Per-user trust profiles
- Thread-safe operations (using asyncio primitives)
- Audit trail for all trust decisions

Philosophy:
- "Trust is earned, not granted"
- First N uses require approval
- After earning trust, user can opt-in to auto-approve
- Trust can be revoked at any time

See: spec/protocols/chat-web.md Part VII.2
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Literal

from .trust import TrustProfile

logger = logging.getLogger(__name__)


# =============================================================================
# Storage Backend (In-Memory + JSON)
# =============================================================================


class TrustStorage:
    """
    Storage backend for trust profiles.

    Current implementation: JSON files in ~/.kgents/trust/
    Future: D-gent persistence layer
    """

    def __init__(self, base_path: Path | None = None):
        """
        Initialize trust storage.

        Args:
            base_path: Base directory for trust profiles (default: ~/.kgents/trust/)
        """
        if base_path is None:
            base_path = Path.home() / ".kgents" / "trust"

        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

        # In-memory cache
        self._profiles: dict[str, TrustProfile] = {}

        logger.info(f"TrustStorage initialized at {self.base_path}")

    def _get_profile_path(self, user_id: str) -> Path:
        """Get path to user's trust profile file."""
        # Sanitize user_id for filesystem
        safe_user_id = user_id.replace("/", "_").replace("\\", "_")
        return self.base_path / f"{safe_user_id}.json"

    def load_profile(self, user_id: str) -> TrustProfile:
        """
        Load trust profile for user.

        Creates a new profile if it doesn't exist.

        Args:
            user_id: User identifier

        Returns:
            Trust profile
        """
        # Check in-memory cache first
        if user_id in self._profiles:
            return self._profiles[user_id]

        # Try loading from disk
        profile_path = self._get_profile_path(user_id)
        if profile_path.exists():
            try:
                with open(profile_path, "r") as f:
                    data = json.load(f)
                profile = TrustProfile.from_dict(data)
                self._profiles[user_id] = profile
                logger.debug(f"Loaded trust profile for {user_id}")
                return profile
            except Exception as e:
                logger.error(f"Failed to load trust profile for {user_id}: {e}")
                # Fall through to create new profile

        # Create new profile
        profile = TrustProfile(user_id=user_id)
        self._profiles[user_id] = profile
        self.save_profile(profile)
        logger.info(f"Created new trust profile for {user_id}")
        return profile

    def save_profile(self, profile: TrustProfile) -> None:
        """
        Save trust profile to disk.

        Args:
            profile: Trust profile to save
        """
        try:
            profile_path = self._get_profile_path(profile.user_id)
            with open(profile_path, "w") as f:
                json.dump(profile.to_dict(), f, indent=2)
            logger.debug(f"Saved trust profile for {profile.user_id}")
        except Exception as e:
            logger.error(f"Failed to save trust profile for {profile.user_id}: {e}")
            raise

    def delete_profile(self, user_id: str) -> None:
        """
        Delete trust profile.

        Args:
            user_id: User identifier
        """
        # Remove from cache
        self._profiles.pop(user_id, None)

        # Remove from disk
        profile_path = self._get_profile_path(user_id)
        if profile_path.exists():
            profile_path.unlink()
            logger.info(f"Deleted trust profile for {user_id}")


# =============================================================================
# Trust Manager
# =============================================================================


class TrustManager:
    """
    Trust manager for tool auto-approval.

    Singleton instance manages all trust profiles.
    """

    def __init__(self, storage: TrustStorage | None = None):
        """
        Initialize trust manager.

        Args:
            storage: Storage backend (default: JSON in ~/.kgents/trust/)
        """
        self.storage = storage or TrustStorage()
        logger.info("TrustManager initialized")

    # =========================================================================
    # Core Operations
    # =========================================================================

    def should_gate(self, user_id: str, tool_name: str) -> bool:
        """
        Check if tool needs approval (gating).

        Args:
            user_id: User identifier
            tool_name: Tool name (e.g., "Edit", "Write", "Bash")

        Returns:
            True if approval required, False if auto-approved
        """
        profile = self.storage.load_profile(user_id)
        return profile.should_gate(tool_name)

    def record_approval(
        self,
        user_id: str,
        tool_name: str,
        approved: bool,
        context: str = "",
        session_id: str | None = None,
        turn_number: int | None = None,
    ) -> None:
        """
        Record a tool approval or denial.

        Args:
            user_id: User identifier
            tool_name: Tool name
            approved: True if approved, False if denied
            context: Additional context for audit trail
            session_id: Optional session ID
            turn_number: Optional turn number
        """
        profile = self.storage.load_profile(user_id)

        if approved:
            profile.record_approval(
                tool_name=tool_name,
                context=context,
                session_id=session_id,
                turn_number=turn_number,
            )
        else:
            profile.record_denial(
                tool_name=tool_name,
                context=context,
                session_id=session_id,
                turn_number=turn_number,
            )

        self.storage.save_profile(profile)
        logger.debug(
            f"Recorded {'approval' if approved else 'denial'} for {tool_name} by {user_id}"
        )

    def suggest_escalation(self, user_id: str, tool_name: str) -> bool:
        """
        Check if we should suggest trust escalation.

        Args:
            user_id: User identifier
            tool_name: Tool name

        Returns:
            True if escalation should be suggested, False otherwise
        """
        profile = self.storage.load_profile(user_id)
        return profile.should_suggest_escalation(tool_name)

    def mark_escalation_suggested(
        self,
        user_id: str,
        tool_name: str,
        session_id: str | None = None,
    ) -> None:
        """
        Mark that escalation has been suggested (to avoid re-suggesting).

        Args:
            user_id: User identifier
            tool_name: Tool name
            session_id: Optional session ID
        """
        profile = self.storage.load_profile(user_id)
        profile.mark_escalation_suggested(tool_name, session_id=session_id)
        self.storage.save_profile(profile)

    def escalate_trust(
        self,
        user_id: str,
        tool_name: str,
        context: str = "",
        session_id: str | None = None,
    ) -> None:
        """
        Escalate tool to TRUSTED (auto-approve).

        User has opted in to auto-approving this tool.

        Args:
            user_id: User identifier
            tool_name: Tool name
            context: Additional context for audit trail
            session_id: Optional session ID
        """
        profile = self.storage.load_profile(user_id)
        profile.escalate_trust(
            tool_name=tool_name,
            context=context,
            session_id=session_id,
        )
        self.storage.save_profile(profile)
        logger.info(f"Escalated {tool_name} to TRUSTED for {user_id}")

    def revoke_trust(
        self,
        user_id: str,
        tool_name: str,
        context: str = "",
        session_id: str | None = None,
    ) -> None:
        """
        Revoke tool trust back to ASK.

        User wants to go back to manual approval.

        Args:
            user_id: User identifier
            tool_name: Tool name
            context: Additional context for audit trail
            session_id: Optional session ID
        """
        profile = self.storage.load_profile(user_id)
        profile.revoke_trust(
            tool_name=tool_name,
            context=context,
            session_id=session_id,
        )
        self.storage.save_profile(profile)
        logger.info(f"Revoked trust for {tool_name} for {user_id}")

    def set_never_trust(
        self,
        user_id: str,
        tool_name: str,
        context: str = "",
        session_id: str | None = None,
    ) -> None:
        """
        Set tool to NEVER (always require approval).

        User explicitly wants to never auto-approve this tool.

        Args:
            user_id: User identifier
            tool_name: Tool name
            context: Additional context for audit trail
            session_id: Optional session ID
        """
        profile = self.storage.load_profile(user_id)
        profile.set_never_trust(
            tool_name=tool_name,
            context=context,
            session_id=session_id,
        )
        self.storage.save_profile(profile)
        logger.info(f"Set {tool_name} to NEVER for {user_id}")

    # =========================================================================
    # Query Operations
    # =========================================================================

    def get_profile(self, user_id: str) -> TrustProfile:
        """
        Get trust profile for user.

        Args:
            user_id: User identifier

        Returns:
            Trust profile
        """
        return self.storage.load_profile(user_id)

    def get_tool_stats(self, user_id: str, tool_name: str) -> dict:
        """
        Get usage statistics for a tool.

        Args:
            user_id: User identifier
            tool_name: Tool name

        Returns:
            Dict with approval_count, denial_count, level, etc.
        """
        profile = self.storage.load_profile(user_id)
        state = profile.get_tool_state(tool_name)
        return {
            "tool_name": state.tool_name,
            "level": state.level.value,
            "approval_count": state.approval_count,
            "denial_count": state.denial_count,
            "last_used": state.last_used.isoformat() if state.last_used else None,
            "escalation_threshold": state.escalation_threshold,
            "escalation_offered": state.escalation_offered,
        }

    def get_trust_summary(self, user_id: str) -> dict:
        """
        Get summary of user's trust profile.

        Args:
            user_id: User identifier

        Returns:
            Summary dict with trusted tools, history stats, etc.
        """
        profile = self.storage.load_profile(user_id)

        trusted_tools = [
            name
            for name, state in profile.trusted_tools.items()
            if state.level.allows_auto_approve()
        ]

        return {
            "user_id": profile.user_id,
            "trusted_tools": trusted_tools,
            "total_tools_used": len(profile.trusted_tools),
            "total_events": len(profile.trust_history),
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
        }


# =============================================================================
# Global Instance
# =============================================================================

# Singleton instance (will be replaced with DI in production)
_trust_manager: TrustManager | None = None


def get_trust_manager() -> TrustManager:
    """
    Get global trust manager instance.

    Singleton pattern for now, will be replaced with proper DI.
    """
    global _trust_manager
    if _trust_manager is None:
        _trust_manager = TrustManager()
    return _trust_manager


__all__ = [
    "TrustStorage",
    "TrustManager",
    "get_trust_manager",
]
