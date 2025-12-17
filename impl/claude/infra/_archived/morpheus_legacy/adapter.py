"""
Claude CLI Adapter: Wraps ClaudeCLIRuntime with concurrency control.

This adapter enables Morpheus to use the authenticated Claude CLI
for LLM calls while managing concurrency via semaphore.

Architecture:
    Morpheus → ClaudeCLIAdapter → asyncio.Semaphore → ClaudeCLIRuntime → `claude -p`

The semaphore prevents spawning too many concurrent subprocesses,
which would overwhelm the system and hit rate limits.

Future: Warm pool pattern with persistent `claude` REPL for lower latency.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .types import ChatRequest, ChatResponse


@dataclass
class AdapterConfig:
    """Configuration for Claude CLI adapter."""

    max_concurrent: int = 3
    timeout_seconds: float = 120.0
    verbose: bool = False
    # Path to Claude auth files (mounted from K8s Secret)
    auth_path: Path = Path("/var/run/secrets/claude")


class ClaudeCLIAdapter:
    """
    Adapter from OpenAI-compatible requests to ClaudeCLIRuntime.

    Uses asyncio.Semaphore for concurrency control to prevent
    overwhelming the system with subprocess spawns.
    """

    def __init__(self, config: Optional[AdapterConfig] = None) -> None:
        self._config = config or AdapterConfig()
        self._semaphore = asyncio.Semaphore(self._config.max_concurrent)
        self._runtime: Any = None  # Lazy-loaded
        self._request_count = 0

    @property
    def request_count(self) -> int:
        """Total requests processed."""
        return self._request_count

    def _ensure_auth_env(self) -> None:
        """Set up Claude CLI auth from mounted secret."""
        auth_path = self._config.auth_path

        if auth_path.exists():
            # Set CLAUDE_CONFIG_DIR to point to secret mount
            os.environ["CLAUDE_CONFIG_DIR"] = str(auth_path)
        # If not in K8s, fall back to default ~/.claude

    def _ensure_runtime(self) -> None:
        """Lazy-initialize the ClaudeCLIRuntime."""
        if self._runtime is None:
            self._ensure_auth_env()
            from runtime.cli import ClaudeCLIRuntime

            self._runtime = ClaudeCLIRuntime(
                timeout=self._config.timeout_seconds,
                verbose=self._config.verbose,
            )

    async def complete(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat completion request.

        Acquires semaphore before executing to limit concurrency.
        """
        async with self._semaphore:
            self._request_count += 1
            return await self._execute(request)

    async def _execute(self, request: ChatRequest) -> ChatResponse:
        """Execute the completion via ClaudeCLIRuntime."""
        self._ensure_runtime()

        # Build AgentContext from request
        from runtime.base import AgentContext

        # Extract system message and user messages
        system_prompt = ""
        messages: list[dict[str, str]] = []

        for msg in request.messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                messages.append({"role": msg.role, "content": msg.content})

        context = AgentContext(
            system_prompt=system_prompt,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        # Execute via runtime
        text, metadata = await self._runtime.raw_completion(context)

        # Build response
        # Estimate tokens (rough approximation)
        prompt_tokens = sum(len(m.content.split()) for m in request.messages) * 2
        completion_tokens = len(text.split()) * 2

        return ChatResponse.from_text(
            text=text,
            model=request.model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    def is_available(self) -> bool:
        """Check if Claude CLI is available."""
        return shutil.which("claude") is not None

    def health_check(self) -> dict[str, Any]:
        """Return health status for monitoring."""
        return {
            "adapter": "claude-cli",
            "available": self.is_available(),
            "max_concurrent": self._config.max_concurrent,
            "current_requests": self._config.max_concurrent
            - self._semaphore._value,  # Active requests
            "total_requests": self._request_count,
            "timeout_seconds": self._config.timeout_seconds,
        }


class MockAdapter:
    """Mock adapter for testing without real LLM calls."""

    def __init__(
        self,
        responses: Optional[list[str]] = None,
        default_response: str = "Mock response from Morpheus",
    ) -> None:
        self._responses = list(responses) if responses else []
        self._default_response = default_response
        self._request_count = 0
        self._history: list[ChatRequest] = []

    async def complete(self, request: ChatRequest) -> ChatResponse:
        """Return mock response."""
        self._request_count += 1
        self._history.append(request)

        if self._responses:
            text = self._responses.pop(0)
        else:
            text = self._default_response

        return ChatResponse.from_text(
            text=text,
            model=request.model,
            prompt_tokens=100,
            completion_tokens=50,
        )

    def is_available(self) -> bool:
        return True

    def health_check(self) -> dict[str, Any]:
        return {
            "adapter": "mock",
            "available": True,
            "total_requests": self._request_count,
        }

    @property
    def history(self) -> list[ChatRequest]:
        """Request history for testing assertions."""
        return self._history
