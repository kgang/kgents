"""
Tests for K-Block <-> Witness Bridge Integration.

This module tests the bidirectional bridge between K-Block and Witness:
1. K-Block -> Witness: bind() emits marks
2. Witness -> K-Block: marks and crystals reference K-Block IDs

See: spec/protocols/k-block.md
See: spec/protocols/witness-primitives.md
"""

from datetime import datetime, timezone

import pytest

from services.k_block.core.kblock import (
    KBlock,
    LineageEdge,
    generate_kblock_id,
    get_witness_bridge,
    set_witness_bridge,
)
from services.witness.crystal import Crystal, CrystalLevel, generate_crystal_id
from services.witness.mark import Mark, MarkId, Response, Stimulus, UmweltSnapshot

# =============================================================================
# Test: Mark.from_kblock_bind()
# =============================================================================


class TestMarkFromKBlockBind:
    """Tests for the Mark factory that creates marks from K-Block operations."""

    def test_creates_mark_with_kblock_origin(self) -> None:
        """Mark should have origin='k_block'."""
        mark = Mark.from_kblock_bind(
            from_kblock_id="kb_source123",
            to_kblock_id="kb_result456",
            from_content="Hello",
            to_content="HELLO",
            operation="uppercase",
            lineage_edge_dict={
                "from_id": "kb_source123",
                "to_id": "kb_result456",
                "operation": "uppercase",
                "timestamp": "2025-01-01T00:00:00+00:00",
            },
        )
        assert mark.origin == "k_block"

    def test_creates_mark_with_edit_domain(self) -> None:
        """Mark should have domain='edit' for frontend routing."""
        mark = Mark.from_kblock_bind(
            from_kblock_id="kb_source123",
            to_kblock_id="kb_result456",
            from_content="Hello",
            to_content="HELLO",
            operation="uppercase",
            lineage_edge_dict={},
        )
        assert mark.domain == "edit"

    def test_captures_kblock_ids_in_metadata(self) -> None:
        """Mark metadata should contain from and to K-Block IDs."""
        mark = Mark.from_kblock_bind(
            from_kblock_id="kb_source123",
            to_kblock_id="kb_result456",
            from_content="Hello",
            to_content="HELLO",
            operation="uppercase",
            lineage_edge_dict={},
        )
        assert mark.metadata["kblock_from_id"] == "kb_source123"
        assert mark.metadata["kblock_to_id"] == "kb_result456"

    def test_captures_operation_in_metadata(self) -> None:
        """Mark metadata should contain the operation name."""
        mark = Mark.from_kblock_bind(
            from_kblock_id="kb_source123",
            to_kblock_id="kb_result456",
            from_content="Hello",
            to_content="HELLO",
            operation="my_transform",
            lineage_edge_dict={},
        )
        assert mark.metadata["kblock_operation"] == "my_transform"

    def test_captures_lineage_edge_in_metadata(self) -> None:
        """Mark metadata should contain the serialized lineage edge."""
        edge_dict = {
            "from_id": "kb_source123",
            "to_id": "kb_result456",
            "operation": "uppercase",
            "timestamp": "2025-01-01T00:00:00+00:00",
        }
        mark = Mark.from_kblock_bind(
            from_kblock_id="kb_source123",
            to_kblock_id="kb_result456",
            from_content="Hello",
            to_content="HELLO",
            operation="uppercase",
            lineage_edge_dict=edge_dict,
        )
        assert mark.metadata["lineage_edge"] == edge_dict

    def test_truncates_long_content(self) -> None:
        """Long content should be truncated in stimulus and response."""
        long_content = "x" * 1000
        mark = Mark.from_kblock_bind(
            from_kblock_id="kb_source123",
            to_kblock_id="kb_result456",
            from_content=long_content,
            to_content=long_content,
            operation="identity",
            lineage_edge_dict={},
        )
        # Content truncated to 500 chars
        assert len(mark.stimulus.content) == 500
        assert len(mark.response.content) == 500

    def test_includes_kblock_tags(self) -> None:
        """Mark should have kblock, bind, and operation tags."""
        mark = Mark.from_kblock_bind(
            from_kblock_id="kb_source123",
            to_kblock_id="kb_result456",
            from_content="Hello",
            to_content="HELLO",
            operation="uppercase",
            lineage_edge_dict={},
        )
        assert "kblock" in mark.tags
        assert "bind" in mark.tags
        assert "uppercase" in mark.tags

    def test_accepts_custom_umwelt(self) -> None:
        """Mark should use provided umwelt."""
        custom_umwelt = UmweltSnapshot(
            observer_id="custom_observer",
            role="tester",
            trust_level=2,
        )
        mark = Mark.from_kblock_bind(
            from_kblock_id="kb_source123",
            to_kblock_id="kb_result456",
            from_content="Hello",
            to_content="HELLO",
            operation="uppercase",
            lineage_edge_dict={},
            umwelt=custom_umwelt,
        )
        assert mark.umwelt.observer_id == "custom_observer"
        assert mark.umwelt.role == "tester"


