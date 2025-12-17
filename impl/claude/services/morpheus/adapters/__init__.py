"""
Morpheus Adapters: LLM backend implementations.

Each adapter implements the Adapter protocol to provide
completion functionality from different LLM backends.

Available adapters:
- ClaudeCLIAdapter: Uses Claude CLI subprocess
- MockAdapter: Testing adapter with queued responses
"""

from .base import Adapter, AdapterConfig
from .claude_cli import ClaudeCLIAdapter
from .mock import MockAdapter

__all__ = [
    "Adapter",
    "AdapterConfig",
    "ClaudeCLIAdapter",
    "MockAdapter",
]
