"""
Observer-dependent LLM model selection.

Per spec/protocols/chat-morpheus-synergy.md Part III:
Different observers get different LLM behavior. This is the core AGENTESE insight—
the same path yields different results based on who is observing.

Model selection is a functor from Observer to MorpheusConfig:
    ModelSelector : Observer → MorpheusConfig
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

    from .session import ChatSession


# === Model Options (for UI) ===


@dataclass(frozen=True)
class ModelOption:
    """A selectable model option with metadata."""

    id: str
    name: str
    description: str
    tier: str  # "fast", "balanced", "powerful"


# Available models for user selection
MODEL_OPTIONS: list[ModelOption] = [
    ModelOption(
        id="claude-3-haiku-20240307",
        name="Haiku",
        description="Fast responses, lower cost",
        tier="fast",
    ),
    ModelOption(
        id="claude-sonnet-4-20250514",
        name="Sonnet",
        description="Balanced speed and capability",
        tier="balanced",
    ),
    ModelOption(
        id="claude-opus-4-20250514",
        name="Opus",
        description="Most capable, highest quality",
        tier="powerful",
    ),
]


def can_switch_model(session: "ChatSession", observer: "Umwelt") -> bool:
    """
    Check if model switching is allowed for this session.

    Model switching is allowed when:
    1. It's a personal session (self.* path) - owner can always switch
    2. It's a one-on-one session (citizen paths)
    3. Observer has explicit non-guest archetype

    Args:
        session: The chat session
        observer: The current observer

    Returns:
        True if model switching is allowed
    """
    node_path = session.node_path

    # Personal sessions (self.*) always allow model switching
    # The owner of the session should be able to pick their model
    if node_path.startswith("self."):
        return True

    # Citizen conversations allowed (user is sole observer)
    if "citizen" in node_path:
        return True

    # For other paths, check archetype
    archetype = _get_archetype(observer)

    # Guests can't switch models on non-personal paths
    if archetype == "guest":
        return False

    # Allow for all other archetypes
    return True


def get_model_options() -> list[ModelOption]:
    """Get the list of available model options."""
    return MODEL_OPTIONS


# === Configuration Types ===


@dataclass(frozen=True)
class MorpheusConfig:
    """Configuration for Morpheus request."""

    model: str = "claude-sonnet-4-20250514"
    temperature: float = 0.7
    max_tokens: int = 4096


# === Model Selector Protocol ===


class ModelSelector(Protocol):
    """Protocol for model selection strategies."""

    def __call__(self, observer: "Umwelt", node_path: str) -> MorpheusConfig:
        """Select model configuration based on observer and path."""
        ...


# === Default Implementation ===


def default_model_selector(observer: "Umwelt", node_path: str) -> MorpheusConfig:
    """
    Select LLM configuration based on observer.

    This is observer-dependent behavior—the core AGENTESE insight.
    Different observers get different models, temperatures, and token limits.

    Observer Archetypes → Model Selection:
    - system: claude-opus (highest capability, lower temp)
    - developer: claude-sonnet (balanced)
    - guest: claude-haiku (cost-efficient, limited tokens)
    - citizen (NPC): claude-haiku (high temp for personality)
    """
    # Extract archetype from observer
    archetype = _get_archetype(observer)

    # Match on (archetype, node_path) pairs
    match (archetype, node_path):
        # System observers get highest capability
        case ("system", _):
            return MorpheusConfig(
                model="claude-opus-4-20250514",
                temperature=0.3,
                max_tokens=8192,
            )

        # Developer chatting with soul
        case ("developer", path) if "soul" in path:
            return MorpheusConfig(
                model="claude-sonnet-4-20250514",
                temperature=0.7,
                max_tokens=4096,
            )

        # Guest observers get cost-efficient model
        case ("guest", _):
            return MorpheusConfig(
                model="claude-3-haiku-20240307",
                temperature=0.5,
                max_tokens=1024,
            )

        # Citizen conversations get haiku with high temp for personality
        case (_, path) if "citizen" in path:
            return MorpheusConfig(
                model="claude-3-haiku-20240307",
                temperature=0.8,
                max_tokens=2048,
            )

        # Default: sonnet with balanced settings
        case _:
            return MorpheusConfig(
                model="claude-sonnet-4-20250514",
                temperature=0.7,
                max_tokens=4096,
            )


def _get_archetype(observer: "Umwelt") -> str:
    """Extract archetype from observer umwelt."""
    try:
        meta = observer.meta
        return getattr(meta, "archetype", "guest")
    except Exception:
        return "guest"


# === Budget-Aware Selector ===


@dataclass(frozen=True)
class TokenBudget:
    """Token budget for an observer tier."""

    daily_tokens: int
    per_request: int


# Tier budgets (from spec Part III §3.3)
TIER_BUDGETS = {
    "free": TokenBudget(daily_tokens=10_000, per_request=1024),
    "pro": TokenBudget(daily_tokens=100_000, per_request=4096),
    "enterprise": TokenBudget(daily_tokens=1_000_000, per_request=16384),
}

FREE_BUDGET = TokenBudget(daily_tokens=10_000, per_request=1024)


def budget_aware_selector(observer: "Umwelt", node_path: str) -> MorpheusConfig:
    """
    Model selector that respects token budgets.

    Derives budget from observer tier, then selects model accordingly.
    """
    base_config = default_model_selector(observer, node_path)

    # Get tier from observer
    tier = _get_tier(observer)
    budget = TIER_BUDGETS.get(tier, FREE_BUDGET)

    # Cap max_tokens to tier budget
    capped_tokens = min(base_config.max_tokens, budget.per_request)

    return MorpheusConfig(
        model=base_config.model,
        temperature=base_config.temperature,
        max_tokens=capped_tokens,
    )


def _get_tier(observer: "Umwelt") -> str:
    """Extract tier from observer capabilities."""
    try:
        meta = observer.meta
        capabilities = getattr(meta, "capabilities", {})
        return capabilities.get("tier", "free")
    except Exception:
        return "free"


__all__ = [
    "MorpheusConfig",
    "ModelSelector",
    "ModelOption",
    "MODEL_OPTIONS",
    "default_model_selector",
    "budget_aware_selector",
    "can_switch_model",
    "get_model_options",
    "TokenBudget",
    "TIER_BUDGETS",
]
