"""Tests for runtime/config.py"""

import os
import pytest
from unittest.mock import patch

from runtime.config import (
    AuthMethod,
    RuntimeConfig,
    detect_auth_method,
    load_config,
    get_config,
    reset_config,
)


class TestRuntimeConfig:
    def test_default_config(self):
        config = RuntimeConfig()
        assert config.auth_method is None
        assert config.default_model == "claude-sonnet-4-20250514"
        assert config.enable_cache is True

    def test_config_from_environment(self):
        with patch.dict(os.environ, {
            "KGENTS_MODEL": "claude-opus-4-20250514",
            "ANTHROPIC_API_KEY": "sk-ant-test",
        }):
            config = RuntimeConfig()
            assert config.default_model == "claude-opus-4-20250514"
            assert config.anthropic_api_key == "sk-ant-test"

    def test_auth_method_override(self):
        with patch.dict(os.environ, {"KGENTS_AUTH_METHOD": "api_key"}):
            config = RuntimeConfig()
            assert config.auth_method == AuthMethod.API_KEY


class TestDetectAuthMethod:
    def setup_method(self):
        reset_config()

    @patch('runtime.config._check_claude_cli_logged_in', return_value=False)
    def test_detect_api_key(self, mock_cli):
        with patch.dict(os.environ, {}, clear=True):
            config = RuntimeConfig(anthropic_api_key="sk-ant-test")
            assert detect_auth_method(config) == AuthMethod.API_KEY

    @patch('runtime.config._check_claude_cli_logged_in', return_value=False)
    def test_detect_oauth(self, mock_cli):
        with patch.dict(os.environ, {}, clear=True):
            config = RuntimeConfig(oauth_token="sk-ant-oat01-test")
            assert detect_auth_method(config) == AuthMethod.OAUTH

    @patch('runtime.config._check_claude_cli_logged_in', return_value=False)
    def test_detect_openrouter(self, mock_cli):
        with patch.dict(os.environ, {}, clear=True):
            config = RuntimeConfig(openrouter_api_key="sk-or-test")
            assert detect_auth_method(config) == AuthMethod.OPENROUTER

    @patch('runtime.config._check_claude_cli_logged_in', return_value=False)
    def test_priority_oauth_over_api_key(self, mock_cli):
        with patch.dict(os.environ, {}, clear=True):
            config = RuntimeConfig(
                oauth_token="sk-ant-oat01-test",
                anthropic_api_key="sk-ant-test"
            )
            # OAuth has higher priority than API key
            assert detect_auth_method(config) == AuthMethod.OAUTH

    @patch('runtime.config._check_claude_cli_logged_in', return_value=False)
    def test_no_auth_raises(self, mock_cli):
        with patch.dict(os.environ, {}, clear=True):
            config = RuntimeConfig()
            with pytest.raises(RuntimeError, match="No authentication method available"):
                detect_auth_method(config)


class TestLoadConfig:
    def setup_method(self):
        reset_config()

    @patch('runtime.config._check_claude_cli_logged_in', return_value=False)
    def test_load_config_with_api_key(self, mock_cli):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test"}, clear=True):
            reset_config()
            config = load_config()
            assert config.auth_method == AuthMethod.API_KEY


class TestGetConfig:
    def setup_method(self):
        reset_config()

    def test_singleton(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test"}, clear=False):
            config1 = get_config()
            config2 = get_config()
            assert config1 is config2
