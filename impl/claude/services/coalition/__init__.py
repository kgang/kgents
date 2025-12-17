"""
Coalition Crown Jewel: Visible Agent Collaboration Workshop.

Coalitions are emergent groups of agents that form around shared goals,
with visible decision-making processes.

AGENTESE Paths:
- world.coalition.manifest - Show coalition landscape
- world.coalition.forge - Form a new coalition
- world.coalition.join - Join existing coalition
- world.coalition.deliberate - Collective decision-making

Design DNA:
- Emergent: Coalitions form organically from agent interactions
- Visible: Decision processes are observable
- k-clique: Mathematical foundation from graph theory

See: docs/skills/metaphysical-fullstack.md
"""

from .persistence import (
    CoalitionPersistence,
    CoalitionView,
    MemberView,
    ProposalView,
    VoteView,
    OutputView,
    CoalitionStatus,
)

__all__ = [
    "CoalitionPersistence",
    "CoalitionView",
    "MemberView",
    "ProposalView",
    "VoteView",
    "OutputView",
    "CoalitionStatus",
]