# =============================================================================
# Test: Mark helper methods
# =============================================================================


class TestMarkKBlockHelpers:
    """Tests for Mark helper methods for K-Block integration."""

    def test_is_kblock_mark_returns_true_for_kblock_marks(self) -> None:
        """is_kblock_mark() should return True for K-Block marks."""
        mark = Mark.from_kblock_bind(
            from_kblock_id="kb_source123",
            to_kblock_id="kb_result456",
            from_content="Hello",
            to_content="HELLO",
            operation="uppercase",
            lineage_edge_dict={},
        )
        assert mark.is_kblock_mark() is True

    def test_is_kblock_mark_returns_false_for_regular_marks(self) -> None:
        """is_kblock_mark() should return False for regular marks."""
        mark = Mark.from_thought(
            content="This is a thought",
            source="test",
            tags=("test",),
        )
        assert mark.is_kblock_mark() is False

    def test_get_kblock_lineage_returns_edge_dict(self) -> None:
        """get_kblock_lineage() should return the lineage edge dict."""
        edge_dict = {
            "from_id": "kb_a",
            "to_id": "kb_b",
            "operation": "op",
            "timestamp": "2025-01-01T00:00:00+00:00",
        }
        mark = Mark.from_kblock_bind(
            from_kblock_id="kb_a",
            to_kblock_id="kb_b",
            from_content="A",
            to_content="B",
            operation="op",
            lineage_edge_dict=edge_dict,
        )
        assert mark.get_kblock_lineage() == edge_dict

    def test_get_kblock_lineage_returns_none_for_regular_marks(self) -> None:
        """get_kblock_lineage() should return None for non-K-Block marks."""
        mark = Mark.from_thought(content="thought", source="test")
        assert mark.get_kblock_lineage() is None

    def test_get_kblock_ids_returns_tuple(self) -> None:
        """get_kblock_ids() should return (from_id, to_id) tuple."""
        mark = Mark.from_kblock_bind(
            from_kblock_id="kb_source123",
            to_kblock_id="kb_result456",
            from_content="Hello",
            to_content="HELLO",
            operation="uppercase",
            lineage_edge_dict={},
        )
        ids = mark.get_kblock_ids()
        assert ids == ("kb_source123", "kb_result456")

    def test_get_kblock_ids_returns_none_for_regular_marks(self) -> None:
        """get_kblock_ids() should return None for non-K-Block marks."""
        mark = Mark.from_thought(content="thought", source="test")
        assert mark.get_kblock_ids() is None


# =============================================================================
# Test: Crystal K-Block Provenance
# =============================================================================


