"""
Brain Crown Jewel as DP formulation.

Brain is the spatial cathedral of memory. As a DP problem: optimal capture/recall policies.

This module formulates Brain's memory management as a Markov Decision Process (MDP),
where the agent must balance:
- Capturing new memories (storage cost)
- Recalling existing memories (accuracy reward)
- Forgetting low-value memories (capacity management)
- Consolidating memories (compression)

The reward function maps directly to kgents principles:
- COMPOSABLE: Do memories compose coherently?
- GENERATIVE: Is storage efficient (compression ratio)?
- JOY_INDUCING: Are unexpected connections made (serendipity)?

See: services/brain/ (Crown Jewel implementation)
See: dp/core/ (ValueAgent, Constitution, DPSolver)
"""

from dp.jewels.brain.formulation import (
    BrainAction,
    BrainFormulation,
    BrainState,
    create_brain_agent,
)

__all__ = [
    "BrainState",
    "BrainAction",
    "BrainFormulation",
    "create_brain_agent",
]
