"""
K-gent LLM Client: Abstraction for LLM-backed K-gent operations.

This provides a simple interface for K-gent to call LLMs without
needing to know about the full LLMAgent/Runtime machinery.

The client supports:
- Direct text generation with system/user prompts
- Temperature control per mode
- Token budget awareness

DEVELOPER NOTE: Runtime Selection
=================================
The client prefers Morpheus Gateway (cluster-native) over CLI:

1. MorpheusLLMClient (preferred):
   - Uses HTTP/OpenAI-compatible API
   - No subprocess spawns
   - Works in-cluster via `http://morpheus-gateway:8080/v1`
   - Enabled when MORPHEUS_URL is set or gateway is reachable

2. ClaudeCLIRuntime (fallback):
   - Uses `claude -p` subprocess
   - Authenticated via Claude Code CLI's OAuth flow
   - For local development without Morpheus

Check availability with `has_llm_credentials()` or `morpheus_available()`.

Usage:
    llm = create_llm_client()  # Auto-detects best backend
    response = await llm.generate(
        system="You are K-gent...",
        user="I'm stuck on architecture",
        temperature=0.6,
    )

    # Force specific backend:
    llm = create_llm_client(prefer_morpheus=False)  # Force CLI
"""

from __future__ import annotations

import os
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Protocol, cast


@dataclass
class LLMResponse:
    """Response from LLM generation."""

    text: str
    model: str = ""
    tokens_used: int = 0
    raw_metadata: Optional[dict[str, Any]] = None


class LLMClient(Protocol):
    """Protocol for LLM clients used by K-gent."""

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        ...


class BaseLLMClient(ABC):
    """Base class for LLM clients."""

    @abstractmethod
    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass


class ClaudeLLMClient(BaseLLMClient):
    """
    LLM client using ClaudeCLIRuntime.

    IMPORTANT: This uses the Claude Code CLI (`claude -p`) which is
    already authenticated via OAuth. Do NOT use ClaudeRuntime directly
    as it requires API keys or OAuth tokens that the Anthropic API
    doesn't accept directly.
    """

    def __init__(
        self,
        timeout: float = 120.0,
        verbose: bool = False,
    ):
        """Initialize Claude LLM client.

        Args:
            timeout: Timeout in seconds for CLI execution.
            verbose: Print progress messages during execution.
        """
        self._timeout = timeout
        self._verbose = verbose
        self._runtime: Any = None

    def _ensure_runtime(self) -> None:
        """Lazy-initialize the runtime."""
        if self._runtime is None:
            from runtime.cli import ClaudeCLIRuntime

            self._runtime = ClaudeCLIRuntime(
                timeout=self._timeout,
                verbose=self._verbose,
            )

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> LLMResponse:
        """Generate a response using ClaudeCLIRuntime.

        Note: The CLI doesn't support temperature/max_tokens directly,
        but we include them in the prompt context for documentation.
        """
        from runtime.base import AgentContext

        self._ensure_runtime()

        context = AgentContext(
            system_prompt=system,
            messages=[{"role": "user", "content": user}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        text, metadata = await self._runtime.raw_completion(context)

        return LLMResponse(
            text=text,
            model=metadata.get("model", "claude-cli"),
            tokens_used=metadata.get("usage", {}).get("total_tokens", 0),
            raw_metadata=metadata,
        )


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing."""

    def __init__(
        self,
        responses: Optional[list[str]] = None,
        default_response: str = "Mock response",
    ):
        """Initialize mock client.

        Args:
            responses: Queue of responses to return (consumed in order).
            default_response: Response when queue is empty.
        """
        self._responses = list(responses) if responses else []
        self._default_response = default_response
        self._call_history: list[dict[str, Any]] = []

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> LLMResponse:
        """Return mock response."""
        self._call_history.append(
            {
                "system": system,
                "user": user,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )

        if self._responses:
            text = self._responses.pop(0)
        else:
            text = self._default_response

        return LLMResponse(
            text=text,
            model="mock-model",
            tokens_used=len(text.split()) * 2,  # Rough estimate
        )

    @property
    def call_history(self) -> list[dict[str, Any]]:
        """Get history of calls made to this client."""
        return self._call_history

    @property
    def call_count(self) -> int:
        """Get number of calls made to this client."""
        return len(self._call_history)


def morpheus_available() -> bool:
    """Check if Morpheus Gateway is available.

    Returns True if:
    1. MORPHEUS_URL environment variable is set, OR
    2. LLM_ENDPOINT environment variable is set

    Note: We don't do a connectivity check here to avoid latency.
    The actual connection will fail gracefully if the gateway is down.
    """
    return bool(os.environ.get("MORPHEUS_URL") or os.environ.get("LLM_ENDPOINT"))


def create_llm_client(
    timeout: float = 120.0,
    verbose: bool = False,
    mock: bool = False,
    mock_responses: Optional[list[str]] = None,
    prefer_morpheus: bool = True,
) -> LLMClient:
    """Create an LLM client for K-gent.

    The client selection follows this precedence:
    1. Mock client (if mock=True)
    2. MorpheusLLMClient (if prefer_morpheus=True and MORPHEUS_URL/LLM_ENDPOINT set)
    3. ClaudeLLMClient (fallback for local development)

    Args:
        timeout: Timeout in seconds for execution.
        verbose: Print progress messages during execution.
        mock: If True, return a mock client.
        mock_responses: Responses for mock client.
        prefer_morpheus: If True, prefer Morpheus Gateway when available.

    Returns:
        An LLM client instance.

    Environment Variables:
        MORPHEUS_URL: URL for Morpheus Gateway (e.g., http://morpheus-gateway:8080/v1)
        LLM_ENDPOINT: Alternative name for MORPHEUS_URL
    """
    if mock:
        return MockLLMClient(responses=mock_responses)

    # Prefer Morpheus if available (cluster-native)
    if prefer_morpheus and morpheus_available():
        from runtime.morpheus import MorpheusLLMClient

        return cast(LLMClient, MorpheusLLMClient())

    # Fallback to CLI (local development)
    return ClaudeLLMClient(
        timeout=timeout,
        verbose=verbose,
    )


def has_llm_credentials() -> bool:
    """Check if any LLM client is available.

    Returns True if either:
    1. Morpheus Gateway is configured (MORPHEUS_URL or LLM_ENDPOINT), OR
    2. Claude CLI is installed
    """
    return morpheus_available() or shutil.which("claude") is not None
