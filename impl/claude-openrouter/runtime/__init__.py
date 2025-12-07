"""
kgents Runtime

LLM-backed execution for kgents agents.

This module provides LLM-backed implementations of bootstrap agents,
enabling semantic reasoning instead of heuristic checks.

Authentication (auto-detected in priority order):
1. Claude CLI (claude login) - Best for Max subscribers
2. OAuth Token (CLAUDE_CODE_OAUTH_TOKEN) - For containers/CI
3. OpenRouter via y-router (OPENROUTER_API_KEY) - Multi-model flexibility
4. Anthropic API Key (ANTHROPIC_API_KEY) - Fallback

Usage:
    from runtime import get_llm_judge, get_llm_sublate, get_llm_contradict

    # Get LLM-backed agents (falls back to heuristic if not configured)
    judge = get_llm_judge()
    sublate = get_llm_sublate()
    contradict = get_llm_contradict()

    # Or use the clients directly
    from runtime import get_client
    client = get_client()
    result = await client.complete([Message(role="user", content="Hello")])
"""

from .config import (
    AuthMethod,
    RuntimeConfig,
    load_config,
    get_config,
    reset_config,
    detect_auth_method,
)

from .messages import (
    Message,
    TokenUsage,
    CompletionResult,
    user,
    assistant,
    system,
)

from .client import (
    LLMClient,
    ClaudeCLIClient,
    OAuthTokenClient,
    OpenRouterClient,
    AnthropicAPIClient,
    create_client,
    get_client,
    reset_client,
)

from .usage import (
    UsageStats,
    UsageTracker,
    get_tracker,
    reset_tracker,
)

from .cache import (
    ResponseCache,
    get_cache,
    reset_cache,
)

from .llm_agents import (
    LLMJudge,
    LLMSublate,
    LLMContradict,
)

# Re-export bootstrap agents for convenience
from bootstrap import (
    judge_agent,
    sublate_agent,
    contradict_agent,
)


# Factory functions that return LLM-backed agents when configured,
# falling back to heuristic versions.

_llm_judge: LLMJudge | None = None
_llm_sublate: LLMSublate | None = None
_llm_contradict: LLMContradict | None = None


def get_llm_judge() -> LLMJudge:
    """
    Get an LLM-backed Judge agent.

    Returns LLMJudge which uses LLM reasoning for principled evaluation.
    Requires authentication to be configured.
    """
    global _llm_judge
    if _llm_judge is None:
        _llm_judge = LLMJudge()
    return _llm_judge


def get_llm_sublate() -> LLMSublate:
    """
    Get an LLM-backed Sublate agent.

    Returns LLMSublate which uses LLM reasoning for Hegelian synthesis.
    Requires authentication to be configured.
    """
    global _llm_sublate
    if _llm_sublate is None:
        _llm_sublate = LLMSublate()
    return _llm_sublate


def get_llm_contradict() -> LLMContradict:
    """
    Get an LLM-backed Contradict agent.

    Returns LLMContradict which uses LLM reasoning for tension detection.
    Requires authentication to be configured.
    """
    global _llm_contradict
    if _llm_contradict is None:
        _llm_contradict = LLMContradict()
    return _llm_contradict


def reset_all() -> None:
    """Reset all singletons (for testing)"""
    global _llm_judge, _llm_sublate, _llm_contradict
    _llm_judge = None
    _llm_sublate = None
    _llm_contradict = None
    reset_config()
    reset_client()
    reset_cache()
    reset_tracker()


__all__ = [
    # Config
    "AuthMethod",
    "RuntimeConfig",
    "load_config",
    "get_config",
    "reset_config",
    "detect_auth_method",

    # Messages
    "Message",
    "TokenUsage",
    "CompletionResult",
    "user",
    "assistant",
    "system",

    # Client
    "LLMClient",
    "ClaudeCLIClient",
    "OAuthTokenClient",
    "OpenRouterClient",
    "AnthropicAPIClient",
    "create_client",
    "get_client",
    "reset_client",

    # Usage
    "UsageStats",
    "UsageTracker",
    "get_tracker",
    "reset_tracker",

    # Cache
    "ResponseCache",
    "get_cache",
    "reset_cache",

    # LLM Agents
    "LLMJudge",
    "LLMSublate",
    "LLMContradict",

    # Factory functions
    "get_llm_judge",
    "get_llm_sublate",
    "get_llm_contradict",
    "reset_all",

    # Re-exported bootstrap agents
    "judge_agent",
    "sublate_agent",
    "contradict_agent",
]
