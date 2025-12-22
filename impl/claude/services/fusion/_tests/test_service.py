"""
Tests for FusionService: Main API for Symmetric Supersession.

Tests the service layer that orchestrates dialectical fusion.
"""

import pytest

from services.fusion import (
    Agent,
    FusionService,
    FusionStatus,
)


class TestFusionService:
    """Test FusionService."""

    def test_create_service(self):
        """FusionService can be created."""
        service = FusionService()

        assert service is not None
        assert len(service._proposals) == 0
        assert len(service._fusions) == 0

    def test_propose(self):
        """propose creates and stores proposals."""
        service = FusionService()

        kent = service.propose(
            agent="kent",
            content="Use LangChain",
            reasoning="Scale and resources",
        )

        assert kent.agent == Agent.KENT
        assert kent.content == "Use LangChain"
        assert service.get_proposal(kent.id) == kent

    def test_propose_with_principles(self):
        """propose accepts principles."""
        service = FusionService()

        claude = service.propose(
            agent="claude",
            content="Build kgents",
            reasoning="Novel contribution",
            principles=["tasteful", "generative"],
        )

        assert claude.principles == ("tasteful", "generative")

    def test_list_proposals(self):
        """list_proposals returns all proposals."""
        service = FusionService()

        service.propose(agent="kent", content="A", reasoning="B")
        service.propose(agent="claude", content="C", reasoning="D")

        proposals = service.list_proposals()
        assert len(proposals) == 2

    def test_list_proposals_filtered(self):
        """list_proposals can filter by agent."""
        service = FusionService()

        service.propose(agent="kent", content="A", reasoning="B")
        service.propose(agent="kent", content="C", reasoning="D")
        service.propose(agent="claude", content="E", reasoning="F")

        kent_proposals = service.list_proposals(agent="kent")
        assert len(kent_proposals) == 2

        claude_proposals = service.list_proposals(agent="claude")
        assert len(claude_proposals) == 1

    @pytest.mark.asyncio
    async def test_simple_fuse(self):
        """simple_fuse creates synthesis."""
        service = FusionService()

        kent = service.propose(agent="kent", content="A", reasoning="B")
        claude = service.propose(agent="claude", content="C", reasoning="D")

        result = await service.simple_fuse(
            kent,
            claude,
            synthesis_content="E",
            synthesis_reasoning="F",
        )

        assert result.status == FusionStatus.SYNTHESIZED
        assert result.synthesis is not None
        assert result.synthesis.content == "E"
        assert result.is_genuine_fusion is True

    @pytest.mark.asyncio
    async def test_simple_fuse_with_metadata(self):
        """simple_fuse captures what was incorporated."""
        service = FusionService()

        kent = service.propose(agent="kent", content="A", reasoning="B")
        claude = service.propose(agent="claude", content="C", reasoning="D")

        result = await service.simple_fuse(
            kent,
            claude,
            synthesis_content="E",
            synthesis_reasoning="F",
            incorporates_from_a="Part of A",
            incorporates_from_b="Part of C",
            transcends="Goes beyond both",
        )

        assert result.synthesis.incorporates_from_a == "Part of A"
        assert result.synthesis.incorporates_from_b == "Part of C"
        assert result.synthesis.transcends == "Goes beyond both"

    @pytest.mark.asyncio
    async def test_veto(self):
        """veto applies disgust veto to fusion."""
        service = FusionService()

        kent = service.propose(agent="kent", content="A", reasoning="B")
        claude = service.propose(agent="claude", content="C", reasoning="D")

        result = await service.simple_fuse(
            kent,
            claude,
            synthesis_content="E",
            synthesis_reasoning="F",
        )

        vetoed = await service.veto(result, "Visceral wrongness")

        assert vetoed.status == FusionStatus.VETOED
        assert vetoed.veto_reason == "Visceral wrongness"

    @pytest.mark.asyncio
    async def test_fuse_without_synthesizer(self):
        """fuse without synthesizer ends in impasse."""
        service = FusionService()

        kent = service.propose(agent="kent", content="A", reasoning="B")
        claude = service.propose(agent="claude", content="C", reasoning="D")

        # No synthesizer provided - will end in impasse after max_rounds
        result = await service.fuse(kent, claude)

        assert result.status == FusionStatus.IMPASSE
        assert result.synthesis is None

    def test_clear(self):
        """clear removes all proposals and fusions."""
        service = FusionService()

        service.propose(agent="kent", content="A", reasoning="B")
        service.clear()

        assert len(service._proposals) == 0
        assert len(service._fusions) == 0


class TestSymmetricAgency:
    """Test that Kent and Claude have symmetric agency."""

    def test_both_can_propose(self):
        """Both agents can create proposals."""
        service = FusionService()

        kent = service.propose(agent="kent", content="A", reasoning="B")
        claude = service.propose(agent="claude", content="C", reasoning="D")

        assert kent.agent == Agent.KENT
        assert claude.agent == Agent.CLAUDE
        # Same type
        assert type(kent) == type(claude)

    @pytest.mark.asyncio
    async def test_proposals_are_interchangeable(self):
        """Either agent's proposal can be A or B in fusion."""
        service = FusionService()

        kent = service.propose(agent="kent", content="A", reasoning="B")
        claude = service.propose(agent="claude", content="C", reasoning="D")

        # Kent as A, Claude as B
        result1 = await service.simple_fuse(
            kent,
            claude,
            synthesis_content="E1",
            synthesis_reasoning="F1",
        )

        # Claude as A, Kent as B
        result2 = await service.simple_fuse(
            claude,
            kent,
            synthesis_content="E2",
            synthesis_reasoning="F2",
        )

        # Both work equally well
        assert result1.status == FusionStatus.SYNTHESIZED
        assert result2.status == FusionStatus.SYNTHESIZED


class TestDisgustVetoIntegration:
    """Test disgust veto in service context."""

    @pytest.mark.asyncio
    async def test_veto_is_absolute(self):
        """Once vetoed, a fusion cannot be un-vetoed."""
        service = FusionService()

        kent = service.propose(agent="kent", content="A", reasoning="B")
        claude = service.propose(agent="claude", content="C", reasoning="D")

        result = await service.simple_fuse(
            kent,
            claude,
            synthesis_content="E",
            synthesis_reasoning="F",
        )

        # Apply veto
        vetoed = await service.veto(result, "Visceral wrongness")

        # Verify state
        assert vetoed.status == FusionStatus.VETOED
        assert vetoed.synthesis.content == "E"  # Synthesis still recorded
        assert vetoed.veto_reason == "Visceral wrongness"

    @pytest.mark.asyncio
    async def test_fusion_stored_after_veto(self):
        """Vetoed fusions are stored for learning."""
        service = FusionService()

        kent = service.propose(agent="kent", content="A", reasoning="B")
        claude = service.propose(agent="claude", content="C", reasoning="D")

        result = await service.simple_fuse(
            kent,
            claude,
            synthesis_content="E",
            synthesis_reasoning="F",
        )

        await service.veto(result, "Visceral wrongness")

        # Can retrieve vetoed fusion
        stored = service.get_fusion(result.id)
        assert stored is not None
        assert stored.status == FusionStatus.VETOED
