"""
Tests for command factory agents.
"""

import os
import pytest
from zen_agents.commands import (
    command_build,
    command_validate,
    CommandResult,
    ValidationResult,
)
from zen_agents.types import SessionConfig, SessionType


class TestCommandValidate:
    """Tests for CommandValidate agent."""

    @pytest.mark.asyncio
    async def test_shell_always_valid(self):
        """SHELL session type is always valid."""
        result = await command_validate.invoke(SessionType.SHELL)
        assert result.valid is True
        assert result.error is None

    @pytest.mark.asyncio
    async def test_custom_always_valid(self):
        """CUSTOM session type is always valid."""
        result = await command_validate.invoke(SessionType.CUSTOM)
        assert result.valid is True
        assert result.error is None

    @pytest.mark.asyncio
    async def test_claude_validation(self):
        """CLAUDE session type checks for 'claude' binary."""
        result = await command_validate.invoke(SessionType.CLAUDE)
        # Result depends on whether 'claude' is in PATH
        assert isinstance(result, ValidationResult)
        assert isinstance(result.valid, bool)


class TestCommandBuild:
    """Tests for CommandBuild agent."""

    @pytest.mark.asyncio
    async def test_shell_command(self):
        """Build command for SHELL session."""
        config = SessionConfig(
            name="test-shell",
            session_type=SessionType.SHELL,
            working_dir="/tmp",
        )
        result = await command_build.invoke(config)

        assert isinstance(result, CommandResult)
        assert len(result.command) == 2
        assert result.command[1] == "-l"  # Login shell flag
        assert isinstance(result.env, dict)
        assert len(result.wrapped_command) == 4
        assert result.wrapped_command[0] == "bash"

    @pytest.mark.asyncio
    async def test_claude_command(self):
        """Build command for CLAUDE session."""
        config = SessionConfig(
            name="test-claude",
            session_type=SessionType.CLAUDE,
            model="claude-sonnet-4-5",
            working_dir="/tmp",
        )
        result = await command_build.invoke(config)

        assert isinstance(result, CommandResult)
        assert result.command[0] == "claude"
        assert "--model" in result.command
        assert "claude-sonnet-4-5" in result.command

    @pytest.mark.asyncio
    async def test_custom_command(self):
        """Build command for CUSTOM session."""
        config = SessionConfig(
            name="test-custom",
            session_type=SessionType.CUSTOM,
            command="htop -C",
            working_dir="/tmp",
        )
        result = await command_build.invoke(config)

        assert isinstance(result, CommandResult)
        assert result.command == ["htop", "-C"]

    @pytest.mark.asyncio
    async def test_openrouter_proxy(self):
        """Test OpenRouter proxy environment variables."""
        # Set up environment
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test123"
        os.environ["OPENROUTER_BASE_URL"] = "https://openrouter.ai/api/v1"

        try:
            config = SessionConfig(
                name="test-proxy",
                session_type=SessionType.CLAUDE,
                model="anthropic/claude-sonnet-4",
                working_dir="/tmp",
            )
            result = await command_build.invoke(config)

            # Check that proxy env vars are set
            assert "ANTHROPIC_API_KEY" in result.env
            assert "ANTHROPIC_BASE_URL" in result.env
            assert "ANTHROPIC_CUSTOM_HEADERS" in result.env
            assert "ANTHROPIC_MODEL" in result.env

            # Verify values
            assert result.env["ANTHROPIC_API_KEY"] == "sk-or-test123"
            assert result.env["ANTHROPIC_BASE_URL"] == "https://openrouter.ai/api/v1"
            assert "sk-or-test123" in result.env["ANTHROPIC_CUSTOM_HEADERS"]

        finally:
            # Clean up
            del os.environ["OPENROUTER_API_KEY"]
            del os.environ["OPENROUTER_BASE_URL"]

    @pytest.mark.asyncio
    async def test_banner_wrapping(self):
        """Test that commands are wrapped with banner."""
        config = SessionConfig(
            name="test-banner",
            session_type=SessionType.SHELL,
            working_dir="/tmp",
        )
        result = await command_build.invoke(config)

        # Verify wrapped command structure
        assert len(result.wrapped_command) == 4
        assert result.wrapped_command[0] == "bash"
        assert result.wrapped_command[1] == "-l"
        assert result.wrapped_command[2] == "-c"
        # Script should contain printf for banner
        assert "printf" in result.wrapped_command[3]
        assert "test-banner" in result.wrapped_command[3]

    @pytest.mark.asyncio
    async def test_codex_command(self):
        """Build command for CODEX session."""
        config = SessionConfig(
            name="test-codex",
            session_type=SessionType.CODEX,
            working_dir="/tmp/project",
        )
        result = await command_build.invoke(config)

        assert result.command[0] == "codex"
        assert "--cd" in result.command
        assert "/tmp/project" in result.command

    @pytest.mark.asyncio
    async def test_gemini_command(self):
        """Build command for GEMINI session."""
        config = SessionConfig(
            name="test-gemini",
            session_type=SessionType.GEMINI,
            system_prompt="You are a helpful assistant",
        )
        result = await command_build.invoke(config)

        assert result.command[0] == "gemini"
        assert "-p" in result.command
        assert "You are a helpful assistant" in result.command


class TestSecurityValidation:
    """Tests for security validation in command building."""

    @pytest.mark.asyncio
    async def test_url_validation(self):
        """Test URL validation."""
        from zen_agents.commands import CommandBuild

        cb = CommandBuild()

        # Valid URLs
        assert cb._validate_url("https://example.com") is not None
        assert cb._validate_url("http://localhost:8080") is not None

        # Invalid URLs
        assert cb._validate_url("file:///etc/passwd") is None
        assert cb._validate_url("javascript:alert(1)") is None
        assert cb._validate_url("") is None
        assert cb._validate_url("a" * 3000) is None  # Too long

    @pytest.mark.asyncio
    async def test_api_key_validation(self):
        """Test API key validation."""
        from zen_agents.commands import CommandBuild

        cb = CommandBuild()

        # Valid API keys
        assert cb._validate_api_key("sk-or-123456") is not None
        assert cb._validate_api_key("sk-ant-xyz789") is not None

        # Invalid API keys
        assert cb._validate_api_key("key with spaces") is None
        assert cb._validate_api_key("key;injection") is None
        assert cb._validate_api_key("") is None
        assert cb._validate_api_key("k" * 300) is None  # Too long

    @pytest.mark.asyncio
    async def test_model_name_validation(self):
        """Test model name validation."""
        from zen_agents.commands import CommandBuild

        cb = CommandBuild()

        # Valid model names
        assert cb._validate_model_name("claude-sonnet-4") is not None
        assert cb._validate_model_name("anthropic/claude-3.5") is not None
        assert cb._validate_model_name("openai/gpt-4o:beta") is not None

        # Invalid model names
        assert cb._validate_model_name("model;injection") is None
        assert cb._validate_model_name("model with spaces") is None
        assert cb._validate_model_name("") is None
        assert cb._validate_model_name("m" * 200) is None  # Too long
