"""
Soul Crown Jewel as DP formulation.

The Soul is the attractor basin in value space—personality as a fixed point.

This module exports the Soul MDP formulation where K-gent's personality
emerges from value function convergence.
"""

from dp.jewels.soul.formulation import (
    SoulAction,
    SoulContext,
    SoulFormulation,
    SoulState,
    create_soul_agent,
    soul_available_actions,
    soul_reward,
    soul_transition,
)

__all__ = [
    "SoulState",
    "SoulAction",
    "SoulFormulation",
    "SoulContext",
    "soul_transition",
    "soul_available_actions",
    "soul_reward",
    "create_soul_agent",
]
