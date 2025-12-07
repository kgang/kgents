"""
Claude Runtime - Execute agents using Anthropic's Claude API.
"""

import os
from typing import Any, TypeVar

from .base import Runtime, LLMAgent, AgentContext, AgentResult

A = TypeVar("A")
B = TypeVar("B")


class ClaudeRuntime(Runtime):
    """
    Runtime for executing LLM agents via Claude.

    Usage:
        runtime = ClaudeRuntime()
        result = await runtime.execute(my_agent, input_data)
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        """
        Initialize Claude runtime.

        Args:
            api_key: Anthropic API key. Defaults to ANTHROPIC_API_KEY env var.
            model: Model to use. Defaults to claude-sonnet-4-20250514.
        """
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._model = model or self.DEFAULT_MODEL
        self._client = None

    def _ensure_client(self):
        """Lazy-initialize the Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(api_key=self._api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package required. Install with: pip install anthropic"
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
