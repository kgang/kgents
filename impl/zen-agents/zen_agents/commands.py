"""
Command Factory Agents

CommandBuild: SessionConfig → CommandResult
CommandValidate: SessionType → ValidationResult

Builds shell commands for different session types.
Based on zenportal's SessionCommandBuilder.
"""

import hashlib
import os
import re
import shlex
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from bootstrap import Agent
from .types import SessionConfig, SessionType


# =============================================================================
# RESULT TYPES
# =============================================================================

@dataclass
class CommandResult:
    """Result of building a command"""
    command: list[str]              # The command args
    env: dict[str, str]             # Environment variables to set
    wrapped_command: list[str]      # Command wrapped with banner


@dataclass
class ValidationResult:
    """Result of validating a session type"""
    valid: bool
    error: str | None = None

    @classmethod
    def ok(cls) -> 'ValidationResult':
        return cls(valid=True)

    @classmethod
    def fail(cls, error: str) -> 'ValidationResult':
        return cls(valid=False, error=error)


# =============================================================================
# BANNER GENERATION (from zenportal)
# =============================================================================

# Box drawing characters for borders
GLYPHS = {
    "top_left": "╭",
    "top_right": "╮",
    "bottom_left": "╰",
    "bottom_right": "╯",
    "horizontal": "─",
    "vertical": "│",
}

# Zen-themed decorative patterns
PATTERNS = [
    "· · ·",
    "~ ~ ~",
    "* * *",
    "○ ○ ○",
    "◦ ◦ ◦",
    "· ~ ·",
    "* · *",
    "~ · ~",
]

# Subtle accent colors (ANSI 256-color codes, muted tones)
COLORS = [
    "\033[38;5;109m",  # muted cyan
    "\033[38;5;139m",  # muted purple
    "\033[38;5;144m",  # muted olive
    "\033[38;5;138m",  # muted rose
    "\033[38;5;108m",  # muted green
    "\033[38;5;146m",  # muted blue
    "\033[38;5;181m",  # muted pink
    "\033[38;5;187m",  # muted cream
]

RESET = "\033[0m"
DIM = "\033[2m"


def _hash_to_index(seed: str, options: list) -> int:
    """Convert a string seed to a deterministic index."""
    h = hashlib.md5(seed.encode()).hexdigest()
    return int(h[:8], 16) % len(options)


def generate_banner(session_name: str, session_id: str) -> str:
    """Generate a procedural banner for a session.

    The banner is deterministic based on the session ID, so the same
    session always gets the same visual identity.

    Args:
        session_name: Display name for the session
        session_id: Unique session ID for procedural generation

    Returns:
        A multi-line string containing the banner
    """
    # Use session_id for deterministic selection
    pattern = PATTERNS[_hash_to_index(session_id + "pattern", PATTERNS)]
    color = COLORS[_hash_to_index(session_id + "color", COLORS)]

    # Build the banner
    width = max(40, len(session_name) + 8)
    inner_width = width - 2

    # Top pattern line
    pattern_line = f"{pattern:^{inner_width}}"

    # Session name centered
    name_line = f"{session_name:^{inner_width}}"

    # Short ID for reference
    short_id = session_id[:8]
    id_line = f"{short_id:^{inner_width}}"

    # Build the box
    top = GLYPHS["top_left"] + GLYPHS["horizontal"] * inner_width + GLYPHS["top_right"]
    bottom = GLYPHS["bottom_left"] + GLYPHS["horizontal"] * inner_width + GLYPHS["bottom_right"]

    lines = [
        "",
        f"{color}{DIM}{top}{RESET}",
        f"{color}{DIM}{GLYPHS['vertical']}{RESET}{pattern_line}{color}{DIM}{GLYPHS['vertical']}{RESET}",
        f"{color}{DIM}{GLYPHS['vertical']}{RESET}{color}{name_line}{RESET}{color}{DIM}{GLYPHS['vertical']}{RESET}",
        f"{color}{DIM}{GLYPHS['vertical']}{id_line}{GLYPHS['vertical']}{RESET}",
        f"{color}{DIM}{bottom}{RESET}",
        "",
    ]

    return "\n".join(lines)


