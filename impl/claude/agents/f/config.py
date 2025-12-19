"""
Flow configuration.

FlowConfig captures all configuration options for flow agents,
including modality-specific settings.

See: spec/f-gents/README.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Literal

if TYPE_CHECKING:
    from agents.f.state import Permission


@dataclass
class FlowConfig:
    """
    Configuration for flow behavior.

    A single configuration class handles all three modalities (chat, research,
    collaboration). The modality field determines which settings are active.
    """

    # === Modality Selection ===
    modality: Literal["chat", "research", "collaboration"] = "chat"

    # === Universal Config ===
    entropy_budget: float = 1.0
    """Initial entropy budget (void.entropy). Depletes over time."""

    entropy_decay: float = 0.01
    """Per-event entropy decay."""

    max_events: int | None = None
    """Hard cap on events. None = unlimited."""

    # === Backpressure ===
    buffer_size: int = 100
    """Output buffer size."""

    drop_policy: Literal["block", "drop_oldest", "drop_newest"] = "block"
    """What to do when buffer is full."""

    # === Feedback (Ouroboros) ===
    feedback_fraction: float = 0.0
    """0.0 = no feedback, 1.0 = full ouroboros (DANGER: solipsism)."""

    feedback_transform: Callable[[Any], Any] | None = None
    """Transform output before feeding back as input."""

    # === Chat-Specific ===
    context_window: int = 128_000
    """Token limit for context."""

    summarization_threshold: float = 0.8
    """Trigger summarization at N% of context_window."""

    context_strategy: Literal["sliding", "summarize", "forget"] = "summarize"
    """How to manage context overflow."""

    turn_timeout: float = 60.0
    """Max seconds per turn."""

    max_turns: int | None = None
    """Max conversation turns. None = unlimited."""

    system_prompt: str | None = None
    """System prompt for chat."""

    system_prompt_position: Literal["prepend", "inject"] = "prepend"
    """Where to place system prompt."""

    interruption_strategy: Literal["complete", "abort", "merge"] = "complete"
    """How to handle interruptions during response."""

    # === Research-Specific ===
    max_branches: int = 5
    """Max parallel hypotheses per node."""

    depth_limit: int = 4
    """Max exploration depth."""

    max_nodes: int = 100
    """Total node limit in hypothesis tree."""

    branching_threshold: float = 0.3
    """Branch if confidence < this threshold."""

    branching_strategy: Literal["uncertainty", "contradiction", "explicit"] = "uncertainty"
    """When to trigger branching."""

    pruning_threshold: float = 0.2
    """Prune branches with promise < this threshold."""

    prune_after_depth: int = 1
    """Start pruning after this depth."""

    merge_strategy: Literal["best_first", "weighted_vote", "synthesis"] = "synthesis"
    """How to merge branches."""

    exploration_strategy: Literal["depth_first", "breadth_first", "best_first"] = "best_first"
    """Order of hypothesis exploration."""

    exploration_budget: int = 50
    """Max hypothesis explorations."""

    confidence_threshold: float = 0.9
    """Stop if answer confidence > this."""

    insight_target: int | None = None
    """Stop after N insights. None = unlimited."""

    # === Collaboration-Specific ===
    agents: list[str] = field(default_factory=list)
    """Agent IDs participating in collaboration."""

    moderator_id: str | None = None
    """ID of moderator agent."""

    blackboard_capacity: int = 100
    """Max contributions on blackboard."""

    contribution_order: Literal["round_robin", "priority", "free"] = "round_robin"
    """How agents take turns."""

    max_contributions_per_round: int = 10
    """Max contributions per round."""

    consensus_threshold: float = 0.67
    """Fraction needed for consensus (e.g., 2/3)."""

    conflict_strategy: Literal["vote", "moderator", "timestamp"] = "vote"
    """How to resolve conflicts."""

    round_limit: int = 10
    """Max contribution rounds."""

    contribution_timeout: float = 30.0
    """Max seconds per contribution."""

    allow_references: bool = True
    """Can contributions cite others?"""

    require_confidence: bool = True
    """Must contributions include confidence?"""

    terminate_on_consensus: bool = True
    """Stop when consensus reached?"""

    minimum_contributions: int = 3
    """Min contributions before allowing termination."""

    moderation_guidelines: str | None = None
    """Guidelines for moderator."""

    escalation_threshold: int = 3
    """Escalate to moderator after N failed votes."""

    # === Observability ===
    agent_id: str | None = None
    """Unique ID for this flow agent."""

    emit_pheromones: bool = True
    """Emit stigmergy signals?"""

    trace_enabled: bool = True
    """Enable N-gent tracing?"""

    # === Memory (D-gent Integration) ===
    persist_history: bool = False
    """Persist conversation history?"""

    memory_key: str | None = None
    """Key for persistent memory."""


@dataclass
class ChatConfig:
    """Chat-specific configuration (convenience wrapper)."""

    context_window: int = 128_000
    context_strategy: Literal["sliding", "summarize", "forget"] = "summarize"
    summarization_threshold: float = 0.8
    turn_timeout: float = 60.0
    max_turns: int | None = None
    system_prompt: str | None = None
    system_prompt_position: Literal["prepend", "inject"] = "prepend"
    interruption_strategy: Literal["complete", "abort", "merge"] = "complete"
    persist_history: bool = False
    memory_key: str | None = None

    def to_flow_config(self) -> FlowConfig:
        """Convert to FlowConfig."""
        return FlowConfig(
            modality="chat",
            context_window=self.context_window,
            context_strategy=self.context_strategy,
            summarization_threshold=self.summarization_threshold,
            turn_timeout=self.turn_timeout,
            max_turns=self.max_turns,
            system_prompt=self.system_prompt,
            system_prompt_position=self.system_prompt_position,
            interruption_strategy=self.interruption_strategy,
            persist_history=self.persist_history,
            memory_key=self.memory_key,
        )


@dataclass
class ResearchConfig:
    """Research-specific configuration (convenience wrapper)."""

    max_branches: int = 5
    depth_limit: int = 4
    max_nodes: int = 100
    branching_threshold: float = 0.3
    branching_strategy: Literal["uncertainty", "contradiction", "explicit"] = "uncertainty"
    pruning_threshold: float = 0.2
    merge_strategy: Literal["best_first", "weighted_vote", "synthesis"] = "synthesis"
    exploration_strategy: Literal["depth_first", "breadth_first", "best_first"] = "best_first"
    exploration_budget: int = 50
    confidence_threshold: float = 0.9
    insight_target: int | None = None

    def to_flow_config(self) -> FlowConfig:
        """Convert to FlowConfig."""
        return FlowConfig(
            modality="research",
            max_branches=self.max_branches,
            depth_limit=self.depth_limit,
            max_nodes=self.max_nodes,
            branching_threshold=self.branching_threshold,
            branching_strategy=self.branching_strategy,
            pruning_threshold=self.pruning_threshold,
            merge_strategy=self.merge_strategy,
            exploration_strategy=self.exploration_strategy,
            exploration_budget=self.exploration_budget,
            confidence_threshold=self.confidence_threshold,
            insight_target=self.insight_target,
        )


@dataclass
class CollaborationConfig:
    """Collaboration-specific configuration (convenience wrapper)."""

    agents: list[str] = field(default_factory=list)
    moderator_id: str | None = None
    blackboard_capacity: int = 100
    contribution_order: Literal["round_robin", "priority", "free"] = "round_robin"
    consensus_threshold: float = 0.67
    conflict_strategy: Literal["vote", "moderator", "timestamp"] = "vote"
    round_limit: int = 10
    contribution_timeout: float = 30.0
    terminate_on_consensus: bool = True
    minimum_contributions: int = 3
    moderation_guidelines: str | None = None

    def to_flow_config(self) -> FlowConfig:
        """Convert to FlowConfig."""
        return FlowConfig(
            modality="collaboration",
            agents=self.agents,
            moderator_id=self.moderator_id,
            blackboard_capacity=self.blackboard_capacity,
            contribution_order=self.contribution_order,
            consensus_threshold=self.consensus_threshold,
            conflict_strategy=self.conflict_strategy,
            round_limit=self.round_limit,
            contribution_timeout=self.contribution_timeout,
            terminate_on_consensus=self.terminate_on_consensus,
            minimum_contributions=self.minimum_contributions,
            moderation_guidelines=self.moderation_guidelines,
        )


__all__ = [
    "FlowConfig",
    "ChatConfig",
    "ResearchConfig",
    "CollaborationConfig",
]
