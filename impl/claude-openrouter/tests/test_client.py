"""Tests for runtime/client.py"""

import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from runtime.client import (
    create_client,
    ClaudeCLIClient,
    OAuthTokenClient,
    OpenRouterClient,
    AnthropicAPIClient,
    get_client,
    reset_client,
)
from runtime.config import AuthMethod, RuntimeConfig, reset_config
from runtime.messages import Message


class TestCreateClient:
    def setup_method(self):
        reset_client()
        reset_config()

    def test_create_cli_client(self):
        config = RuntimeConfig(auth_method=AuthMethod.CLI)
        client = create_client(config)
        assert isinstance(client, ClaudeCLIClient)

    def test_create_oauth_client(self):
        config = RuntimeConfig(
            auth_method=AuthMethod.OAUTH,
            oauth_token="sk-ant-oat01-test"
        )
        client = create_client(config)
        assert isinstance(client, OAuthTokenClient)

    def test_create_openrouter_client(self):
        config = RuntimeConfig(
            auth_method=AuthMethod.OPENROUTER,
            openrouter_api_key="sk-or-test"
        )
        client = create_client(config)
        assert isinstance(client, OpenRouterClient)

    def test_create_api_key_client(self):
        config = RuntimeConfig(
            auth_method=AuthMethod.API_KEY,
            anthropic_api_key="sk-ant-test"
        )
        client = create_client(config)
        assert isinstance(client, AnthropicAPIClient)


class TestOAuthTokenClient:
    def test_requires_token(self):
        config = RuntimeConfig(auth_method=AuthMethod.OAUTH)
        with pytest.raises(ValueError, match="OAuth token not configured"):
            OAuthTokenClient(config)


class TestOpenRouterClient:
    def test_requires_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            config = RuntimeConfig(auth_method=AuthMethod.OPENROUTER)
            with pytest.raises(ValueError, match="OpenRouter API key not configured"):
                OpenRouterClient(config)


class TestAnthropicAPIClient:
    def test_requires_api_key(self):
        config = RuntimeConfig(auth_method=AuthMethod.API_KEY)
        with pytest.raises(ValueError, match="Anthropic API key not configured"):
            AnthropicAPIClient(config)


class TestClaudeCLIClient:
    @pytest.mark.asyncio
    async def test_complete_builds_prompt(self):
        config = RuntimeConfig(auth_method=AuthMethod.CLI)
        client = ClaudeCLIClient(config)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello from Claude"

        with patch('runtime.client.subprocess.run', return_value=mock_result):
            result = await client.complete(
                messages=[Message(role="user", content="Hi")],
                model="test-model"
            )

        assert result.content == "Hello from Claude"
        assert result.model == "test-model"
