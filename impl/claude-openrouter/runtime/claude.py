"""
Claude Runtime - Execute agents using Anthropic's Claude API.

Supports two authentication methods:
1. API Key: Set ANTHROPIC_API_KEY or pass api_key
2. OAuth Token: Set CLAUDE_CODE_OAUTH_TOKEN or pass auth_token
   (Used by Claude Code CLI for delegated authentication)
"""

import os
from typing import Any, TypeVar, Protocol

from .base import Runtime, LLMAgent, AgentContext, AgentResult

A = TypeVar("A")
B = TypeVar("B")


class AsyncAnthropicClient(Protocol):
    """Protocol for Anthropic async clients to enable dependency injection."""
    
    async def messages_create(
        self,
        *,
        model: str,
        max_tokens: int,
        system: str,
        messages: list[dict[str, Any]],
    ) -> Any:
        """Create a message completion."""
        ...


class ClaudeRuntime(Runtime):
    """
    Runtime for executing LLM agents via Claude.

    Usage:
        # With API key (default)
        runtime = ClaudeRuntime()

        # With OAuth token (Claude Code CLI)
        runtime = ClaudeRuntime(auth_token=os.environ["CLAUDE_CODE_OAUTH_TOKEN"])

        # With custom client (for testing)
        runtime = ClaudeRuntime(client=mock_client)

        result = await runtime.execute(my_agent, input_data)
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(
        self,
        api_key: str | None = None,
        auth_token: str | None = None,
        model: str | None = None,
        client: Any | None = None,
    ):
        """
        Initialize Claude runtime.

        Args:
            api_key: Anthropic API key. Defaults to ANTHROPIC_API_KEY env var.
            auth_token: OAuth token (e.g., from Claude Code CLI).
                       Defaults to CLAUDE_CODE_OAUTH_TOKEN env var.
                       Takes precedence over api_key if both are set.
            model: Model to use. Defaults to claude-sonnet-4-20250514.
            client: Pre-configured Anthropic client. If provided, api_key and
                   auth_token are ignored. Useful for testing and custom configs.
        """
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._auth_token = auth_token or os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
        self._model = model or self.DEFAULT_MODEL
        self._client = client

    def _ensure_client(self):
        """Lazy-initialize the Anthropic client."""
        if self._client is None:
            try:
                import anthropic
            except ImportError:
                raise ImportError(
                    "anthropic package required. Install with: pip install anthropic"
                )

            # OAuth token takes precedence over API key
            if self._auth_token:
                self._client = anthropic.AsyncAnthropic(auth_token=self._auth_token)
            elif self._api_key:
                self._client = anthropic.AsyncAnthropic(api_key=self._api_key)
            else:
                raise ValueError(
                    "No authentication configured. Set ANTHROPIC_API_KEY, "
                    "CLAUDE_CODE_OAUTH_TOKEN, or pass api_key/auth_token to ClaudeRuntime."
                )
        return self._client

    async def raw_completion(
        self,
        context: AgentContext,
    ) -> tuple[str, dict[str, Any]]:
        """Execute raw completion via Claude API."""
        client = self._ensure_client()

        response = await client.messages.create(
            model=self._model,
            max_tokens=context.max_tokens,
            system=context.system_prompt,
            messages=context.messages,
        )

        text = response.content[0].text
        metadata = {
            "model": response.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            "stop_reason": response.stop_reason,
        }

        return text, metadata

    async def execute(
        self,
        agent: LLMAgent[A, B],
        input: A,
    ) -> AgentResult[B]:
        """Execute an LLM agent with Claude."""
        context = agent.build_prompt(input)
        response_text, metadata = await self.raw_completion(context)

        output = agent.parse_response(response_text)

        return AgentResult(
            output=output,
            raw_response=response_text,
            model=metadata["model"],
            usage=metadata["usage"],
        )
