"""
OpenRouter Runtime - Execute agents via OpenRouter API.

OpenRouter provides access to multiple LLM providers through a unified API.
"""

import os
from typing import Any, TypeVar

from .base import Runtime, LLMAgent, AgentContext, AgentResult

A = TypeVar("A")
B = TypeVar("B")


class OpenRouterRuntime(Runtime):
    """
    Runtime for executing LLM agents via OpenRouter.

    Usage:
        runtime = OpenRouterRuntime(model="anthropic/claude-3.5-sonnet")
        result = await runtime.execute(my_agent, input_data)
    """

    BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        site_url: str | None = None,
        site_name: str | None = None,
    ):
        """
        Initialize OpenRouter runtime.

        Args:
            api_key: OpenRouter API key. Defaults to OPENROUTER_API_KEY env var.
            model: Model to use. Defaults to anthropic/claude-3.5-sonnet.
            site_url: Your site URL for rankings (optional).
            site_name: Your site name for rankings (optional).
        """
        self._api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self._model = model or self.DEFAULT_MODEL
        self._site_url = site_url
        self._site_name = site_name
        self._client = None

    def _ensure_client(self):
        """Lazy-initialize the HTTP client."""
        if self._client is None:
            try:
                import httpx
                self._client = httpx.AsyncClient(
                    base_url=self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                        **({"HTTP-Referer": self._site_url} if self._site_url else {}),
                        **({"X-Title": self._site_name} if self._site_name else {}),
                    },
                    timeout=120.0,
                )
            except ImportError:
                raise ImportError(
                    "httpx package required. Install with: pip install httpx"
                )
        return self._client

    async def raw_completion(
        self,
        context: AgentContext,
    ) -> tuple[str, dict[str, Any]]:
        """Execute raw completion via OpenRouter API."""
        client = self._ensure_client()

        # Build messages with system prompt
        messages = [
            {"role": "system", "content": context.system_prompt},
            *context.messages,
        ]

        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": context.max_tokens,
            "temperature": context.temperature,
        }

        response = await client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        metadata = {
            "model": data.get("model", self._model),
            "usage": {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            },
            "finish_reason": data["choices"][0].get("finish_reason"),
        }

        return text, metadata

    async def execute(
        self,
        agent: LLMAgent[A, B],
        input: A,
    ) -> AgentResult[B]:
        """Execute an LLM agent with OpenRouter."""
        context = agent.build_prompt(input)
        response_text, metadata = await self.raw_completion(context)

        output = agent.parse_response(response_text)

        return AgentResult(
            output=output,
            raw_response=response_text,
            model=metadata["model"],
            usage=metadata["usage"],
        )

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