class TestCrystalKBlockProvenance:
    """Tests for Crystal K-Block provenance tracking."""

    def test_crystal_has_empty_source_kblocks_by_default(self) -> None:
        """Crystal should have empty source_kblocks by default."""
        crystal = Crystal.from_crystallization(
            insight="Test insight",
            significance="Test significance",
            principles=["composable"],
            source_marks=[MarkId("mark-1")],
            time_range=(datetime.now(timezone.utc), datetime.now(timezone.utc)),
        )
        assert crystal.source_kblocks == ()

    def test_crystal_with_kblocks_stores_ids(self) -> None:
        """Crystal should store K-Block IDs when created with them."""
        crystal = Crystal.from_crystallization_with_kblocks(
            insight="Test insight",
            significance="Test significance",
            principles=["composable"],
            source_marks=[MarkId("mark-1")],
            source_kblocks=["kb_123", "kb_456"],
            time_range=(datetime.now(timezone.utc), datetime.now(timezone.utc)),
        )
        assert crystal.source_kblocks == ("kb_123", "kb_456")

    def test_has_kblock_provenance_returns_true(self) -> None:
        """has_kblock_provenance() should return True when kblocks exist."""
        crystal = Crystal.from_crystallization_with_kblocks(
            insight="Test insight",
            significance="Test significance",
            principles=["composable"],
            source_marks=[MarkId("mark-1")],
            source_kblocks=["kb_123"],
            time_range=(datetime.now(timezone.utc), datetime.now(timezone.utc)),
        )
        assert crystal.has_kblock_provenance() is True

    def test_has_kblock_provenance_returns_false(self) -> None:
        """has_kblock_provenance() should return False when no kblocks."""
        crystal = Crystal.from_crystallization(
            insight="Test insight",
            significance="Test significance",
            principles=["composable"],
            source_marks=[MarkId("mark-1")],
            time_range=(datetime.now(timezone.utc), datetime.now(timezone.utc)),
        )
        assert crystal.has_kblock_provenance() is False

    def test_get_kblock_ids_returns_ids(self) -> None:
        """get_kblock_ids() should return the K-Block IDs."""
        crystal = Crystal.from_crystallization_with_kblocks(
            insight="Test insight",
            significance="Test significance",
            principles=["composable"],
            source_marks=[MarkId("mark-1")],
            source_kblocks=["kb_a", "kb_b", "kb_c"],
            time_range=(datetime.now(timezone.utc), datetime.now(timezone.utc)),
        )
        assert crystal.get_kblock_ids() == ("kb_a", "kb_b", "kb_c")

    def test_crystal_serialization_preserves_kblocks(self) -> None:
        """Crystal to_dict/from_dict should preserve source_kblocks."""
        original = Crystal.from_crystallization_with_kblocks(
            insight="Test insight",
            significance="Test significance",
            principles=["composable"],
            source_marks=[MarkId("mark-1")],
            source_kblocks=["kb_123", "kb_456"],
            time_range=(datetime.now(timezone.utc), datetime.now(timezone.utc)),
        )
        data = original.to_dict()
        restored = Crystal.from_dict(data)
        assert restored.source_kblocks == original.source_kblocks


# =============================================================================
# Test: End-to-End Integration
# =============================================================================


