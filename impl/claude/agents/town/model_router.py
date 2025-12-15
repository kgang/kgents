"""
Unified Model Router for Agent Town.

Single source of truth for model selection across all operations.

Per unified-v2.md Track B: Haiku-first routing with tier-based degradation.

This module consolidates model routing from:
- paywall.py: ACTION_MODELS
- dialogue_engine.py: DialogueBudgetConfig.model_routing
- lens.py: LOD_MODEL_MAP

Usage:
    from agents.town.model_router import select_model, ModelSelection

    selection = select_model(
        action="lod3",
        tier="RESIDENT",
        remaining_credits=50,
    )
    print(selection.model)  # "haiku"
    print(selection.reason)  # "Tier RESIDENT: Haiku for LOD 3"
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ModelName(str, Enum):
    """Available LLM models."""

    HAIKU = "haiku"
    SONNET = "sonnet"
    OPUS = "opus"
    TEMPLATE = "template"  # No LLM, template fallback
    CACHED = "cached"  # No LLM, cache hit
    NONE = "none"  # No model needed (e.g., branching)


@dataclass(frozen=True)
class ModelSelection:
    """Result of model selection."""

    model: str
    reason: str
    degraded: bool = False  # True if model was downgraded due to budget/tier


# =============================================================================
# Default Model Mappings (unified source of truth)
# =============================================================================

# LOD model routing (from lens.py)
LOD_MODELS: dict[int, ModelName] = {
    0: ModelName.CACHED,  # Silhouette - no LLM
    1: ModelName.HAIKU,  # Posture - quick inference
    2: ModelName.HAIKU,  # Cosmotechnics - dialogue synthesis
    3: ModelName.HAIKU,  # Memory - retrieval (spec says Sonnet, but Haiku-first)
    4: ModelName.SONNET,  # Psyche - deep psychological
    5: ModelName.OPUS,  # Abyss - the irreducible mystery
}

# Operation model routing (from dialogue_engine.py)
OPERATION_MODELS: dict[str, ModelName] = {
    "greet": ModelName.HAIKU,
    "gossip": ModelName.HAIKU,
    "trade": ModelName.SONNET,
    "council": ModelName.SONNET,
    "solo_reflect": ModelName.HAIKU,
}

# INHABIT model routing (from paywall.py)
INHABIT_MODELS: dict[str, ModelName] = {
    "inhabit_session": ModelName.HAIKU,  # Mixed, but start with Haiku
    "inhabit_force": ModelName.SONNET,  # Force needs nuanced response
    "inhabit_apologize": ModelName.HAIKU,  # Apology is lightweight
}

# Branch model routing (no LLM needed)
BRANCH_MODELS: dict[str, ModelName] = {
    "branch_create": ModelName.NONE,
    "branch_switch": ModelName.NONE,
    "branch_merge": ModelName.NONE,
}


# =============================================================================
# Tier-Based Degradation
# =============================================================================

# Model degradation chain: Opus → Sonnet → Haiku → Template
DEGRADATION_CHAIN: list[ModelName] = [
    ModelName.OPUS,
    ModelName.SONNET,
    ModelName.HAIKU,
    ModelName.TEMPLATE,
]


def degrade_model(model: ModelName) -> ModelName:
    """Get next lower model in degradation chain."""
    try:
        idx = DEGRADATION_CHAIN.index(model)
        if idx < len(DEGRADATION_CHAIN) - 1:
            return DEGRADATION_CHAIN[idx + 1]
    except ValueError:
        pass
    return ModelName.TEMPLATE


# Tier maximum models (can't go higher than this)
TIER_MAX_MODELS: dict[str, ModelName] = {
    "TOURIST": ModelName.HAIKU,
    "RESIDENT": ModelName.HAIKU,
    "CITIZEN": ModelName.SONNET,
    "FOUNDER": ModelName.OPUS,
}


# =============================================================================
# Unified Model Selection
# =============================================================================


def select_model(
    action: str,
    tier: str = "TOURIST",
    remaining_credits: int | None = None,
    lod_level: int | None = None,
    is_cached: bool = False,
) -> ModelSelection:
    """
    Select the appropriate model for an action.

    Single source of truth for model routing per unified-v2.md Track B.

    Args:
        action: Action type (lod0-5, greet, gossip, inhabit_session, etc.)
        tier: User subscription tier (TOURIST, RESIDENT, CITIZEN, FOUNDER)
        remaining_credits: User's remaining credits (for degradation)
        lod_level: LOD level (0-5) if action is LOD-based
        is_cached: Whether result can be served from cache

    Returns:
        ModelSelection with model name, reason, and degraded flag
    """
    # Handle cached responses
    if is_cached:
        return ModelSelection(
            model=ModelName.CACHED.value,
            reason="Cache hit - no LLM call needed",
        )

    # Get tier max model
    tier_max = TIER_MAX_MODELS.get(tier.upper(), ModelName.HAIKU)

    # Determine base model for action
    base_model: ModelName = ModelName.HAIKU
    reason_prefix = ""

    # LOD actions
    if action.startswith("lod") or lod_level is not None:
        level = lod_level if lod_level is not None else int(action.replace("lod", ""))
        base_model = LOD_MODELS.get(level, ModelName.HAIKU)
        reason_prefix = f"LOD {level}"

    # Dialogue operations
    elif action in OPERATION_MODELS:
        base_model = OPERATION_MODELS[action]
        reason_prefix = f"Operation '{action}'"

    # INHABIT actions
    elif action in INHABIT_MODELS:
        base_model = INHABIT_MODELS[action]
        reason_prefix = f"INHABIT '{action}'"

    # Branch actions
    elif action in BRANCH_MODELS:
        return ModelSelection(
            model=ModelName.NONE.value,
            reason=f"Branch '{action}' - no LLM needed",
        )

    else:
        reason_prefix = f"Unknown action '{action}'"

    # Apply tier-based cap
    selected_model = base_model
    degraded = False

    # Skip tier cap for cached/none models (they're free)
    if selected_model not in (ModelName.CACHED, ModelName.NONE, ModelName.TEMPLATE):
        if selected_model in DEGRADATION_CHAIN and tier_max in DEGRADATION_CHAIN:
            if DEGRADATION_CHAIN.index(selected_model) < DEGRADATION_CHAIN.index(
                tier_max
            ):
                # User's tier doesn't allow this model - degrade
                selected_model = tier_max
                degraded = True

    # Apply credit-based degradation (if credits are low)
    if remaining_credits is not None:
        credit_thresholds = {
            ModelName.OPUS: 400,
            ModelName.SONNET: 100,
            ModelName.HAIKU: 10,
        }

        threshold = credit_thresholds.get(selected_model, 0)
        if remaining_credits < threshold:
            # Not enough credits - degrade
            while (
                remaining_credits < threshold and selected_model != ModelName.TEMPLATE
            ):
                selected_model = degrade_model(selected_model)
                threshold = credit_thresholds.get(selected_model, 0)
                degraded = True

    # Build reason string
    if degraded:
        reason = f"{reason_prefix}: Degraded from {base_model.value} to {selected_model.value}"
        if remaining_credits is not None and remaining_credits < 100:
            reason += f" (credits={remaining_credits})"
    else:
        reason = f"{reason_prefix}: {selected_model.value}"

    return ModelSelection(
        model=selected_model.value,
        reason=reason,
        degraded=degraded,
    )


def get_model_for_lod(lod: int) -> str:
    """Convenience function for LOD model lookup."""
    return LOD_MODELS.get(lod, ModelName.HAIKU).value


def get_model_for_operation(operation: str) -> str:
    """Convenience function for operation model lookup."""
    return OPERATION_MODELS.get(operation, ModelName.HAIKU).value


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Enums
    "ModelName",
    # Data structures
    "ModelSelection",
    # Constants
    "LOD_MODELS",
    "OPERATION_MODELS",
    "INHABIT_MODELS",
    "BRANCH_MODELS",
    "TIER_MAX_MODELS",
    "DEGRADATION_CHAIN",
    # Functions
    "select_model",
    "degrade_model",
    "get_model_for_lod",
    "get_model_for_operation",
]
