"""
Flow lifecycle states.

The FlowState enum captures the lifecycle phases of a flow agent.
Each state determines what operations are valid.

See: spec/f-gents/README.md
"""

from enum import Enum


class FlowState(Enum):
    """Lifecycle states of a flow agent."""

    DORMANT = "dormant"
    """Created, not started. invoke() works directly."""

    STREAMING = "streaming"
    """Processing continuous input. Main operational state."""

    BRANCHING = "branching"
    """Exploring alternatives (research mode). Generating hypotheses."""

    CONVERGING = "converging"
    """Merging branches (research) or building consensus (collaboration)."""

    DRAINING = "draining"
    """Source exhausted, flushing remaining output."""

    COLLAPSED = "collapsed"
    """Terminal state. Entropy depleted, error, or completed."""

    def is_terminal(self) -> bool:
        """Check if this is a terminal state."""
        return self == FlowState.COLLAPSED

    def is_active(self) -> bool:
        """Check if flow is actively processing."""
        return self in {
            FlowState.STREAMING,
            FlowState.BRANCHING,
            FlowState.CONVERGING,
            FlowState.DRAINING,
        }

    def can_perturb(self) -> bool:
        """Check if perturbation is allowed in this state."""
        return self in {
            FlowState.STREAMING,
            FlowState.BRANCHING,
            FlowState.CONVERGING,
        }


class HypothesisStatus(Enum):
    """Status of a hypothesis in research flow."""

    EXPLORING = "exploring"
    """Currently being investigated."""

    EXPANDED = "expanded"
    """Has been branched into children."""

    PRUNED = "pruned"
    """Eliminated due to low promise."""

    MERGED = "merged"
    """Combined with other hypotheses."""

    CONFIRMED = "confirmed"
    """High confidence, accepted as finding."""


class ContributionType(Enum):
    """Types of contributions in collaboration flow."""

    IDEA = "idea"
    """New proposal or approach."""

    CRITIQUE = "critique"
    """Challenge to existing contribution."""

    QUESTION = "question"
    """Request for clarification."""

    EVIDENCE = "evidence"
    """Supporting or contradicting data."""

    SYNTHESIS = "synthesis"
    """Combining multiple contributions."""

    DECISION = "decision"
    """Final call on a topic."""


class Permission(Enum):
    """Permissions for collaboration agents."""

    READ_ALL = "read_all"
    """Read any contribution."""

    READ_OWN = "read_own"
    """Read only own contributions."""

    POST = "post"
    """Add contributions."""

    CRITIQUE = "critique"
    """Challenge others."""

    PROPOSE = "propose"
    """Submit proposals."""

    VOTE = "vote"
    """Vote on proposals."""

    MODERATE = "moderate"
    """Resolve conflicts."""

    DECIDE = "decide"
    """Make final decisions."""


__all__ = [
    "FlowState",
    "HypothesisStatus",
    "ContributionType",
    "Permission",
]
