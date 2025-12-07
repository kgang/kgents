"""
zen-agents Session Templates

Pre-configured session templates for quick creation.
Templates can be built-in or user-defined.
"""

from dataclasses import dataclass, field
from pathlib import Path

from .types import SessionConfig, SessionType


@dataclass(frozen=True)
class SessionTemplate:
    """A reusable session configuration template."""
    name: str
    display_name: str
    description: str
    session_type: SessionType
    command: str | None = None
    model: str | None = None
    system_prompt: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)
    icon: str = "*"

    def to_config(self, name: str, working_dir: str | None = None) -> SessionConfig:
        """Create a SessionConfig from this template."""
        return SessionConfig(
            name=name,
            session_type=self.session_type,
            working_dir=working_dir,
            command=self.command,
            model=self.model,
            system_prompt=self.system_prompt,
            tags=list(self.tags),
        )


# Built-in templates
CLAUDE_DEFAULT = SessionTemplate(
    name="claude_default",
    display_name="Claude Code",
    description="Interactive Claude Code session",
    session_type=SessionType.CLAUDE,
    icon=">>>",
)

CLAUDE_REVIEW = SessionTemplate(
    name="claude_review",
    display_name="Code Review",
    description="Claude session for reviewing code",
    session_type=SessionType.CLAUDE,
    system_prompt="You are a code reviewer. Focus on bugs, security issues, and maintainability.",
    tags=("review", "quality"),
    icon="?>>",
)

CLAUDE_REFACTOR = SessionTemplate(
    name="claude_refactor",
    display_name="Refactoring",
    description="Claude session for refactoring code",
    session_type=SessionType.CLAUDE,
    system_prompt="You are helping refactor code for clarity and maintainability.",
    tags=("refactor",),
    icon="~>>",
)

CLAUDE_DEBUG = SessionTemplate(
    name="claude_debug",
    display_name="Debugging",
    description="Claude session for debugging issues",
    session_type=SessionType.CLAUDE,
    system_prompt="You are helping debug code. Be methodical and check assumptions.",
    tags=("debug",),
    icon="!>>",
)

SHELL_DEFAULT = SessionTemplate(
    name="shell_default",
    display_name="Shell",
    description="Plain zsh shell",
    session_type=SessionType.SHELL,
    command="/bin/zsh",
    icon="$",
)

SHELL_HTOP = SessionTemplate(
    name="shell_htop",
    display_name="System Monitor",
    description="htop for system monitoring",
    session_type=SessionType.SHELL,
    command="htop",
    tags=("monitoring",),
    icon="^",
)

SHELL_LOGS = SessionTemplate(
    name="shell_logs",
    display_name="Log Viewer",
    description="Tail system logs",
    session_type=SessionType.SHELL,
    command="tail -f /var/log/system.log",
    tags=("logs", "monitoring"),
    icon="@",
)

CODEX_DEFAULT = SessionTemplate(
    name="codex_default",
    display_name="Codex CLI",
    description="OpenAI Codex CLI session",
    session_type=SessionType.CODEX,
    icon="cx",
)

GEMINI_DEFAULT = SessionTemplate(
    name="gemini_default",
    display_name="Gemini CLI",
    description="Google Gemini CLI session",
    session_type=SessionType.GEMINI,
    icon="gm",
)

# Template registry
BUILT_IN_TEMPLATES: list[SessionTemplate] = [
    CLAUDE_DEFAULT,
    CLAUDE_REVIEW,
    CLAUDE_REFACTOR,
    CLAUDE_DEBUG,
    SHELL_DEFAULT,
    SHELL_HTOP,
    SHELL_LOGS,
    CODEX_DEFAULT,
    GEMINI_DEFAULT,
]

# Group templates by type for easier access
TEMPLATES_BY_TYPE: dict[SessionType, list[SessionTemplate]] = {}
for t in BUILT_IN_TEMPLATES:
    if t.session_type not in TEMPLATES_BY_TYPE:
        TEMPLATES_BY_TYPE[t.session_type] = []
    TEMPLATES_BY_TYPE[t.session_type].append(t)


def get_templates() -> list[SessionTemplate]:
    """Get all available templates."""
    return BUILT_IN_TEMPLATES.copy()


def get_template(name: str) -> SessionTemplate | None:
    """Get a template by name."""
    for t in BUILT_IN_TEMPLATES:
        if t.name == name:
            return t
    return None


def get_templates_for_type(session_type: SessionType) -> list[SessionTemplate]:
    """Get templates for a specific session type."""
    return TEMPLATES_BY_TYPE.get(session_type, [])


__all__ = [
    "SessionTemplate",
    "BUILT_IN_TEMPLATES",
    "TEMPLATES_BY_TYPE",
    "get_templates",
    "get_template",
    "get_templates_for_type",
]
