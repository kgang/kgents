"""
Morpheus Gateway: OpenAI-compatible LLM Router.

Morpheus provides a standard API (OpenAI-compatible) that routes
requests to multiple LLM backends based on model prefix.

Architecture:
    POST /v1/chat/completions
         ↓
    Route by model prefix:
        claude-*    → Anthropic API / Claude CLI
        gpt-*       → OpenAI API
        openrouter/* → OpenRouter
        ollama/*    → Local Ollama

Principles:
    - Heterarchical: Standard APIs, portable agents
    - Tasteful: Thin adapter, not infrastructure theater
    - Generative: OpenAI spec compresses multiple implementations

AGENTESE: world.morpheus.gateway
"""

from .adapter import ClaudeCLIAdapter
from .server import MorpheusGateway, create_app
from .types import (
    ChatChoice,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    Usage,
)

__all__ = [
    "MorpheusGateway",
    "create_app",
    "ClaudeCLIAdapter",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ChatChoice",
    "Usage",
]