def generate_banner_command(session_name: str, session_id: str) -> str:
    """Generate a shell command that prints the banner.

    This is safe to pass to bash -c or include in a script.

    Args:
        session_name: Display name for the session
        session_id: Unique session ID for procedural generation

    Returns:
        A shell command string that prints the banner
    """
    banner = generate_banner(session_name, session_id)
    # Escape for shell (single quotes, escape existing single quotes)
    escaped = banner.replace("'", "'\"'\"'")
    return f"printf '%s\\n' '{escaped}'"


# =============================================================================
# VALIDATION PATTERNS
# =============================================================================

_API_KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
_SAFE_URL_SCHEMES = frozenset({'http', 'https'})
_MAX_API_KEY_LENGTH = 256
_MAX_URL_LENGTH = 2048


# =============================================================================
# COMMAND VALIDATION AGENT
# =============================================================================

class CommandValidate(Agent[SessionType, ValidationResult]):
    """
    Validate that required binaries exist for a session type.

    Type signature: SessionType → ValidationResult

    Checks:
        - CLAUDE: 'claude' binary exists
        - CODEX: 'codex' binary exists
        - GEMINI: 'gemini' binary exists
        - SHELL: shell exists (from env or /bin/zsh)
        - CUSTOM: always valid (command provided by user)
    """

    # Binary required for each session type
    BINARY_MAP = {
        SessionType.CLAUDE: "claude",
        SessionType.CODEX: "codex",
        SessionType.GEMINI: "gemini",
    }

    @property
    def name(self) -> str:
        return "CommandValidate"

    @property
    def genus(self) -> str:
        return "zen"

    @property
    def purpose(self) -> str:
        return "Validate that required binaries exist for session type"

    async def invoke(self, session_type: SessionType) -> ValidationResult:
        """
        Check if the required binary exists for the session type.

        Returns ValidationResult with valid=True if binary found or not needed.
        """
        # SHELL and CUSTOM don't require specific binaries
        if session_type in {SessionType.SHELL, SessionType.CUSTOM}:
            return ValidationResult.ok()

        # Check if binary exists
        binary = self.BINARY_MAP.get(session_type)
        if binary and not shutil.which(binary):
            return ValidationResult.fail(f"Command '{binary}' not found in PATH")

        return ValidationResult.ok()


# =============================================================================
# COMMAND BUILD AGENT
# =============================================================================

