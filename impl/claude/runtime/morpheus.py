"""
Morpheus Runtime: Use OpenAI SDK against Morpheus Gateway.

This is the cluster-native runtime for kgents LLM access. It uses the
standard OpenAI SDK to communicate with the Morpheus Gateway, which
routes to appropriate backends.

Benefits:
    - Standard API: Works with any OpenAI-compatible endpoint
    - Portable: Same code works in-cluster and locally
    - Centralized Auth: Gateway handles credentials
    - No subprocess spawns: HTTP instead of CLI

Usage:
    # In-cluster (default)
    runtime = MorpheusRuntime()

    # Local development (pointing to NodePort)
    runtime = MorpheusRuntime(base_url="http://localhost:30808/v1")

    # Direct usage
    response = await runtime.chat([
        {"role": "user", "content": "Hello"}
    ])

AGENTESE: world.morpheus.runtime
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, AsyncIterator, Optional, Union

from .base import AgentContext, AgentResult, LLMAgent, Runtime

if TYPE_CHECKING:
    from agents.k.llm import LLMResponse, StreamingLLMResponse


@dataclass
class MorpheusConfig:
    """Configuration for Morpheus Runtime."""

    # Gateway URL (default: in-cluster service)
    base_url: str = "http://morpheus-gateway.kgents.svc.cluster.local:8080/v1"

    # API key (not actually validated by Morpheus, but required by OpenAI SDK)
    api_key: str = "morpheus-internal"

    # Default model (routed by prefix)
    default_model: str = "claude-sonnet-4-20250514"

    # Request timeout in seconds
    timeout: float = 120.0

    @classmethod
    def from_env(cls) -> "MorpheusConfig":
        """Create config from environment variables."""
        return cls(
            base_url=os.environ.get(
                "MORPHEUS_URL",
                os.environ.get(
                    "LLM_ENDPOINT",
                    "http://morpheus-gateway.kgents.svc.cluster.local:8080/v1",
                ),
            ),
            api_key=os.environ.get("MORPHEUS_API_KEY", "morpheus-internal"),
            default_model=os.environ.get("MORPHEUS_DEFAULT_MODEL", "claude-sonnet-4-20250514"),
            timeout=float(os.environ.get("MORPHEUS_TIMEOUT", "120")),
        )


class MorpheusRuntime(Runtime):
    """
    Runtime that speaks OpenAI API to Morpheus Gateway.

    This is the recommended runtime for cluster-native agent execution.
    It provides standard API compatibility while leveraging the gateway
    for authentication and routing.
    """

    def __init__(self, config: Optional[MorpheusConfig] = None) -> None:
        """Initialize Morpheus Runtime.

        Args:
            config: Configuration (uses env vars if None)
        """
        self._config = config or MorpheusConfig.from_env()
        self._client: Any = None  # Lazy-loaded

    def _ensure_client(self) -> Any:
        """Lazy-initialize the OpenAI client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError:
                raise ImportError("openai package not installed. Install with: pip install openai")

            self._client = AsyncOpenAI(
                base_url=self._config.base_url,
                api_key=self._config.api_key,
                timeout=self._config.timeout,
            )
        return self._client

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """
        Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (uses default if None)
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            Response text
        """
        client = self._ensure_client()
        model = model or self._config.default_model

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content
        return content or ""

    async def raw_completion(
        self,
        context: AgentContext,
    ) -> tuple[str, dict[str, Any]]:
        """
        Low-level completion call matching Runtime interface.

        Args:
            context: Agent context with system prompt and messages

        Returns:
            Tuple of (response_text, metadata)
        """
        client = self._ensure_client()

        # Build messages list
        messages: list[dict[str, str]] = []
        if context.system_prompt:
            messages.append({"role": "system", "content": context.system_prompt})
        messages.extend(context.messages)

        response = await client.chat.completions.create(
            model=self._config.default_model,
            messages=messages,
            temperature=context.temperature,
            max_tokens=context.max_tokens,
        )

        text = response.choices[0].message.content
        metadata = {
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            "finish_reason": response.choices[0].finish_reason,
        }

        return text, metadata

    async def execute(self, agent: LLMAgent[Any, Any], input: Any) -> AgentResult[Any]:
        """
        Execute an LLM agent with input.

        Args:
            agent: The agent to execute
            input: Input to the agent

        Returns:
            AgentResult with parsed output
        """
        context = agent.build_prompt(input)
        text, metadata = await self.raw_completion(context)

        try:
            output = agent.parse_response(text)
            return AgentResult(
                output=output,
                raw_response=text,
                model=metadata.get("model", self._config.default_model),
                usage=metadata.get("usage", {}),
                success=True,
            )
        except Exception as e:
            return AgentResult(
                output=None,
                raw_response=text,
                model=metadata.get("model", self._config.default_model),
                usage=metadata.get("usage", {}),
                success=False,
                error=str(e),
            )


