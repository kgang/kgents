"""
Session Quality Checks as Judge.

Judge evaluates at key decision points. Quality gates are Judge.
Validation returns Verdict, not bool.

Why irreducible: Taste cannot be computed. "Is this tasteful?"
                 "Is this ethical?" requires grounding in human values.
"""

from typing import TYPE_CHECKING

import sys
sys.path.insert(0, str(__file__).rsplit("/impl/", 1)[0] + "/impl/claude-openrouter")

from bootstrap import (
    Agent,
    Judge,
    JudgeInput,
    Verdict,
    VerdictType,
    make_default_principles,
)

if TYPE_CHECKING:
    from ..models import Session, NewSessionConfig
    from .config import ZenConfig


class SessionJudge(Agent["NewSessionConfig", Verdict]):
    """
    Evaluate session configuration quality.

    Checks:
    - Tasteful: Is the name meaningful?
    - Composable: Can this session work with others?
    - Ethical: Does this respect resource limits?
    """

    @property
    def name(self) -> str:
        return "SessionJudge"

    async def invoke(self, config: "NewSessionConfig") -> Verdict:
        """Evaluate session config against quality principles."""
        reasons: list[str] = []
        revisions: list[str] = []

        # Tasteful: Is the name meaningful?
        if len(config.name) < 2:
            reasons.append("Name too short - should be descriptive")
            revisions.append("Use a meaningful name (2+ characters)")

        if config.name.isdigit():
            reasons.append("Name is just numbers - should be descriptive")
            revisions.append("Include letters in the name")

        # Composable: Has required fields
        if config.session_type is None:
            reasons.append("Session type is required")
            revisions.append("Specify session_type (claude, codex, gemini, shell, openrouter)")

        # OpenRouter-specific: needs model
        if config.session_type and config.session_type.value == "openrouter":
            if not config.model:
                revisions.append("Consider specifying model for OpenRouter sessions")

        # Working dir validation
        if config.working_dir:
            from pathlib import Path
            if not Path(config.working_dir).exists():
                reasons.append(f"Working directory does not exist: {config.working_dir}")
                revisions.append("Create the directory or use an existing one")

        if reasons:
            if len(reasons) > 2:
                return Verdict.reject(reasons)
            return Verdict.revise(reasons, revisions)

        return Verdict.accept(["Session config passes quality checks"])


class ConfigJudge(Agent["ZenConfig", Verdict]):
    """
    Evaluate merged configuration quality.

    Checks for sensible values and potential issues.
    """

    @property
    def name(self) -> str:
        return "ConfigJudge"

    async def invoke(self, config: "ZenConfig") -> Verdict:
        """Evaluate config against quality principles."""
        reasons: list[str] = []
        revisions: list[str] = []

        # Sensible poll interval
        if config.poll_interval < 0.1:
            reasons.append("Poll interval too short (< 0.1s) - may cause high CPU")
            revisions.append("Use poll_interval >= 0.5s")
        elif config.poll_interval > 60:
            revisions.append("Poll interval > 60s may feel unresponsive")

        # Sensible grace period
        if config.grace_period < 1:
            reasons.append("Grace period too short (< 1s)")
            revisions.append("Use grace_period >= 2s")

        # Session limit
        if config.max_sessions < 1:
            reasons.append("max_sessions must be >= 1")
        elif config.max_sessions > 50:
            revisions.append("max_sessions > 50 may strain system resources")

        # Scrollback
        if config.scrollback_lines < 1000:
            revisions.append("Low scrollback (< 1000) may lose important output")
        elif config.scrollback_lines > 500000:
            revisions.append("Very high scrollback (> 500K) uses significant memory")

        if reasons:
            return Verdict.reject(reasons)
        if revisions:
            return Verdict.revise(
                reasons=["Config has potential issues"],
                revisions=revisions,
            )

        return Verdict.accept(["Config passes quality checks"])


class CreatedSessionJudge(Agent["Session", Verdict]):
    """
    Evaluate a created session for quality.

    Post-creation validation to ensure session is properly initialized.
    """

    @property
    def name(self) -> str:
        return "CreatedSessionJudge"

    async def invoke(self, session: "Session") -> Verdict:
        """Evaluate created session."""
        reasons: list[str] = []

        # Must have tmux_name
        if not session.tmux_name:
            reasons.append("Session has no tmux_name - not properly created")

        # Must have valid state
        if session.state is None:
            reasons.append("Session has no state")

        # Should have id
        if session.id is None:
            reasons.append("Session has no ID")

        if reasons:
            return Verdict.reject(reasons)

        return Verdict.accept(["Session properly initialized"])


class ValidateName(Agent[str, Verdict]):
    """
    Validate just the session name.

    For quick validation in UI before full config is built.
    """

    @property
    def name(self) -> str:
        return "ValidateName"

    async def invoke(self, session_name: str) -> Verdict:
        """Validate session name."""
        reasons: list[str] = []
        revisions: list[str] = []

        if not session_name:
            reasons.append("Name cannot be empty")

        if len(session_name) < 2:
            reasons.append("Name too short")
            revisions.append("Use at least 2 characters")

        if session_name.isdigit():
            revisions.append("Consider using letters, not just numbers")

        # Check for problematic characters
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', session_name):
            reasons.append("Name contains invalid characters")
            revisions.append("Use only letters, numbers, underscore, hyphen")

        if len(session_name) > 50:
            revisions.append("Name is very long - consider shortening")

        if reasons:
            return Verdict.reject(reasons)
        if revisions:
            return Verdict.revise(reasons=["Name has issues"], revisions=revisions)

        return Verdict.accept()
