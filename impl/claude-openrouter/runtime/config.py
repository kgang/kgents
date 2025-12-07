"""
Runtime Configuration

Configuration and environment loading for the kgents runtime.
Supports 4 authentication methods in priority order:
1. Claude CLI (claude login)
2. OAuth Token (CLAUDE_CODE_OAUTH_TOKEN)
3. OpenRouter via y-router (OPENROUTER_API_KEY)
4. Anthropic API Key (ANTHROPIC_API_KEY)
"""

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class AuthMethod(Enum):
    """Supported authentication methods in priority order"""
    CLI = "cli"              # Use claude CLI (requires claude login)
    OAUTH = "oauth"          # Use CLAUDE_CODE_OAUTH_TOKEN
    OPENROUTER = "openrouter"  # Use OPENROUTER_API_KEY via y-router
    API_KEY = "api_key"      # Use ANTHROPIC_API_KEY


@dataclass
class RuntimeConfig:
    """Configuration for the kgents runtime"""

    # Authentication (auto-detected in order: CLI > OAuth > OpenRouter > API_KEY)
    auth_method: AuthMethod | None = None  # None = auto-detect

    # Model defaults
    default_model: str = "claude-sonnet-4-20250514"

    # y-router configuration (for OpenRouter via local Docker)
    yrouter_base_url: str = "http://localhost:8787"

    # Token limits
    max_tokens_per_request: int = 4096
    max_tokens_per_minute: int | None = None  # Rate limit

    # Caching
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".cache" / "kgents")

    # API keys (loaded from environment if not set)
    oauth_token: str | None = None
    openrouter_api_key: str | None = None
    anthropic_api_key: str | None = None

    def __post_init__(self):
        # Load from environment if not explicitly set
        if self.oauth_token is None:
            self.oauth_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
        if self.openrouter_api_key is None:
            self.openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
        if self.anthropic_api_key is None:
            self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")

        # Override from environment
        if env_model := os.environ.get("KGENTS_MODEL"):
            self.default_model = env_model
        if env_auth := os.environ.get("KGENTS_AUTH_METHOD"):
            self.auth_method = AuthMethod(env_auth)
        if env_cache_dir := os.environ.get("KGENTS_CACHE_DIR"):
            self.cache_dir = Path(env_cache_dir).expanduser()
        if env_yrouter := os.environ.get("KGENTS_YROUTER_URL"):
            self.yrouter_base_url = env_yrouter


def _check_claude_cli_logged_in() -> bool:
    """Check if claude CLI is installed and user is logged in"""
    # First check if claude binary exists
    if not shutil.which("claude"):
        return False

    try:
        # Try running a simple command to check authentication
        # claude --version should work even if not logged in
        # We check for the presence of auth by trying a print command
        result = subprocess.run(
            ["claude", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return False

        # Check if there's a session file or config indicating login
        # Claude Code stores auth in ~/.claude or similar
        claude_config = Path.home() / ".claude"
        if claude_config.exists():
            # Simple heuristic: if config dir exists and has files, likely logged in
            return any(claude_config.iterdir()) if claude_config.is_dir() else True

        return False
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def detect_auth_method(config: RuntimeConfig | None = None) -> AuthMethod:
    """
    Auto-detect available authentication method.

    Priority order:
    1. Claude CLI (preferred for Max subscribers - no API keys needed)
    2. OAuth token (for containers/CI)
    3. OpenRouter via y-router (multi-model flexibility)
    4. Anthropic API key (fallback)

    Raises:
        RuntimeError: If no authentication method is available
    """
    config = config or RuntimeConfig()

    # 1. Check Claude CLI
    if _check_claude_cli_logged_in():
        return AuthMethod.CLI

    # 2. Check OAuth token
    if config.oauth_token:
        return AuthMethod.OAUTH

    # 3. Check OpenRouter
    if config.openrouter_api_key:
        return AuthMethod.OPENROUTER

    # 4. Check Anthropic API key
    if config.anthropic_api_key:
        return AuthMethod.API_KEY

    raise RuntimeError(
        "No authentication method available. Please either:\n"
        "  1. Run 'claude login' (recommended for Max subscribers)\n"
        "  2. Set CLAUDE_CODE_OAUTH_TOKEN (for containers/CI)\n"
        "  3. Set OPENROUTER_API_KEY (for multi-model via y-router)\n"
        "  4. Set ANTHROPIC_API_KEY (fallback)"
    )


def load_config() -> RuntimeConfig:
    """Load configuration from environment and detect auth method"""
    config = RuntimeConfig()

    # Auto-detect auth method if not specified
    if config.auth_method is None:
        config.auth_method = detect_auth_method(config)

    return config


# Default config singleton
_config: RuntimeConfig | None = None


def get_config() -> RuntimeConfig:
    """Get the global runtime configuration"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reset_config() -> None:
    """Reset the global configuration (for testing)"""
    global _config
    _config = None
