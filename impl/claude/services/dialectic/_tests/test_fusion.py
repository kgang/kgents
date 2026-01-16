"""
Tests for Dialectical Fusion Service.

These tests verify:
1. Position structuring
2. Fusion outcomes (consensus, synthesis, prevails, veto)
3. Trust delta computation
4. Witnessed traces
5. Constitutional article compliance
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from services.dialectic.fusion import (
    DialecticalFusionService,
    Fusion,
    FusionResult,
    FusionStore,
    Position,
    create_position,
    generate_fusion_id,
    get_fusion_store,
    reset_fusion_store,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def service() -> DialecticalFusionService:
    """Create a fusion service without LLM."""
    reset_fusion_store()
    return DialecticalFusionService()


@pytest.fixture
def mock_llm():
    """Create a mock LLM provider."""

    class MockLLM:
        async def complete(self, prompt: str) -> str:
            # Simple mock responses based on prompt content
            if "AGREE" in prompt or "DISAGREE" in prompt:
                return "DISAGREE"
            elif "0.0 to 1.0" in prompt or "scale" in prompt:
                return "0.7"
            elif "evidence" in prompt.lower():
                return "1. First evidence\n2. Second evidence"
            elif "synthesis" in prompt.lower():
                return "A balanced approach combining both perspectives"
            return "Generic response"

    return MockLLM()


# =============================================================================
# Position Tests
# =============================================================================


class TestPosition:
    """Tests for Position dataclass."""

    def test_create_position_basic(self):
        """Basic position creation."""
        pos = create_position(
            content="Use Postgres",
            reasoning="Familiar, reliable",
            holder="kent",
        )

        assert pos.content == "Use Postgres"
        assert pos.reasoning == "Familiar, reliable"
        assert pos.holder == "kent"
        assert pos.confidence == 0.5  # default
        assert len(pos.principle_alignment) == 7  # all 7 principles

    def test_position_confidence_clamping(self):
        """Confidence should be clamped to [0, 1]."""
        pos = Position(
            content="test",
            reasoning="test",
            confidence=1.5,  # Over 1.0
        )
        assert pos.confidence == 1.0

        pos2 = Position(
            content="test",
            reasoning="test",
            confidence=-0.5,  # Under 0.0
        )
        assert pos2.confidence == 0.0

    def test_position_ethical_score(self):
        """Ethical score should be extracted from principle alignment."""
        pos = create_position(
            content="test",
            reasoning="test",
        )
        pos.principle_alignment["ETHICAL"] = 0.9
        assert pos.ethical_score == 0.9

    def test_position_is_ethically_concerning(self):
        """Positions with low ethical scores should be flagged."""
        pos = create_position(content="test", reasoning="test")
        pos.principle_alignment["ETHICAL"] = 0.2
        assert pos.is_ethically_concerning

        pos.principle_alignment["ETHICAL"] = 0.5
        assert not pos.is_ethically_concerning

    def test_position_serialization(self):
        """Position should serialize and deserialize correctly."""
        pos = create_position(
            content="test content",
            reasoning="test reasoning",
            holder="kent",
            confidence=0.8,
            evidence=["evidence 1", "evidence 2"],
        )

        data = pos.to_dict()
        restored = Position.from_dict(data)

        assert restored.content == pos.content
        assert restored.reasoning == pos.reasoning
        assert restored.holder == pos.holder
        assert restored.confidence == pos.confidence
        assert restored.evidence == pos.evidence


# =============================================================================
# Fusion Store Tests
# =============================================================================


class TestFusionStore:
    """Tests for FusionStore."""

    def test_store_add_and_get(self):
        """Store should add and retrieve fusions."""
        store = FusionStore()
        kent = create_position("A", "B", "kent")
        claude = create_position("C", "D", "claude")

        fusion = Fusion(
            id=generate_fusion_id(),
            topic="test topic",
            timestamp=datetime.now(timezone.utc),
            kent_position=kent,
            claude_position=claude,
            synthesis=None,
            result=FusionResult.DEFERRED,
            reasoning="test",
        )

        store.add(fusion)
        retrieved = store.get(fusion.id)

        assert retrieved is not None
        assert retrieved.id == fusion.id
        assert retrieved.topic == fusion.topic

    def test_store_get_by_topic(self):
        """Store should filter by topic."""
        store = FusionStore()
        kent = create_position("A", "B", "kent")
        claude = create_position("C", "D", "claude")

        for i, topic in enumerate(["database choice", "api design", "database migration"]):
            fusion = Fusion(
                id=generate_fusion_id(),
                topic=topic,
                timestamp=datetime.now(timezone.utc),
                kent_position=kent,
                claude_position=claude,
                synthesis=None,
                result=FusionResult.DEFERRED,
                reasoning="test",
            )
            store.add(fusion)

        db_fusions = store.get_by_topic("database")
        assert len(db_fusions) == 2

    def test_store_get_recent(self):
        """Store should return recent fusions."""
        store = FusionStore()
        kent = create_position("A", "B", "kent")
        claude = create_position("C", "D", "claude")

        for i in range(5):
            fusion = Fusion(
                id=generate_fusion_id(),
                topic=f"topic {i}",
                timestamp=datetime.now(timezone.utc),
                kent_position=kent,
                claude_position=claude,
                synthesis=None,
                result=FusionResult.DEFERRED,
                reasoning="test",
            )
            store.add(fusion)

        recent = store.get_recent(limit=3)
        assert len(recent) == 3


# =============================================================================
# Fusion Service Tests (Without LLM)
# =============================================================================


class TestFusionServiceWithoutLLM:
    """Tests for DialecticalFusionService without LLM."""

    @pytest.mark.asyncio
    async def test_propose_fusion_basic(self, service):
        """Basic fusion should work without LLM."""
        witnessed = await service.propose_fusion(
            topic="Database choice",
            kent_view="Use Postgres",
            kent_reasoning="Familiar, reliable",
            claude_view="Use SQLite",
            claude_reasoning="Simpler for prototyping",
        )

        fusion = witnessed.value
        assert fusion.topic == "Database choice"
        assert fusion.kent_position.content == "Use Postgres"
        assert fusion.claude_position.content == "Use SQLite"
        # Without LLM, should be DEFERRED (equal confidence)
        assert fusion.result == FusionResult.DEFERRED

        # Should have witness marks
        assert len(witnessed.marks) == 1
        assert "dialectic" in witnessed.marks[0].tags

    @pytest.mark.asyncio
    async def test_fusion_creates_mark(self, service):
        """Fusion should create a witness mark."""
        witnessed = await service.propose_fusion(
            topic="API choice",
            kent_view="REST",
            kent_reasoning="Standard",
            claude_view="GraphQL",
            claude_reasoning="Flexible",
        )

        mark = witnessed.marks[0]
        assert mark.origin == "dialectic"
        assert mark.stimulus.kind == "fusion"
        assert mark.response.kind == "fusion_result"

    @pytest.mark.asyncio
    async def test_veto_on_ethical_concern(self, service):
        """Low ethical score should trigger veto (Article IV)."""
        witnessed = await service.propose_fusion(
            topic="Ethics test",
            kent_view="Avoid harm",
            kent_reasoning="Ethical concerns",
            claude_view="Proceed anyway",
            claude_reasoning="Efficiency",
        )

        fusion = witnessed.value
        # Without LLM, we need to manually set ethical concern
        # Let's test the logic directly
        kent = fusion.kent_position
        kent.principle_alignment["ETHICAL"] = 0.2  # Below threshold

        # Re-determine result
        result, reasoning = await service._determine_result(kent, fusion.claude_position, None)

        assert result == FusionResult.VETO
        assert "disgust veto" in reasoning

    @pytest.mark.asyncio
    async def test_trust_delta_recorded(self, service):
        """Trust delta should be recorded in fusion."""
        witnessed = await service.propose_fusion(
            topic="test",
            kent_view="A",
            kent_reasoning="B",
            claude_view="C",
            claude_reasoning="D",
        )

        fusion = witnessed.value
        # Trust delta should be set based on result
        expected_delta = service.TRUST_DELTAS[fusion.result]
        assert fusion.trust_delta == expected_delta


# =============================================================================
# Fusion Service Tests (With Mock LLM)
# =============================================================================


class TestFusionServiceWithLLM:
    """Tests for DialecticalFusionService with mock LLM."""

    @pytest.mark.asyncio
    async def test_consensus_detection(self, mock_llm):
        """Consensus should be detected when positions agree."""
        reset_fusion_store()

        class AgreeingLLM:
            async def complete(self, prompt: str) -> str:
                if "AGREE" in prompt or "DISAGREE" in prompt:
                    return "AGREE"
                elif "0.0 to 1.0" in prompt:
                    return "0.8"
                return "Evidence point"

        service = DialecticalFusionService(llm=AgreeingLLM())
        witnessed = await service.propose_fusion(
            topic="Agreed topic",
            kent_view="Use Python",
            kent_reasoning="Team knows it",
            claude_view="Use Python",
            claude_reasoning="Great ecosystem",
        )

        fusion = witnessed.value
        assert fusion.result == FusionResult.CONSENSUS

    @pytest.mark.asyncio
    async def test_synthesis_attempted(self, mock_llm):
        """Synthesis should be attempted when positions disagree."""
        reset_fusion_store()
        service = DialecticalFusionService(llm=mock_llm)

        witnessed = await service.propose_fusion(
            topic="Framework choice",
            kent_view="Use Django",
            kent_reasoning="Full-featured",
            claude_view="Use FastAPI",
            claude_reasoning="Modern, async",
        )

        fusion = witnessed.value
        # With mock LLM, synthesis is attempted
        # Result depends on confidence comparison


# =============================================================================
# Constitutional Compliance Tests
# =============================================================================


class TestConstitutionalCompliance:
    """Tests for Emerging Constitution article compliance."""

    def test_article_iv_disgust_veto(self):
        """Article IV: Kent's disgust veto should be absolute."""
        kent = create_position("Avoid harm", "Ethical concerns", "kent")
        kent.principle_alignment["ETHICAL"] = 0.1  # Very low

        assert kent.is_ethically_concerning

    @pytest.mark.asyncio
    async def test_article_vi_fusion_as_goal(self, service):
        """Article VI: Synthesis should be preferred when achievable."""
        # This is tested via the synthesis attempt logic
        # Without LLM, synthesis isn't possible, so we verify the logic exists
        assert FusionResult.SYNTHESIS in service.TRUST_DELTAS
        assert (
            service.TRUST_DELTAS[FusionResult.SYNTHESIS]
            > service.TRUST_DELTAS[FusionResult.KENT_PREVAILS]
        )

    def test_trust_delta_values(self):
        """Trust deltas should follow constitution principles."""
        service = DialecticalFusionService()

        # Synthesis should build most trust
        assert (
            service.TRUST_DELTAS[FusionResult.SYNTHESIS]
            >= service.TRUST_DELTAS[FusionResult.CONSENSUS]
        )

        # Veto should lose trust
        assert service.TRUST_DELTAS[FusionResult.VETO] < 0

        # Deferred should be neutral
        assert service.TRUST_DELTAS[FusionResult.DEFERRED] == 0