class TestBridgeIntegration:
    """End-to-end tests for the K-Block <-> Witness bridge."""

    def test_kblock_bind_with_bridge_emits_mark(self) -> None:
        """K-Block bind() with bridge should emit a mark."""
        from services.witness.kblock_bridge import WitnessBridge

        bridge = WitnessBridge()
        set_witness_bridge(bridge)

        try:
            doc = KBlock.pure("hello")

            def uppercase(content: str) -> KBlock:
                return KBlock.pure(content.upper())

            result = doc >> uppercase

            # Bridge should have one mark
            assert len(bridge) == 1
            mark = bridge.marks[0]

            # Mark should capture the bind operation
            assert mark.origin == "k_block"
            assert mark.is_kblock_mark()
            assert mark.stimulus.content == "hello"
            assert mark.response.content == "HELLO"
        finally:
            set_witness_bridge(None)

    def test_kblock_chain_emits_multiple_marks(self) -> None:
        """K-Block bind chain should emit a mark for each bind."""
        from services.witness.kblock_bridge import WitnessBridge

        bridge = WitnessBridge()
        set_witness_bridge(bridge)

        try:
            doc = KBlock.pure("hello")

            def uppercase(content: str) -> KBlock:
                return KBlock.pure(content.upper())

            def add_exclaim(content: str) -> KBlock:
                return KBlock.pure(content + "!")

            result = doc >> uppercase >> add_exclaim

            # Two binds = two marks
            assert len(bridge) == 2

            # First mark: hello -> HELLO
            mark1 = bridge.marks[0]
            assert mark1.stimulus.content == "hello"
            assert mark1.response.content == "HELLO"

            # Second mark: HELLO -> HELLO!
            mark2 = bridge.marks[1]
            assert mark2.stimulus.content == "HELLO"
            assert mark2.response.content == "HELLO!"
        finally:
            set_witness_bridge(None)

    def test_result_metadata_contains_mark_id(self) -> None:
        """Result K-Block should have witness_mark_id in metadata."""
        from services.witness.kblock_bridge import WitnessBridge

        bridge = WitnessBridge()
        set_witness_bridge(bridge)

        try:
            doc = KBlock.pure("hello")

            def identity(content: str) -> KBlock:
                return KBlock.pure(content)

            result = doc >> identity

            # Result should have the mark ID
            assert "witness_mark_id" in result.metadata
            mark_id = result.metadata["witness_mark_id"]

            # Should match the emitted mark
            assert bridge.get_mark(mark_id) is not None
        finally:
            set_witness_bridge(None)

    def test_crystal_can_reference_kblock_marks(self) -> None:
        """Crystal created from K-Block marks should reference K-Block IDs."""
        from services.witness.kblock_bridge import WitnessBridge

        bridge = WitnessBridge()
        set_witness_bridge(bridge)

        try:
            # Create some K-Block operations
            doc = KBlock.pure("content")
            result = doc >> (lambda c: KBlock.pure(c.upper()))

            # Get the emitted mark
            mark = bridge.marks[0]
            kblock_ids = mark.get_kblock_ids()

            # Create a crystal referencing the marks and K-Blocks
            crystal = Crystal.from_crystallization_with_kblocks(
                insight="Uppercased some content",
                significance="Demonstrated bridge integration",
                principles=["composable"],
                source_marks=[mark.id],
                source_kblocks=list(kblock_ids) if kblock_ids else [],
                time_range=(datetime.now(timezone.utc), datetime.now(timezone.utc)),
            )

            # Crystal should reference the K-Blocks
            assert crystal.has_kblock_provenance()
            assert kblock_ids[0] in crystal.source_kblocks
            assert kblock_ids[1] in crystal.source_kblocks
        finally:
            set_witness_bridge(None)


# =============================================================================
# Test: Bridge Installation
# =============================================================================


class TestBridgeInstallation:
    """Tests for bridge installation and uninstallation."""

    def test_install_witness_bridge(self) -> None:
        """install_witness_bridge() should set the global bridge."""
        from services.witness.kblock_bridge import (
            install_witness_bridge,
            uninstall_witness_bridge,
        )

        try:
            bridge = install_witness_bridge()
            assert get_witness_bridge() is bridge
        finally:
            uninstall_witness_bridge()

    def test_uninstall_witness_bridge(self) -> None:
        """uninstall_witness_bridge() should clear the global bridge."""
        from services.witness.kblock_bridge import (
            install_witness_bridge,
            uninstall_witness_bridge,
        )

        install_witness_bridge()
        uninstall_witness_bridge()
        assert get_witness_bridge() is None

    def test_bridge_with_custom_umwelt(self) -> None:
        """install_witness_bridge() should accept custom umwelt."""
        from services.witness.kblock_bridge import (
            install_witness_bridge,
            uninstall_witness_bridge,
        )

        custom_umwelt = UmweltSnapshot(observer_id="custom", role="tester")

        try:
            bridge = install_witness_bridge(umwelt=custom_umwelt)

            doc = KBlock.pure("test")
            result = doc >> (lambda c: KBlock.pure(c))

            mark = bridge.marks[0]
            assert mark.umwelt.observer_id == "custom"
        finally:
            uninstall_witness_bridge()


