"""
Flow Modalities: Chat, Research, and Collaboration.

Each modality is a configuration of the same underlying flow substrate.
"""

from agents.f.modalities.blackboard import (
    AgentRole,
    Blackboard,
    Contribution,
    Decision,
    Proposal,
    Query,
    Vote,
)
from agents.f.modalities.chat import ChatFlow, Turn
from agents.f.modalities.collaboration import (
    CollaborationFlow,
    CollaborationResult,
    ContributionRequest,
    FreeFormOrder,
    ModeratorInput,
    PriorityOrder,
    RoundRobinOrder,
)
from agents.f.modalities.context import (
    Message,
    SlidingContext,
    SummarizingContext,
    count_tokens,
)
from agents.f.modalities.hypothesis import (
    Evidence,
    Hypothesis,
    HypothesisTree,
    Insight,
    Synthesis,
)
from agents.f.modalities.research import (
    BranchStrategy,
    ExploreStrategy,
    MergeStrategy,
    ResearchFlow,
    ResearchResult,
    ResearchStats,
)

__all__ = [
    # Blackboard
    "AgentRole",
    "Blackboard",
    "Contribution",
    "Decision",
    "Proposal",
    "Query",
    "Vote",
    # Chat
    "ChatFlow",
    "Turn",
    "Message",
    "SlidingContext",
    "SummarizingContext",
    "count_tokens",
    # Collaboration
    "CollaborationFlow",
    "CollaborationResult",
    "ContributionRequest",
    "FreeFormOrder",
    "ModeratorInput",
    "PriorityOrder",
    "RoundRobinOrder",
    # Research
    "Evidence",
    "Hypothesis",
    "HypothesisTree",
    "Insight",
    "Synthesis",
    "ResearchFlow",
    "ResearchResult",
    "ResearchStats",
    "BranchStrategy",
    "MergeStrategy",
    "ExploreStrategy",
]
