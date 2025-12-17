"""
Morpheus Adapter Protocol: Interface for LLM backends.

All adapters must implement this protocol to be usable
with the MorpheusGateway.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncIterator, Protocol

if TYPE_CHECKING:
    from ..types import ChatRequest, ChatResponse, StreamChunk


@dataclass
class AdapterConfig:
    """Base configuration for adapters."""

    max_concurrent: int = 3
    timeout_seconds: float = 120.0
    verbose: bool = False
    # Path to auth files (mounted from K8s Secret)
    auth_path: Path = Path("/var/run/secrets/claude")


class Adapter(Protocol):
    """
    Protocol for LLM adapters.

    Implementations must provide:
    - complete: Process a chat completion request
    - stream: Process a streaming chat completion request (optional)
    - is_available: Check if the adapter can process requests
    - health_check: Return health status for monitoring
    """

    async def complete(self, request: "ChatRequest") -> "ChatResponse":
        """
        Process a chat completion request.

        Args:
            request: OpenAI-compatible chat request

        Returns:
            OpenAI-compatible chat response
        """
        ...

    async def stream(self, request: "ChatRequest") -> AsyncIterator["StreamChunk"]:
        """
        Process a streaming chat completion request.

        Args:
            request: OpenAI-compatible chat request

        Yields:
            StreamChunk objects with delta content
        """
        ...

    def is_available(self) -> bool:
        """
        Check if this adapter is available and can process requests.

        Returns:
            True if available, False otherwise
        """
        ...

    def health_check(self) -> dict[str, Any]:
        """
        Return health status for monitoring.

        Returns:
            Dict with adapter health information
        """
        ...

    def supports_streaming(self) -> bool:
        """
        Check if this adapter supports streaming.

        Returns:
            True if streaming is supported, False otherwise
        """
        ...


__all__ = [
    "Adapter",
    "AdapterConfig",
]
