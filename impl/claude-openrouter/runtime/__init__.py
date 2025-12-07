"""
Runtime - LLM-backed agent execution.

This module provides the execution layer for running agents against LLMs:
- Claude via Anthropic API
- Claude via Claude Code CLI (OAuth authenticated)
- Other models via OpenRouter

Key components:
- LLMAgent: Base class for LLM-backed agents
- ClaudeRuntime: Execute agents using Claude API (requires API key)
- ClaudeCLIRuntime: Execute agents using Claude Code CLI (uses OAuth)
- OpenRouterRuntime: Execute agents using OpenRouter

Usage:
    from runtime import ClaudeCLIRuntime, LLMAgent

    runtime = ClaudeCLIRuntime()  # Uses claude CLI, no API key needed
    result = await runtime.execute(my_agent, input_data)
"""

from .base import LLMAgent, AgentContext, AgentResult
from .claude import ClaudeRuntime
from .cli import ClaudeCLIRuntime, ParseError
from .openrouter import OpenRouterRuntime

__all__ = [
    "LLMAgent",
    "AgentContext",
    "AgentResult",
    "ClaudeRuntime",
    "ClaudeCLIRuntime",
    "OpenRouterRuntime",
    "ParseError",
]