class MorpheusLLMClient:
    """
    Simple LLM client interface for K-gent Soul.

    This mirrors the interface expected by K-gent's LLMClient protocol,
    but routes through Morpheus Gateway.

    Usage:
        from runtime.morpheus import MorpheusLLMClient

        client = MorpheusLLMClient()
        response = await client.generate(
            system="You are K-gent...",
            user="I'm stuck on architecture",
            temperature=0.6,
        )
    """

    def __init__(
        self,
        config: Optional[MorpheusConfig] = None,
        model: Optional[str] = None,
    ) -> None:
        """Initialize Morpheus LLM client.

        Args:
            config: Runtime configuration (uses env if None)
            model: Override model (uses config default if None)
        """
        self._config = config or MorpheusConfig.from_env()
        self._model = model or self._config.default_model
        self._runtime = MorpheusRuntime(self._config)

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> "LLMResponse":
        """Generate a response from the LLM.

        Args:
            system: System prompt
            user: User message
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            LLMResponse with text and metadata
        """
        from agents.k.llm import LLMResponse

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        text = await self._runtime.chat(
            messages=messages,
            model=self._model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Estimate tokens (rough approximation)
        tokens_used = len(text.split()) * 2

        return LLMResponse(
            text=text,
            model=self._model,
            tokens_used=tokens_used,
        )

    async def generate_stream(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> AsyncIterator[Union[str, "StreamingLLMResponse"]]:
        """Generate a streaming response from the LLM.

        Uses OpenAI-compatible streaming API with SSE (Server-Sent Events).

        Yields:
            str: Text chunks as they are generated
            StreamingLLMResponse: Final item with accumulated text and token counts

        Example:
            async for item in client.generate_stream(...):
                if isinstance(item, str):
                    print(item, end="", flush=True)
                else:
                    print(f"\\nTokens used: {item.tokens_used}")
        """
        from agents.k.llm import StreamingLLMResponse

        client = self._runtime._ensure_client()

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        accumulated_text = ""
        prompt_tokens = 0
        completion_tokens = 0
        model_name = self._model

        try:
            # Request streaming with usage info in final chunk
            stream = await client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                stream_options={"include_usage": True},
            )

            async for chunk in stream:
                # Check for content delta
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        accumulated_text += delta.content
                        yield delta.content

                # Capture usage from final chunk (when include_usage=True)
                if chunk.usage is not None:
                    prompt_tokens = chunk.usage.prompt_tokens
                    completion_tokens = chunk.usage.completion_tokens

                # Capture model name
                if chunk.model:
                    model_name = chunk.model

        except Exception:
            # On streaming error, fall back to non-streaming
            # This handles cases where the gateway doesn't support streaming
            if accumulated_text:
                # Partial stream succeeded, yield what we have
                pass
            else:
                # No stream data, fall back to generate()
                response = await self.generate(
                    system=system,
                    user=user,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                yield response.text
                yield StreamingLLMResponse(
                    text=response.text,
                    tokens_used=response.tokens_used,
                    model=response.model,
                )
                return

        # Yield final StreamingLLMResponse with token counts
        total_tokens = prompt_tokens + completion_tokens
        if total_tokens == 0:
            # Estimate if API didn't provide usage
            total_tokens = len(accumulated_text.split()) * 2

        yield StreamingLLMResponse(
            text=accumulated_text,
            tokens_used=total_tokens,
            model=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            raw_metadata={
                "streaming": True,
                "had_usage_info": prompt_tokens > 0 or completion_tokens > 0,
            },
        )


def create_runtime(
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> MorpheusRuntime:
    """
    Create a Morpheus Runtime with optional overrides.

    Args:
        base_url: Gateway URL override
        model: Default model override

    Returns:
        Configured MorpheusRuntime
    """
    config = MorpheusConfig.from_env()
    if base_url:
        config.base_url = base_url
    if model:
        config.default_model = model
    return MorpheusRuntime(config)
