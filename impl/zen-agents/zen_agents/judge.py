"""
ZenJudge Agent

Judge: SessionConfig → SessionVerdict
Judge(config) = Accept | Reject(reason) | Revise(suggestion)

The validation layer for zen-agents. Extends kgents Judge with
session-specific validation principles.

What it judges:
    - Session configs (is this a valid session definition?)
    - Session names (unique? valid characters?)
    - Resource limits (too many sessions? conflicting ports?)
    - State transitions (can this session move from X to Y?)
"""

from pathlib import Path
from typing import Any

from bootstrap import Agent, Verdict, VerdictStatus, Principle
from .types import (
    SessionConfig,
    SessionState,
    SessionType,
    SessionVerdict,
    ZenGroundState,
)


# Session-specific validation questions
SESSION_PRINCIPLES = {
    "name_valid": "Is the session name valid (alphanumeric, dashes, underscores)?",
    "name_unique": "Is this session name unique among active sessions?",
    "type_known": "Is the session type recognized?",
    "working_dir_exists": "Does the working directory exist (if specified)?",
    "command_safe": "Is the command safe to execute?",
    "resources_available": "Are system resources available (not at max sessions)?",
}


class ZenJudge(Agent[SessionConfig, SessionVerdict]):
    """
    The validation layer for zen-agents.

    Type signature: ZenJudge: SessionConfig → SessionVerdict

    Applies session-specific principles:
        - Naming: valid characters, uniqueness
        - Resources: session limits, port conflicts
        - Safety: command injection prevention
        - Transitions: valid state machine moves

    Embodies the 6 kgents principles in session context:
        - Tasteful: Does this session serve a clear purpose?
        - Curated: Is another session doing the same thing?
        - Ethical: Does this respect user intent?
        - Joy-Inducing: Will this session be useful?
        - Composable: Can this session work with others?
        - Heterarchical: Does this preserve user agency?
    """

    def __init__(self, ground_state: ZenGroundState | None = None):
        self._ground_state = ground_state

    @property
    def name(self) -> str:
        return "ZenJudge"

    @property
    def genus(self) -> str:
        return "zen"

    @property
    def purpose(self) -> str:
        return "Validates session configurations against zen principles"

    def with_ground(self, ground_state: ZenGroundState) -> 'ZenJudge':
        """Return a judge with ground state context"""
        return ZenJudge(ground_state=ground_state)

    async def invoke(self, config: SessionConfig) -> SessionVerdict:
        """
        Judge a session configuration.

        Returns Accept if all checks pass, Reject with issues otherwise.
        """
        issues: list[str] = []
        suggestions: list[str] = []

        # Check name validity
        name_result = self._check_name_valid(config.name)
        if not name_result[0]:
            issues.append(name_result[1])

        # Check name uniqueness
        if self._ground_state:
            unique_result = self._check_name_unique(config.name)
            if not unique_result[0]:
                issues.append(unique_result[1])
                suggestions.append(f"Try: {config.name}-2")

        # Check session type
        type_result = self._check_type_known(config.session_type)
        if not type_result[0]:
            issues.append(type_result[1])

        # Check working directory
        if config.working_dir:
            dir_result = self._check_working_dir(config.working_dir)
            if not dir_result[0]:
                issues.append(dir_result[1])

        # Check command safety (basic)
        if config.command:
            cmd_result = self._check_command_safe(config.command)
            if not cmd_result[0]:
                issues.append(cmd_result[1])

        # Check resource limits
        if self._ground_state:
            resource_result = self._check_resources(config)
            if not resource_result[0]:
                issues.append(resource_result[1])

        # Return verdict
        if issues:
            return SessionVerdict(valid=False, issues=issues, suggestions=suggestions)
        return SessionVerdict.accept()

    def _check_name_valid(self, name: str) -> tuple[bool, str]:
        """Check if name contains valid characters"""
        import re
        if not name:
            return False, "Session name cannot be empty"
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return False, f"Invalid name '{name}': use only alphanumeric, dash, underscore"
        if len(name) > 50:
            return False, f"Name too long ({len(name)} chars, max 50)"
        return True, ""

    def _check_name_unique(self, name: str) -> tuple[bool, str]:
        """Check if name is unique among active sessions"""
        if not self._ground_state:
            return True, ""

        for sid, session in self._ground_state.sessions.items():
            if session.config.name == name and session.is_alive():
                return False, f"Session '{name}' already exists"
        return True, ""

    def _check_type_known(self, session_type: SessionType) -> tuple[bool, str]:
        """Check if session type is recognized"""
        # All enum values are valid by definition
        return True, ""

    def _check_working_dir(self, working_dir: str) -> tuple[bool, str]:
        """Check if working directory exists"""
        from pathlib import Path
        path = Path(working_dir).expanduser()
        if not path.exists():
            return False, f"Working directory does not exist: {working_dir}"
        if not path.is_dir():
            return False, f"Not a directory: {working_dir}"
        return True, ""

    def _check_command_safe(self, command: str) -> tuple[bool, str]:
        """Basic command safety check (prevent obvious issues)"""
        dangerous_patterns = [
            "rm -rf /",
            ":(){ :|:& };:",  # Fork bomb
            "> /dev/sda",
            "mkfs.",
            "dd if=",
        ]
        for pattern in dangerous_patterns:
            if pattern in command:
                return False, f"Potentially dangerous command detected"
        return True, ""

    def _check_resources(self, config: SessionConfig) -> tuple[bool, str]:
        """Check if resources are available"""
        if not self._ground_state:
            return True, ""

        active_count = sum(
            1 for s in self._ground_state.sessions.values()
            if s.is_alive()
        )
        if active_count >= self._ground_state.max_sessions:
            return False, f"Max sessions reached ({self._ground_state.max_sessions})"
        return True, ""


# Singleton instance
zen_judge = ZenJudge()