class CommandBuild(Agent[SessionConfig, CommandResult]):
    """
    Build the shell command for a session.

    Type signature: SessionConfig → CommandResult

    Produces:
        - command: The base command args
        - env: Environment variables (including OpenRouter proxy if configured)
        - wrapped_command: Command wrapped with banner for visual separation

    Based on zenportal's SessionCommandBuilder.
    """

    @property
    def name(self) -> str:
        return "CommandBuild"

    @property
    def genus(self) -> str:
        return "zen"

    @property
    def purpose(self) -> str:
        return "Build shell command for a session configuration"

    async def invoke(self, config: SessionConfig) -> CommandResult:
        """
        Build the command for a session config.

        Returns CommandResult with command, env vars, and wrapped command.
        """
        # Build base command
        command = self._build_command(config)

        # Build environment variables (including proxy settings)
        env = self._build_env_vars(config)

        # Wrap with banner
        # Use session name + working_dir as deterministic ID
        session_id = hashlib.md5(f"{config.name}{config.working_dir}".encode()).hexdigest()
        wrapped = self._wrap_with_banner(command, config.name, session_id, env)

        return CommandResult(
            command=command,
            env=env,
            wrapped_command=wrapped,
        )

    def _build_command(self, config: SessionConfig) -> list[str]:
        """Build the base command for a session type."""
        if config.session_type == SessionType.CLAUDE:
            command_args = ["claude"]
            if config.model:
                command_args.extend(["--model", config.model])
            # Could add other claude-specific flags here
            # if config.prompt:
            #     command_args.append(config.prompt)

        elif config.session_type == SessionType.CODEX:
            command_args = ["codex"]
            if config.working_dir:
                command_args.extend(["--cd", config.working_dir])

        elif config.session_type == SessionType.GEMINI:
            command_args = ["gemini"]
            if config.system_prompt:
                command_args.extend(["-p", config.system_prompt])

        elif config.session_type == SessionType.CUSTOM:
            # Custom command from config
            if config.command:
                # Parse shell command string into args
                command_args = shlex.split(config.command)
            else:
                # Fallback to shell
                command_args = [os.environ.get("SHELL", "/bin/zsh"), "-l"]

        else:
            # SHELL session - start user's default shell with login profile
            command_args = [os.environ.get("SHELL", "/bin/zsh"), "-l"]

        return command_args

    def _build_env_vars(self, config: SessionConfig) -> dict[str, str]:
        """Build environment variables, including OpenRouter proxy if configured."""
        env_vars = dict(config.env)  # Start with config-provided env

        # Add OpenRouter proxy settings if configured
        # Check for OPENROUTER_API_KEY and OPENROUTER_BASE_URL in environment
        api_key = os.environ.get("OPENROUTER_API_KEY")
        base_url = os.environ.get("OPENROUTER_BASE_URL")

        if api_key and config.session_type == SessionType.CLAUDE:
            # Set up Claude to use OpenRouter proxy (y-router)
            validated_key = self._validate_api_key(api_key)
            if validated_key:
                env_vars["ANTHROPIC_API_KEY"] = validated_key
                env_vars["ANTHROPIC_CUSTOM_HEADERS"] = f"x-api-key: {validated_key}"

            # Set base URL if provided
            if base_url:
                validated_url = self._validate_url(base_url)
                if validated_url:
                    env_vars["ANTHROPIC_BASE_URL"] = validated_url
            else:
                # Default y-router URL
                env_vars["ANTHROPIC_BASE_URL"] = "https://y-router.fly.dev"

            # Model override if configured
            if config.model:
                validated_model = self._validate_model_name(config.model)
                if validated_model:
                    env_vars["ANTHROPIC_MODEL"] = validated_model

        return env_vars

    def _wrap_with_banner(
        self,
        command: list[str],
        session_name: str,
        session_id: str,
        env_vars: dict[str, str] | None = None,
    ) -> list[str]:
        """Wrap a command with a banner print for visual session separation.

        Args:
            command: The command to wrap
            session_name: Name to display in banner
            session_id: Session ID for banner
            env_vars: Optional environment variables to export before running

        Returns a bash command that prints the banner then execs the original command.
        """
        banner_cmd = generate_banner_command(session_name, session_id)

        # Build env var exports if provided
        env_exports = ""
        if env_vars:
            exports = [f"export {k}={shlex.quote(v)}" for k, v in env_vars.items()]
            env_exports = " && ".join(exports) + " && "

        # Shell-escape the original command args
        escaped_cmd = " ".join(shlex.quote(arg) for arg in command)
        # Create a bash script that prints banner then execs command
        # Run command and wait on error
        # Use login shell (-l) for proper terminal environment setup
        script = f"{banner_cmd}; {env_exports}{escaped_cmd} || read -p 'Session ended with error. Press enter to close...'"
        return ["bash", "-l", "-c", script]

    def _validate_url(self, url: str) -> str | None:
        """Validate and sanitize a URL for use as an API base URL.

        Returns the sanitized URL or None if invalid.
        """
        if not url or len(url) > _MAX_URL_LENGTH:
            return None

        try:
            parsed = urlparse(url)
            # Only allow http/https schemes
            if parsed.scheme not in _SAFE_URL_SCHEMES:
                return None
            # Must have a host
            if not parsed.netloc:
                return None
            # Reconstruct to normalize (removes potential obfuscation)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
        except Exception:
            return None

    def _validate_api_key(self, key: str) -> str | None:
        """Validate an API key for safe use in environment variables.

        Returns the key if valid, None otherwise.
        API keys should be alphanumeric with dashes/underscores only.
        """
        if not key or len(key) > _MAX_API_KEY_LENGTH:
            return None

        # Strip whitespace
        key = key.strip()

        # Check for safe characters only (alphanumeric, dash, underscore)
        # Most API keys follow this pattern (sk-or-xxx, sk-ant-xxx, etc.)
        if not _API_KEY_PATTERN.match(key):
            return None

        return key

    def _validate_model_name(self, model: str) -> str | None:
        """Validate a model name for safe use.

        Returns the model name if valid, None otherwise.
        Model names should be alphanumeric with common separators.
        """
        if not model or len(model) > 128:
            return None

        model = model.strip()

        # Allow alphanumeric, dash, underscore, slash, colon, period
        # e.g., "anthropic/claude-sonnet-4", "openai/gpt-4o:beta"
        if not re.match(r'^[a-zA-Z0-9/_:.-]+$', model):
            return None

        return model


# =============================================================================
# SINGLETON INSTANCES
# =============================================================================

command_validate = CommandValidate()
command_build = CommandBuild()
