"""
Runtime - LLM-backed agent execution.

This module provides the execution layer for running agents against LLMs:
- Claude via Anthropic API
- Other models via OpenRouter

Key components:
- LLMAgent: Base class for LLM-backed agents
- ClaudeRuntime: Execute agents using Claude
- OpenRouterRuntime: Execute agents using OpenRouter

Usage:
    from runtime import ClaudeRuntime, LLMAgent

    runtime = ClaudeRuntime(api_key="...")
    result = await runtime.execute(my_agent, input_data)
"""

from .base import LLMAgent, AgentContext, AgentResult
from .claude import ClaudeRuntime
from .openrouter import OpenRouterRuntime

__all__ = [
    "LLMAgent",
    "AgentContext",
    "AgentResult",
    "ClaudeRuntime",
    "OpenRouterRuntime",
]
