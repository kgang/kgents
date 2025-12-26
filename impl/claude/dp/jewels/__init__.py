"""
DP Formulations for Crown Jewels.

Each Crown Jewel (Brain, Town, Witness, etc.) can be formulated as a Markov
Decision Process (MDP) where the optimal policy maximizes principle satisfaction.

This creates a delightful self-consistency: the Crown Jewels are BOTH:
1. Domain services (Brain, Town, Witness...)
2. DP formulations optimizing for the 7 principles

The self-referential aspect is key: Witness witnesses itself via DP.

jewels/
  witness/     - Witness as MDP (optimal tracing policy)
  brain/       - Brain as MDP (optimal memory management) ✓
  soul/        - Soul as MDP (personality as attractor basin) ✓ NEW
  town/        - Town as MDP (optimal citizen coordination)
  ...

Available Formulations:
- **witness**: Optimal evidence collection and tracing
- **brain**: Optimal memory capture/recall/consolidation ✓
- **soul**: Personality as fixed point of value iteration ✓ NEW

See: dp/core/value_agent.py
See: services/categorical/dp_bridge.py
"""

from dp.jewels.brain import BrainAction, BrainFormulation, BrainState, create_brain_agent
from dp.jewels.soul import (
    SoulAction,
    SoulContext,
    SoulFormulation,
    SoulState,
    create_soul_agent,
)

__all__ = [
    "BrainState",
    "BrainAction",
    "BrainFormulation",
    "create_brain_agent",
    "SoulState",
    "SoulAction",
    "SoulFormulation",
    "SoulContext",
    "create_soul_agent",
]
