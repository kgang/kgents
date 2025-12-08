"""
Claude Runtime - Execute agents using Anthropic's Claude API.

Supports two authentication methods:
1. API Key: Set ANTHROPIC_API_KEY or pass api_key
2. OAuth Token: Set CLAUDE_CODE_OAUTH_TOKEN or pass auth_token
   (Used by Claude Code CLI for delegated authentication)
"""

import os
import logging
import time
import uuid
from typing import Any, TypeVar, Protocol

from .base import Runtime, LLMAgent, AgentContext, AgentResult, with_retry, TransientError, PermanentError

A = TypeVar("A")
B = TypeVar("B")

logger = logging.getLogger(__name__)


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
        max_retries: int = 3,
        backoff_base: float = 2.0,
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
            max_retries: Maximum retry attempts on transient errors (default: 3).
            backoff_base: Base for exponential backoff in seconds (default: 2.0).
        """
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._auth_token = auth_token or os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
        self._model = model or self.DEFAULT_MODEL
        self._client = client
        self._max_retries = max_retries
        self._backoff_base = backoff_base

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

    def _is_transient_error(self, error: Exception) -> bool:
        """
        Classify if an error is transient (should retry) or permanent.

        Transient errors: rate limits, timeouts, temporary network issues.
        Permanent errors: auth failures, invalid requests, content filtering.
        """
        error_str = str(error).lower()
        error_type = type(error).__name__

        # Already classified
        if isinstance(error, TransientError):
            return True
        if isinstance(error, PermanentError):
            return False

        # Rate limit errors - always transient
        if "rate" in error_str and "limit" in error_str:
            return True
        if "429" in error_str or error_type == "RateLimitError":
            return True

        # Timeout errors - transient
        if "timeout" in error_str or error_type in ("TimeoutError", "asyncio.TimeoutError"):
            return True

        # Overloaded errors - transient
        if "overloaded" in error_str or "529" in error_str:
            return True

        # Connection errors - transient
        if any(term in error_str for term in ["connection", "network", "dns"]):
            return True

        # Auth errors - permanent
        if any(term in error_str for term in ["auth", "unauthorized", "forbidden", "401", "403"]):
            return False

        # Invalid request errors - permanent
        if any(term in error_str for term in ["invalid", "malformed", "400"]):
            return False

        # Content filter errors - permanent
        if "content" in error_str and "filter" in error_str:
            return False

        # Default to transient for unknown errors (conservative)
        return True

    async def raw_completion(
        self,
        context: AgentContext,
    ) -> tuple[str, dict[str, Any]]:
        """
        Execute raw completion via Claude API with retry logic.

        Uses Fix pattern with exponential backoff for transient errors.
        """
        trace_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        logger.info(
            "raw_completion.start",
            extra={
                "trace_id": trace_id,
                "model": self._model,
                "max_tokens": context.max_tokens,
                "message_count": len(context.messages),
            },
        )

        async def _attempt() -> tuple[str, dict[str, Any]]:
            """Single attempt at completion."""
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
                "trace_id": trace_id,
            }

            return text, metadata

        try:
            # Use Fix pattern retry with exponential backoff
            result, attempts = await with_retry(
                _attempt,
                max_attempts=self._max_retries,
                backoff_base=self._backoff_base,
                is_transient=self._is_transient_error,
            )

            elapsed = time.perf_counter() - start_time
            logger.info(
                "raw_completion.success",
                extra={
                    "trace_id": trace_id,
                    "model": result[1]["model"],
                    "input_tokens": result[1]["usage"]["input_tokens"],
                    "output_tokens": result[1]["usage"]["output_tokens"],
                    "stop_reason": result[1]["stop_reason"],
                    "elapsed_seconds": round(elapsed, 3),
                    "retry_attempts": attempts,
                },
            )

            return result

        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.error(
                "raw_completion.error",
                extra={
                    "trace_id": trace_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "elapsed_seconds": round(elapsed, 3),
                },
                exc_info=True,
            )
            raise

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
