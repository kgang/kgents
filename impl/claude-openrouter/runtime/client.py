"""
LLM Client Abstraction

Abstract interface with four backends:
1. ClaudeCLIClient - Uses claude CLI binary (for Max subscribers)
2. OAuthTokenClient - Direct API with OAuth token (for containers/CI)
3. OpenRouterClient - OpenRouter via y-router (multi-model)
4. AnthropicAPIClient - Direct Anthropic API key (fallback)
"""

import asyncio
import json
import subprocess
from abc import ABC, abstractmethod
from typing import AsyncIterator

import httpx

from .config import AuthMethod, RuntimeConfig, get_config
from .messages import CompletionResult, Message, TokenUsage


class LLMClient(ABC):
    """Abstract base class for LLM clients"""

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: str | None = None,
    ) -> CompletionResult:
        """Generate a completion for the given messages"""
        pass

    async def complete_stream(
        self,
        messages: list[Message],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream completion tokens. Default: non-streaming fallback."""
        result = await self.complete(messages, model, max_tokens, temperature, system)
        yield result.content


class ClaudeCLIClient(LLMClient):
    """
    Uses 'claude' CLI binary for completions.
    Requires prior 'claude login' authentication.
    Best for Max subscribers - no API keys needed.
    """

    def __init__(self, config: RuntimeConfig | None = None):
        self._config = config or get_config()

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: str | None = None,
    ) -> CompletionResult:
        model = model or self._config.default_model

        # Build prompt from messages
        prompt_parts = []
        if system:
            prompt_parts.append(f"System: {system}\n")

        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}\n")
            elif msg.role == "user":
                prompt_parts.append(f"Human: {msg.content}\n")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}\n")

        prompt = "\n".join(prompt_parts)

        # Run claude CLI
        cmd = [
            "claude",
            "--print",
            "--model", model,
            "--max-tokens", str(max_tokens),
            prompt
        ]

        try:
            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                raise RuntimeError(f"Claude CLI failed: {result.stderr}")

            content = result.stdout.strip()

            # CLI doesn't provide token counts, estimate
            input_tokens = len(prompt.split()) * 4 // 3  # rough estimate
            output_tokens = len(content.split()) * 4 // 3

            return CompletionResult(
                content=content,
                model=model,
                usage=TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens),
                finish_reason="stop"
            )

        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude CLI timed out after 120 seconds")


class OAuthTokenClient(LLMClient):
    """
    Direct API calls using OAuth token from 'claude setup-token'.
    Set CLAUDE_CODE_OAUTH_TOKEN environment variable.
    For containers/CI where interactive login isn't possible.
    """

    API_URL = "https://api.anthropic.com/v1/messages"

    def __init__(self, config: RuntimeConfig | None = None):
        self._config = config or get_config()
        if not self._config.oauth_token:
            raise ValueError("OAuth token not configured. Set CLAUDE_CODE_OAUTH_TOKEN")

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: str | None = None,
    ) -> CompletionResult:
        model = model or self._config.default_model

        # Convert messages to API format
        api_messages = []
        for msg in messages:
            if msg.role != "system":  # System goes in separate field
                api_messages.append({"role": msg.role, "content": msg.content})

        # Collect system messages
        system_text = system or ""
        for msg in messages:
            if msg.role == "system":
                system_text += ("\n" if system_text else "") + msg.content

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": api_messages,
        }
        if system_text:
            payload["system"] = system_text

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {self._config.oauth_token}",
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                },
                json=payload,
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()

        content = data["content"][0]["text"]
        usage = data.get("usage", {})

        return CompletionResult(
            content=content,
            model=data.get("model", model),
            usage=TokenUsage(
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0)
            ),
            finish_reason=data.get("stop_reason")
        )


class OpenRouterClient(LLMClient):
    """
    OpenRouter API via local y-router proxy (Docker).
    Set OPENROUTER_API_KEY environment variable.
    Start y-router: cd ~/git/y-router && docker-compose up -d
    Supports multiple providers (Claude, GPT-4, Gemini, Kimi, etc.)
    """

    def __init__(self, config: RuntimeConfig | None = None):
        self._config = config or get_config()
        if not self._config.openrouter_api_key:
            raise ValueError("OpenRouter API key not configured. Set OPENROUTER_API_KEY")

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: str | None = None,
    ) -> CompletionResult:
        model = model or self._config.default_model

        # y-router accepts Anthropic format at /v1/messages
        api_messages = []
        for msg in messages:
            if msg.role != "system":
                api_messages.append({"role": msg.role, "content": msg.content})

        system_text = system or ""
        for msg in messages:
            if msg.role == "system":
                system_text += ("\n" if system_text else "") + msg.content

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": api_messages,
        }
        if system_text:
            payload["system"] = system_text

        url = f"{self._config.yrouter_base_url}/v1/messages"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {self._config.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                },
                json=payload,
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()

        content = data["content"][0]["text"]
        usage = data.get("usage", {})

        return CompletionResult(
            content=content,
            model=data.get("model", model),
            usage=TokenUsage(
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0)
            ),
            finish_reason=data.get("stop_reason")
        )


class AnthropicAPIClient(LLMClient):
    """
    Traditional API key authentication.
    Set ANTHROPIC_API_KEY environment variable.
    Fallback for users without Max subscription.
    """

    API_URL = "https://api.anthropic.com/v1/messages"

    def __init__(self, config: RuntimeConfig | None = None):
        self._config = config or get_config()
        if not self._config.anthropic_api_key:
            raise ValueError("Anthropic API key not configured. Set ANTHROPIC_API_KEY")

    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: str | None = None,
    ) -> CompletionResult:
        model = model or self._config.default_model

        api_messages = []
        for msg in messages:
            if msg.role != "system":
                api_messages.append({"role": msg.role, "content": msg.content})

        system_text = system or ""
        for msg in messages:
            if msg.role == "system":
                system_text += ("\n" if system_text else "") + msg.content

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": api_messages,
        }
        if system_text:
            payload["system"] = system_text

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.API_URL,
                headers={
                    "x-api-key": self._config.anthropic_api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                },
                json=payload,
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()

        content = data["content"][0]["text"]
        usage = data.get("usage", {})

        return CompletionResult(
            content=content,
            model=data.get("model", model),
            usage=TokenUsage(
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0)
            ),
            finish_reason=data.get("stop_reason")
        )


def create_client(config: RuntimeConfig | None = None) -> LLMClient:
    """
    Create an LLM client based on configuration.
    Auto-detects authentication method if not specified.
    """
    config = config or get_config()

    match config.auth_method:
        case AuthMethod.CLI:
            return ClaudeCLIClient(config)
        case AuthMethod.OAUTH:
            return OAuthTokenClient(config)
        case AuthMethod.OPENROUTER:
            return OpenRouterClient(config)
        case AuthMethod.API_KEY:
            return AnthropicAPIClient(config)
        case _:
            raise ValueError(f"Unknown auth method: {config.auth_method}")


# Default client singleton
_client: LLMClient | None = None


def get_client() -> LLMClient:
    """Get the global LLM client"""
    global _client
    if _client is None:
        _client = create_client()
    return _client


def reset_client() -> None:
    """Reset the global client (for testing)"""
    global _client
    _client = None
