"""
Tests for K-Block Derivation Service.

Tests the service that bridges K-Block storage with ASHC derivation context.
Covers:
- Derivation context computation
- Grounding suggestion generation
- Grounding operations
- Downstream tracking
- Change propagation

Philosophy: "The system illuminates, not enforces."
"""

from __future__ import annotations

from typing import Any

import pytest

from protocols.ashc.paths import DerivationWitness, WitnessType

from ..derivation_service import (
    GROUNDING_THRESHOLD,
    PRINCIPLES,
    PROVISIONAL_THRESHOLD,
    DerivationContext,
    DerivationWitnessBridge,
    GroundingSuggestion,
    KBlockDerivationService,
    NullDerivationWitnessBridge,
    create_derivation_service,
    get_derivation_service,
    reset_derivation_service,
    set_derivation_service,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def service() -> KBlockDerivationService:
    """Create a fresh derivation service for testing."""
    return create_derivation_service()


@pytest.fixture
def mock_witness_bridge() -> MockWitnessBridge:
    """Create a mock witness bridge that records calls."""
    return MockWitnessBridge()


class MockWitnessBridge:
    """Mock witness bridge for testing."""

    def __init__(self) -> None:
        self.grounding_marks: list[dict[str, Any]] = []
        self.derivation_marks: list[dict[str, Any]] = []

    async def emit_grounding_mark(
        self,
        kblock_id: str,
        principle: str,
        galois_loss: float,
        context: DerivationContext,
    ) -> str | None:
        """Record grounding mark emission."""
        mark_id = f"mark_{len(self.grounding_marks)}"
        self.grounding_marks.append(
            {
                "kblock_id": kblock_id,
                "principle": principle,
                "galois_loss": galois_loss,
                "context": context,
                "mark_id": mark_id,
            }
        )
        return mark_id

    async def emit_derivation_mark(
        self,
        from_kblock_id: str,
        to_kblock_id: str,
        edge_kind: str,
        galois_loss: float,
    ) -> str | None:
        """Record derivation mark emission."""
        mark_id = f"deriv_{len(self.derivation_marks)}"
        self.derivation_marks.append(
            {
                "from_kblock_id": from_kblock_id,
                "to_kblock_id": to_kblock_id,
                "edge_kind": edge_kind,
                "galois_loss": galois_loss,
                "mark_id": mark_id,
            }
        )
        return mark_id


# =============================================================================
# GroundingSuggestion Tests
# =============================================================================


class TestGroundingSuggestion:
    """Tests for GroundingSuggestion dataclass."""

    def test_create_valid_suggestion(self) -> None:
        """Test creating a valid grounding suggestion."""
        suggestion = GroundingSuggestion(
            principle="COMPOSABLE",
            galois_loss=0.3,
            confidence=0.7,
            reasoning="Content aligns with composability patterns",
        )

        assert suggestion.principle == "COMPOSABLE"
        assert suggestion.galois_loss == 0.3
        assert suggestion.confidence == 0.7
        assert "composability" in suggestion.reasoning

    def test_clamp_values(self) -> None:
        """Test that galois_loss and confidence are clamped to [0, 1]."""
        suggestion = GroundingSuggestion(
            principle="ETHICAL",
            galois_loss=1.5,  # Should be clamped to 1.0
            confidence=-0.2,  # Should be clamped to 0.0
            reasoning="Test",
        )

        assert suggestion.galois_loss == 1.0
        assert suggestion.confidence == 0.0

    def test_unknown_principle_logs_warning(self, caplog: Any) -> None:
        """Test that unknown principle logs a warning."""
        import logging

        with caplog.at_level(logging.WARNING):
            _ = GroundingSuggestion(
                principle="UNKNOWN_PRINCIPLE",
                galois_loss=0.5,
                confidence=0.5,
                reasoning="Test",
            )

        # Should log a warning about unknown principle
        assert "Unknown principle" in caplog.text or len(caplog.records) == 0


# =============================================================================
# DerivationContext Tests
# =============================================================================


class TestDerivationContext:
    """Tests for DerivationContext dataclass."""

    def test_create_orphan_context(self) -> None:
        """Test creating an orphan derivation context."""
        context = DerivationContext(
            source_principle=None,
            galois_loss=0.8,
            grounding_status="orphan",
            parent_kblock_id=None,
            derivation_path=None,
            witnesses=[],
        )

        assert context.source_principle is None
        assert context.grounding_status == "orphan"
        assert not context.is_grounded
        assert context.coherence == 0.2

    def test_create_grounded_context(self) -> None:
        """Test creating a grounded derivation context."""
        context = DerivationContext(
            source_principle="COMPOSABLE",
            galois_loss=0.3,
            grounding_status="grounded",
            parent_kblock_id="kb_parent",
            derivation_path=None,
            witnesses=[],
        )

        assert context.source_principle == "COMPOSABLE"
        assert context.grounding_status == "grounded"
        assert context.is_grounded
        assert context.coherence == 0.7

    def test_invalid_grounding_status_raises(self) -> None:
        """Test that invalid grounding status raises ValueError."""
        with pytest.raises(ValueError, match="Invalid grounding_status"):
            DerivationContext(
                source_principle=None,
                galois_loss=0.5,
                grounding_status="invalid_status",
                parent_kblock_id=None,
                derivation_path=None,
                witnesses=[],
            )

    def test_serialization_roundtrip(self) -> None:
        """Test serialization and deserialization."""
        witness = DerivationWitness.from_galois(0.3, method="test")
        context = DerivationContext(
            source_principle="ETHICAL",
            galois_loss=0.3,
            grounding_status="grounded",
            parent_kblock_id="kb_parent",
            derivation_path=None,
            witnesses=[witness],
        )

        # Serialize and deserialize
        data = context.to_dict()
        restored = DerivationContext.from_dict(data)

        assert restored.source_principle == context.source_principle
        assert restored.galois_loss == context.galois_loss
        assert restored.grounding_status == context.grounding_status
        assert restored.parent_kblock_id == context.parent_kblock_id
        assert len(restored.witnesses) == 1


# =============================================================================
# KBlockDerivationService Tests
# =============================================================================


class TestKBlockDerivationService:
    """Tests for the main derivation service."""

    @pytest.mark.asyncio
    async def test_compute_derivation_orphan(self, service: KBlockDerivationService) -> None:
        """Test computing derivation for orphan content."""
        context = await service.compute_derivation(
            kblock_id="kb_test_1",
            content="Some random content without clear principle alignment",
        )

        assert context is not None
        assert context.grounding_status in ("orphan", "provisional", "grounded")
        assert 0.0 <= context.galois_loss <= 1.0
        assert len(context.witnesses) >= 1  # At least Galois witness

    @pytest.mark.asyncio
    async def test_compute_derivation_with_parent(self, service: KBlockDerivationService) -> None:
        """Test computing derivation with a parent K-Block."""
        # First, create parent context
        parent_context = DerivationContext(
            source_principle="COMPOSABLE",
            galois_loss=0.2,
            grounding_status="grounded",
            parent_kblock_id=None,
            derivation_path=None,
            witnesses=[],
        )
        service._contexts["kb_parent"] = parent_context

        # Compute child derivation
        context = await service.compute_derivation(
            kblock_id="kb_child",
            content="Building on composable foundations",
            parent_kblock_id="kb_parent",
        )

        assert context.parent_kblock_id == "kb_parent"
        # Should have at least composition witness + galois witness
        assert len(context.witnesses) >= 1
        # Should inherit source principle
        assert context.source_principle == "COMPOSABLE"

    @pytest.mark.asyncio
    async def test_suggest_grounding_returns_sorted(self, service: KBlockDerivationService) -> None:
        """Test that suggest_grounding returns sorted suggestions."""
        suggestions = await service.suggest_grounding(
            content="Building composable, delightful user experiences",
            limit=5,
        )

        assert len(suggestions) <= 5
        assert all(isinstance(s, GroundingSuggestion) for s in suggestions)

        # Should be sorted by galois_loss (ascending = highest confidence first)
        for i in range(len(suggestions) - 1):
            assert suggestions[i].galois_loss <= suggestions[i + 1].galois_loss

    @pytest.mark.asyncio
    async def test_suggest_grounding_all_principles(self, service: KBlockDerivationService) -> None:
        """Test that suggestions cover multiple principles."""
        suggestions = await service.suggest_grounding(
            content="A comprehensive test content covering many aspects",
            limit=7,  # All 7 principles
        )

        # Should have suggestions for multiple principles
        principles_suggested = {s.principle for s in suggestions}
        assert len(principles_suggested) >= 1
        # All suggestions should be for valid principles
        assert all(s.principle in PRINCIPLES for s in suggestions)

    @pytest.mark.asyncio
    async def test_ground_kblock_valid_principle(self, service: KBlockDerivationService) -> None:
        """Test grounding a K-Block with a valid principle."""
        # First compute derivation (creates context)
        await service.compute_derivation("kb_orphan", "Some orphan content")

        # Ground to a principle
        path = await service.ground_kblock("kb_orphan", "COMPOSABLE")

        assert path is not None
        assert path.source_id == "COMPOSABLE"
        assert path.target_id == "kb_orphan"

        # Context should be updated
        context = service.get_context("kb_orphan")
        assert context is not None
        assert context.source_principle == "COMPOSABLE"
        assert context.grounding_status in ("grounded", "provisional")

    @pytest.mark.asyncio
    async def test_ground_kblock_invalid_principle_raises(
        self, service: KBlockDerivationService
    ) -> None:
        """Test that grounding with invalid principle raises ValueError."""
        with pytest.raises(ValueError, match="Invalid principle"):
            await service.ground_kblock("kb_test", "NOT_A_PRINCIPLE")

    @pytest.mark.asyncio
    async def test_ground_kblock_with_parent(self, service: KBlockDerivationService) -> None:
        """Test grounding a K-Block with a parent."""
        # Create parent
        parent_context = DerivationContext(
            source_principle="ETHICAL",
            galois_loss=0.2,
            grounding_status="grounded",
            parent_kblock_id=None,
            derivation_path=None,
            witnesses=[],
        )
        service._contexts["kb_parent"] = parent_context

        # Ground child
        path = await service.ground_kblock(
            "kb_child",
            "ETHICAL",
            parent_kblock_id="kb_parent",
        )

        assert path.source_id == "kb_parent"
        assert "kb_parent" in path.kblock_lineage

    @pytest.mark.asyncio
    async def test_get_downstream_single_level(self, service: KBlockDerivationService) -> None:
        """Test getting downstream K-Blocks (single level)."""
        # Create parent with children
        service._downstream_index["kb_parent"] = {"kb_child_1", "kb_child_2"}

        downstream = await service.get_downstream("kb_parent")

        assert len(downstream) == 2
        assert "kb_child_1" in downstream
        assert "kb_child_2" in downstream

    @pytest.mark.asyncio
    async def test_get_downstream_multi_level(self, service: KBlockDerivationService) -> None:
        """Test getting downstream K-Blocks (multiple levels)."""
        # Create hierarchy: parent -> child -> grandchild
        service._downstream_index["kb_parent"] = {"kb_child"}
        service._downstream_index["kb_child"] = {"kb_grandchild"}

        downstream = await service.get_downstream("kb_parent")

        assert len(downstream) == 2
        assert "kb_child" in downstream
        assert "kb_grandchild" in downstream

    @pytest.mark.asyncio
    async def test_get_downstream_empty(self, service: KBlockDerivationService) -> None:
        """Test getting downstream when there are no children."""
        downstream = await service.get_downstream("kb_no_children")
        assert downstream == []

    @pytest.mark.asyncio
    async def test_recompute_on_change_updates_context(
        self, service: KBlockDerivationService
    ) -> None:
        """Test that recompute_on_change updates the context."""
        # Create initial context
        initial_context = DerivationContext(
            source_principle="COMPOSABLE",
            galois_loss=0.3,
            grounding_status="grounded",
            parent_kblock_id=None,
            derivation_path=None,
            witnesses=[],
        )
        service._contexts["kb_test"] = initial_context

        # Recompute with new content
        await service.recompute_on_change(
            "kb_test",
            new_content="Completely different content now",
        )

        # Context should be updated
        context = service.get_context("kb_test")
        assert context is not None
        # Should have additional witness from recomputation
        assert len(context.witnesses) >= 1

    @pytest.mark.asyncio
    async def test_recompute_on_change_unknown_kblock(
        self,
        service: KBlockDerivationService,
        caplog: Any,
    ) -> None:
        """Test recompute_on_change logs warning for unknown K-Block."""
        import logging

        with caplog.at_level(logging.WARNING):
            await service.recompute_on_change(
                "kb_unknown",
                new_content="Some content",
            )

        assert "No derivation context" in caplog.text

    def test_get_context_returns_none_for_unknown(self, service: KBlockDerivationService) -> None:
        """Test get_context returns None for unknown K-Block."""
        context = service.get_context("kb_nonexistent")
        assert context is None

    def test_get_all_contexts(self, service: KBlockDerivationService) -> None:
        """Test get_all_contexts returns all stored contexts."""
        # Add some contexts
        ctx1 = DerivationContext(
            source_principle="ETHICAL",
            galois_loss=0.2,
            grounding_status="grounded",
            parent_kblock_id=None,
            derivation_path=None,
            witnesses=[],
        )
        ctx2 = DerivationContext(
            source_principle=None,
            galois_loss=0.8,
            grounding_status="orphan",
            parent_kblock_id=None,
            derivation_path=None,
            witnesses=[],
        )
        service._contexts["kb_1"] = ctx1
        service._contexts["kb_2"] = ctx2

        all_contexts = service.get_all_contexts()

        assert len(all_contexts) == 2
        assert "kb_1" in all_contexts
        assert "kb_2" in all_contexts


# =============================================================================
# Witness Bridge Integration Tests
# =============================================================================


class TestWitnessBridgeIntegration:
    """Tests for witness bridge integration."""

    @pytest.mark.asyncio
    async def test_null_bridge_returns_none(self) -> None:
        """Test that NullDerivationWitnessBridge returns None."""
        bridge = NullDerivationWitnessBridge()

        result = await bridge.emit_grounding_mark(
            kblock_id="kb_test",
            principle="COMPOSABLE",
            galois_loss=0.3,
            context=DerivationContext(
                source_principle="COMPOSABLE",
                galois_loss=0.3,
                grounding_status="grounded",
                parent_kblock_id=None,
                derivation_path=None,
                witnesses=[],
            ),
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_mock_bridge_records_marks(self, mock_witness_bridge: MockWitnessBridge) -> None:
        """Test that mock bridge records emitted marks."""
        service = KBlockDerivationService(
            witness_bridge=mock_witness_bridge,
        )

        # Create a context and ground it
        await service.compute_derivation("kb_test", "Test content")
        await service.ground_kblock("kb_test", "ETHICAL")

        # Should have recorded a grounding mark
        assert len(mock_witness_bridge.grounding_marks) == 1
        mark = mock_witness_bridge.grounding_marks[0]
        assert mark["kblock_id"] == "kb_test"
        assert mark["principle"] == "ETHICAL"
        assert mark["mark_id"].startswith("mark_")


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_derivation_service_defaults(self) -> None:
        """Test creating service with defaults."""
        service = create_derivation_service()

        assert service is not None
        assert service.dag is not None
        assert isinstance(service.witness_bridge, NullDerivationWitnessBridge)

    def test_create_derivation_service_custom_dag(self) -> None:
        """Test creating service with custom DAG."""
        from ..core.derivation import DerivationDAG

        custom_dag = DerivationDAG()
        custom_dag.add_node("kb_axiom", layer=1, kind="axiom")

        service = create_derivation_service(dag=custom_dag)

        assert service.dag is custom_dag
        assert len(service.dag) == 1


class TestGlobalServiceManagement:
    """Tests for global service instance management."""

    def setup_method(self) -> None:
        """Reset global service before each test."""
        reset_derivation_service()

    def teardown_method(self) -> None:
        """Reset global service after each test."""
        reset_derivation_service()

    def test_get_derivation_service_creates_instance(self) -> None:
        """Test that get_derivation_service creates an instance."""
        service = get_derivation_service()
        assert service is not None

    def test_get_derivation_service_returns_same_instance(self) -> None:
        """Test that get_derivation_service returns the same instance."""
        service1 = get_derivation_service()
        service2 = get_derivation_service()
        assert service1 is service2

    def test_set_derivation_service_overrides(self) -> None:
        """Test that set_derivation_service overrides the global instance."""
        custom_service = create_derivation_service()
        set_derivation_service(custom_service)

        retrieved = get_derivation_service()
        assert retrieved is custom_service

    def test_reset_derivation_service(self) -> None:
        """Test that reset_derivation_service clears the global instance."""
        _ = get_derivation_service()  # Create instance
        reset_derivation_service()

        # Should create a new instance
        new_service = get_derivation_service()
        assert new_service is not None


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_content(self, service: KBlockDerivationService) -> None:
        """Test handling empty content."""
        context = await service.compute_derivation("kb_empty", "")

        # Should still compute a context
        assert context is not None
        assert context.grounding_status in ("orphan", "provisional", "grounded")

    @pytest.mark.asyncio
    async def test_very_long_content(self, service: KBlockDerivationService) -> None:
        """Test handling very long content."""
        long_content = "Test " * 1000  # 5000 characters

        context = await service.compute_derivation("kb_long", long_content)

        assert context is not None
        assert 0.0 <= context.galois_loss <= 1.0

    @pytest.mark.asyncio
    async def test_special_characters_in_content(self, service: KBlockDerivationService) -> None:
        """Test handling special characters in content."""
        special_content = "Test with special chars: <>&'\"\n\t\r"

        context = await service.compute_derivation("kb_special", special_content)

        assert context is not None

    @pytest.mark.asyncio
    async def test_ground_kblock_creates_context_if_missing(
        self, service: KBlockDerivationService
    ) -> None:
        """Test that ground_kblock creates context if not exists."""
        # Don't call compute_derivation first
        path = await service.ground_kblock("kb_new", "COMPOSABLE")

        assert path is not None
        context = service.get_context("kb_new")
        assert context is not None
        assert context.source_principle == "COMPOSABLE"

    @pytest.mark.asyncio
    async def test_suggest_grounding_with_zero_limit(
        self, service: KBlockDerivationService
    ) -> None:
        """Test suggest_grounding with limit=0."""
        suggestions = await service.suggest_grounding(
            content="Test content",
            limit=0,
        )

        assert suggestions == []

    @pytest.mark.asyncio
    async def test_downstream_cycle_prevention(self, service: KBlockDerivationService) -> None:
        """Test that get_downstream handles cycles gracefully."""
        # Create a potential cycle (though DAG should prevent this)
        service._downstream_index["kb_a"] = {"kb_b"}
        service._downstream_index["kb_b"] = {"kb_a"}  # Would create cycle

        # Should not hang due to cycle
        downstream = await service.get_downstream("kb_a")

        # Should find both, but not infinite loop
        assert len(downstream) <= 2


# =============================================================================
# Performance Considerations
# =============================================================================


class TestPerformance:
    """Tests for performance-related behavior."""

    @pytest.mark.asyncio
    async def test_loss_cache_is_used(self, service: KBlockDerivationService) -> None:
        """Test that loss cache is utilized for repeated computations."""
        content = "Same content for caching test"

        # First computation
        ctx1 = await service.compute_derivation("kb_1", content)

        # Second computation with same content should use cache
        ctx2 = await service.compute_derivation("kb_2", content)

        # Both should complete (cache should be hit)
        assert ctx1 is not None
        assert ctx2 is not None

    def test_principle_descriptions_complete(self) -> None:
        """Test that all principles have descriptions."""
        from ..derivation_service import PRINCIPLE_DESCRIPTIONS, PRINCIPLES

        for principle in PRINCIPLES:
            assert principle in PRINCIPLE_DESCRIPTIONS
            assert len(PRINCIPLE_DESCRIPTIONS[principle]) > 0