# =============================================================================
# Test: WitnessBridge class
# =============================================================================


class TestWitnessBridgeClass:
    """Tests for the WitnessBridge class itself."""

    def test_bridge_marks_property_returns_copy(self) -> None:
        """bridge.marks should return a copy, not the internal list."""
        from services.witness.kblock_bridge import WitnessBridge

        bridge = WitnessBridge()
        marks = bridge.marks
        assert marks == []
        # Modifying the returned list should not affect internal state
        marks.append(None)  # type: ignore
        assert len(bridge.marks) == 0

    def test_bridge_clear_removes_all_marks(self) -> None:
        """bridge.clear() should remove all stored marks."""
        from services.witness.kblock_bridge import WitnessBridge

        bridge = WitnessBridge()
        set_witness_bridge(bridge)

        try:
            doc = KBlock.pure("test")
            _ = doc >> (lambda c: KBlock.pure(c.upper()))
            assert len(bridge) == 1

            bridge.clear()
            assert len(bridge) == 0
        finally:
            set_witness_bridge(None)

    def test_bridge_get_mark_returns_none_for_unknown_id(self) -> None:
        """bridge.get_mark() should return None for unknown ID."""
        from services.witness.kblock_bridge import WitnessBridge

        bridge = WitnessBridge()
        assert bridge.get_mark("nonexistent-mark-id") is None


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_bind_without_bridge_works(self) -> None:
        """K-Block bind() should work without a bridge installed."""
        # Ensure no bridge is installed
        set_witness_bridge(None)

        doc = KBlock.pure("test")
        result = doc >> (lambda c: KBlock.pure(c.upper()))

        assert result.content == "TEST"
        # No witness_mark_id since no bridge
        assert "witness_mark_id" not in result.metadata

    def test_empty_content_kblock_bind(self) -> None:
        """bind() should handle empty content gracefully."""
        from services.witness.kblock_bridge import WitnessBridge

        bridge = WitnessBridge()
        set_witness_bridge(bridge)

        try:
            doc = KBlock.pure("")
            result = doc >> (lambda c: KBlock.pure(c.upper()))

            assert len(bridge) == 1
            mark = bridge.marks[0]
            assert mark.stimulus.content == ""
            assert mark.response.content == ""
        finally:
            set_witness_bridge(None)

    def test_lineage_edge_dict_integrity(self) -> None:
        """LineageEdge.to_dict() should produce valid dict for mark metadata."""
        edge = LineageEdge(
            from_id="kb_from",
            to_id="kb_to",
            operation="test_op",
        )
        edge_dict = edge.to_dict()

        assert "from_id" in edge_dict
        assert "to_id" in edge_dict
        assert "operation" in edge_dict
        assert "timestamp" in edge_dict

        # Verify roundtrip
        restored = LineageEdge.from_dict(edge_dict)
        assert restored.from_id == edge.from_id
        assert restored.to_id == edge.to_id
        assert restored.operation == edge.operation


# =============================================================================
# Test: Mark Serialization with K-Block Metadata
# =============================================================================


class TestMarkKBlockSerialization:
    """Tests for Mark serialization with K-Block metadata."""

    def test_kblock_mark_roundtrip(self) -> None:
        """K-Block mark should survive serialization roundtrip."""
        original = Mark.from_kblock_bind(
            from_kblock_id="kb_source123",
            to_kblock_id="kb_result456",
            from_content="Hello",
            to_content="HELLO",
            operation="uppercase",
            lineage_edge_dict={
                "from_id": "kb_source123",
                "to_id": "kb_result456",
                "operation": "uppercase",
                "timestamp": "2025-01-01T00:00:00+00:00",
            },
        )

        data = original.to_dict()
        restored = Mark.from_dict(data)

        assert restored.origin == original.origin
        assert restored.domain == original.domain
        assert restored.is_kblock_mark()
        assert restored.get_kblock_ids() == original.get_kblock_ids()
        assert restored.get_kblock_lineage() == original.get_kblock_lineage()
        assert restored.metadata["kblock_operation"] == "uppercase"
