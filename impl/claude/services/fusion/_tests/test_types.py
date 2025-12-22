"""
Tests for Fusion Types: Proposal, Challenge, Synthesis, FusionResult.

Tests the core dataclasses for Symmetric Supersession.
"""

from datetime import datetime

import pytest

from services.fusion.types import (
    Agent,
    Challenge,
    FusionResult,
    FusionStatus,
    Proposal,
    Synthesis,
    new_challenge_id,
    new_fusion_id,
    new_proposal_id,
)


class TestAgent:
    """Test Agent enum."""

    def test_agent_values(self):
        """All expected agents exist."""
        assert Agent.KENT.value == "kent"
        assert Agent.CLAUDE.value == "claude"
        assert Agent.KGENT.value == "k-gent"
        assert Agent.SYSTEM.value == "system"

    def test_agent_from_string(self):
        """Agent can be created from string."""
        assert Agent("kent") == Agent.KENT
        assert Agent("claude") == Agent.CLAUDE


class TestProposal:
    """Test Proposal dataclass."""

    def test_create_minimal(self):
        """Proposal can be created with minimal args."""
        prop = Proposal.create(
            agent="kent",
            content="Use LangChain",
            reasoning="Scale and resources",
        )

        assert prop.agent == Agent.KENT
        assert prop.content == "Use LangChain"
        assert prop.reasoning == "Scale and resources"
        assert prop.id.startswith("prop-")
        assert prop.principles == ()

    def test_create_with_principles(self):
        """Proposal can have principles."""
        prop = Proposal.create(
            agent="claude",
            content="Build kgents",
            reasoning="Novel contribution",
            principles=["tasteful", "generative"],
        )

        assert prop.agent == Agent.CLAUDE
        assert prop.principles == ("tasteful", "generative")

    def test_proposals_are_symmetric(self):
        """Kent and Claude proposals have identical structure."""
        kent = Proposal.create(agent="kent", content="A", reasoning="B")
        claude = Proposal.create(agent="claude", content="A", reasoning="B")

        # Same structure, different agent
        assert type(kent) == type(claude)
        assert kent.agent != claude.agent
        # Both have IDs
        assert kent.id.startswith("prop-")
        assert claude.id.startswith("prop-")

    def test_proposal_is_immutable(self):
        """Proposals are frozen."""
        prop = Proposal.create(agent="kent", content="A", reasoning="B")

        with pytest.raises(AttributeError):
            prop.content = "Modified"


class TestChallenge:
    """Test Challenge dataclass."""

    def test_create_challenge(self):
        """Challenge can be created."""
        prop_id = new_proposal_id()
        challenge = Challenge.create(
            challenger="claude",
            target_proposal=prop_id,
            content="LangChain optimizes for scale, but misses novel insight",
        )

        assert challenge.challenger == Agent.CLAUDE
        assert challenge.target_proposal == prop_id
        assert challenge.id.startswith("chal-")

    def test_challenge_is_immutable(self):
        """Challenges are frozen."""
        challenge = Challenge.create(
            challenger="kent",
            target_proposal=new_proposal_id(),
            content="Test",
        )

        with pytest.raises(AttributeError):
            challenge.content = "Modified"


class TestSynthesis:
    """Test Synthesis dataclass."""

    def test_create_synthesis(self):
        """Synthesis can be created."""
        synthesis = Synthesis(
            content="Build minimal kernel, then decide",
            reasoning="Avoids both risks",
            incorporates_from_a="Validation path",
            incorporates_from_b="Novel ideas",
            transcends="Pure philosophy or pure pragmatism",
        )

        assert synthesis.content == "Build minimal kernel, then decide"
        assert synthesis.incorporates_from_a == "Validation path"
        assert synthesis.transcends == "Pure philosophy or pure pragmatism"

    def test_synthesis_is_immutable(self):
        """Synthesis is frozen."""
        synthesis = Synthesis(content="A", reasoning="B")

        with pytest.raises(AttributeError):
            synthesis.content = "Modified"


class TestFusionResult:
    """Test FusionResult dataclass."""

    def test_create_result(self):
        """FusionResult can be created."""
        kent = Proposal.create(agent="kent", content="A", reasoning="B")
        claude = Proposal.create(agent="claude", content="C", reasoning="D")

        result = FusionResult(
            id=new_fusion_id(),
            status=FusionStatus.IN_PROGRESS,
            proposal_a=kent,
            proposal_b=claude,
        )

        assert result.status == FusionStatus.IN_PROGRESS
        assert result.synthesis is None

    def test_complete_with_synthesis(self):
        """FusionResult can be completed with synthesis."""
        kent = Proposal.create(agent="kent", content="A", reasoning="B")
        claude = Proposal.create(agent="claude", content="C", reasoning="D")
        synthesis = Synthesis(content="E", reasoning="F")

        result = FusionResult(
            id=new_fusion_id(),
            status=FusionStatus.IN_PROGRESS,
            proposal_a=kent,
            proposal_b=claude,
        )
        result.complete(synthesis)

        assert result.status == FusionStatus.SYNTHESIZED
        assert result.synthesis == synthesis
        assert result.completed_at is not None

    def test_veto(self):
        """FusionResult can be vetoed."""
        kent = Proposal.create(agent="kent", content="A", reasoning="B")
        claude = Proposal.create(agent="claude", content="C", reasoning="D")

        result = FusionResult(
            id=new_fusion_id(),
            status=FusionStatus.IN_PROGRESS,
            proposal_a=kent,
            proposal_b=claude,
        )
        result.veto("Visceral wrongness")

        assert result.status == FusionStatus.VETOED
        assert result.veto_reason == "Visceral wrongness"
        assert result.completed_at is not None

    def test_is_genuine_fusion(self):
        """is_genuine_fusion detects true fusion vs convergence."""
        kent = Proposal.create(agent="kent", content="A", reasoning="B")
        claude = Proposal.create(agent="claude", content="C", reasoning="D")

        # Genuine fusion: synthesis differs from both
        result = FusionResult(
            id=new_fusion_id(),
            status=FusionStatus.IN_PROGRESS,
            proposal_a=kent,
            proposal_b=claude,
        )
        result.complete(Synthesis(content="E", reasoning="F"))

        assert result.is_genuine_fusion is True

        # Not fusion: synthesis same as proposal_a
        result2 = FusionResult(
            id=new_fusion_id(),
            status=FusionStatus.IN_PROGRESS,
            proposal_a=kent,
            proposal_b=claude,
        )
        result2.complete(Synthesis(content="A", reasoning="F"))

        assert result2.is_genuine_fusion is False