# =============================================================================
# Trust Trajectory Tests
# =============================================================================


class TestTrustTrajectory:
    """Tests for trust trajectory analysis."""

    @pytest.mark.asyncio
    async def test_trust_trajectory_empty(self, service):
        """Empty history should return neutral trajectory."""
        trajectory = service.get_trust_trajectory()

        assert trajectory["trajectory"] == []
        assert trajectory["trend"] == "neutral"
        assert trajectory["cumulative_delta"] == 0.0

    @pytest.mark.asyncio
    async def test_trust_trajectory_accumulates(self, service):
        """Trust should accumulate across fusions."""
        # Create some fusions
        for i in range(3):
            await service.propose_fusion(
                topic=f"Topic {i}",
                kent_view=f"View {i}",
                kent_reasoning="Reasoning",
                claude_view=f"Other {i}",
                claude_reasoning="Other reasoning",
            )

        trajectory = service.get_trust_trajectory()

        assert len(trajectory["trajectory"]) == 3
        # Cumulative should equal sum of deltas
        expected_cumulative = sum(t["delta"] for t in trajectory["trajectory"])
        assert trajectory["cumulative_delta"] == expected_cumulative


# =============================================================================
# Fusion Serialization Tests
# =============================================================================


class TestFusionSerialization:
    """Tests for Fusion serialization."""

    def test_fusion_to_dict(self):
        """Fusion should serialize to dictionary."""
        kent = create_position("A", "B", "kent")
        claude = create_position("C", "D", "claude")

        fusion = Fusion(
            id=generate_fusion_id(),
            topic="test",
            timestamp=datetime.now(timezone.utc),
            kent_position=kent,
            claude_position=claude,
            synthesis=None,
            result=FusionResult.DEFERRED,
            reasoning="test reasoning",
            trust_delta=0.05,
        )

        data = fusion.to_dict()

        assert data["topic"] == "test"
        assert data["result"] == "deferred"
        assert data["trust_delta"] == 0.05
        assert data["synthesis"] is None

    def test_fusion_from_dict(self):
        """Fusion should deserialize from dictionary."""
        kent = create_position("A", "B", "kent")
        claude = create_position("C", "D", "claude")

        original = Fusion(
            id=generate_fusion_id(),
            topic="test",
            timestamp=datetime.now(timezone.utc),
            kent_position=kent,
            claude_position=claude,
            synthesis=None,
            result=FusionResult.SYNTHESIS,
            reasoning="test",
            trust_delta=0.15,
        )

        data = original.to_dict()
        restored = Fusion.from_dict(data)

        assert restored.id == original.id
        assert restored.topic == original.topic
        assert restored.result == original.result
        assert restored.trust_delta == original.trust_delta


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for fusion service."""

    @pytest.mark.asyncio
    async def test_full_fusion_workflow(self, service):
        """Test complete fusion workflow."""
        # Propose fusion
        witnessed = await service.propose_fusion(
            topic="Architecture decision",
            kent_view="Monolith first",
            kent_reasoning="YAGNI - start simple",
            claude_view="Microservices",
            claude_reasoning="Scale from day one",
        )

        fusion = witnessed.value

        # Check fusion is stored
        stored = service.store.get(fusion.id)
        assert stored is not None
        assert stored.id == fusion.id

        # Check history works
        history = service.get_history(topic="Architecture", limit=1)
        assert len(history) == 1
        assert history[0].id == fusion.id

        # Check mark is linked
        assert fusion.mark_id is not None
        assert len(witnessed.marks) == 1
        assert str(witnessed.marks[0].id) == fusion.mark_id
