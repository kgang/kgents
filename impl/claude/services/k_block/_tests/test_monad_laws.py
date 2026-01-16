"""
Tests for K-Block Monad Laws with Lineage Threading (Amendment D).

This module verifies:
1. Monad Laws (left identity, right identity, associativity)
2. Lineage Threading (bind creates LineageEdge, lineage accumulates)
3. Pure and bind semantics
4. >> operator behavior
5. Functor map via bind

Philosophy:
    "The proof IS the decision. The mark IS the witness."

Amendment D specifies that K-Block bind() MUST create LineageEdge objects
to track the derivation chain. These tests verify that requirement.

See: plans/enlightened-synthesis/01-theoretical-amendments.md (Amendment D)
"""

import pytest

from ..core import (
    KBlock,
    LineageEdge,
    WitnessBridgeProtocol,
    generate_kblock_id,
    get_witness_bridge,
    set_witness_bridge,
)

# -----------------------------------------------------------------------------
# Helper Functions (Kleisli Arrows)
# -----------------------------------------------------------------------------


def append_suffix(content: str) -> KBlock:
    """Kleisli arrow: Append '_suffix' to content."""
    return KBlock.pure(content + "_suffix")


def prepend_prefix(content: str) -> KBlock:
    """Kleisli arrow: Prepend 'prefix_' to content."""
    return KBlock.pure("prefix_" + content)


def wrap_brackets(content: str) -> KBlock:
    """Kleisli arrow: Wrap content in brackets."""
    return KBlock.pure(f"[{content}]")


def upper_transform(content: str) -> KBlock:
    """Kleisli arrow: Convert to uppercase."""
    return KBlock.pure(content.upper())


def identity_transform(content: str) -> KBlock:
    """Kleisli arrow: Identity (pure/return)."""
    return KBlock.pure(content)


# -----------------------------------------------------------------------------
# Monad Law Tests
# -----------------------------------------------------------------------------


class TestMonadLaws:
    """
    Verify K-Block monad laws (content equality).

    The three monad laws:
    1. Left identity:  pure(a) >>= f  ===  f(a)
    2. Right identity: m >>= pure     ===  m
    3. Associativity:  (m >>= f) >>= g === m >>= (x -> f(x) >>= g)

    Note: We verify content equality, not structural equality.
    Different K-Blocks may have different IDs but same content.
    """

    def test_left_identity_content(self):
        """
        Left identity: pure(a) >>= f === f(a)

        Lifting a value into K-Block then binding should give
        the same content as applying the function directly.
        """
        a = "hello"

        # Left side: pure(a) >>= f
        left = KBlock.pure(a).bind(append_suffix)

        # Right side: f(a)
        right = append_suffix(a)

        # Content should be equivalent
        assert left.content == right.content
        assert left.content == "hello_suffix"

    def test_right_identity_content(self):
        """
        Right identity: m >>= pure === m

        Binding with pure should give back the original content.
        """
        m = KBlock.pure("hello")
        original_content = m.content

        # m >>= pure
        result = m.bind(KBlock.pure)

        # Content should be equivalent to m
        assert result.content == original_content
        assert result.content == "hello"

    def test_associativity_content(self):
        """
        Associativity: (m >>= f) >>= g === m >>= (x -> f(x) >>= g)

        Binding is associative (content-wise).
        """
        m = KBlock.pure("a")

        # Left side: (m >>= f) >>= g
        left = m.bind(append_suffix).bind(prepend_prefix)

        # Right side: m >>= (lambda x: f(x) >>= g)
        def fg(content: str) -> KBlock:
            return append_suffix(content).bind(prepend_prefix)

        right = m.bind(fg)

        # Content should be equivalent
        assert left.content == right.content
        assert left.content == "prefix_a_suffix"

    def test_associativity_three_functions(self):
        """
        Extended associativity test with three functions.

        ((m >>= f) >>= g) >>= h === m >>= (x -> f(x) >>= (y -> g(y) >>= h))
        """
        m = KBlock.pure("test")

        # Left side: ((m >>= f) >>= g) >>= h
        left = m.bind(append_suffix).bind(prepend_prefix).bind(wrap_brackets)

        # Right side: m >>= (x -> f(x) >>= (y -> g(y) >>= h))
        def fgh(content: str) -> KBlock:
            return append_suffix(content).bind(lambda y: prepend_prefix(y).bind(wrap_brackets))

        right = m.bind(fgh)

        # Content should be equivalent
        assert left.content == right.content
        assert left.content == "[prefix_test_suffix]"


# -----------------------------------------------------------------------------
# Lineage Threading Tests (Amendment D: THE CRITICAL PART)
# -----------------------------------------------------------------------------


class TestLineageThreading:
    """
    Verify that bind() creates LineageEdge objects.

    This is the core of Amendment D: every bind operation MUST
    create a LineageEdge to track the derivation chain.
    """

    def test_pure_has_empty_lineage(self):
        """Pure (return) creates K-Block with no lineage."""
        block = KBlock.pure("content")
        assert block.bind_lineage == []
        assert len(block.bind_lineage) == 0

    def test_bind_creates_lineage_edge(self):
        """Single bind creates one LineageEdge."""
        block = KBlock.pure("content")
        result = block.bind(append_suffix)

        # Should have exactly one edge
        assert len(result.bind_lineage) == 1

        # Edge should connect block to result
        edge = result.bind_lineage[0]
        assert isinstance(edge, LineageEdge)
        assert edge.from_id == block.id
        assert edge.to_id == result.id
        assert edge.operation == "append_suffix"

    def test_bind_chain_accumulates_lineage(self):
        """Chained binds accumulate lineage edges."""
        a = KBlock.pure("start")
        b = a.bind(append_suffix)
        c = b.bind(prepend_prefix)

        # After two binds, should have 2 edges
        assert len(c.bind_lineage) == 2

        # First edge: a -> b
        assert c.bind_lineage[0].from_id == a.id
        assert c.bind_lineage[0].to_id == b.id
        assert c.bind_lineage[0].operation == "append_suffix"

        # Second edge: b -> c
        assert c.bind_lineage[1].from_id == b.id
        assert c.bind_lineage[1].to_id == c.id
        assert c.bind_lineage[1].operation == "prepend_prefix"

    def test_lineage_through_rshift_operator(self):
        """>> operator creates same lineage as bind."""
        a = KBlock.pure("start")

        # Using >> operator
        result = a >> append_suffix >> prepend_prefix

        # Should have 2 edges
        assert len(result.bind_lineage) == 2
        assert result.bind_lineage[0].operation == "append_suffix"
        assert result.bind_lineage[1].operation == "prepend_prefix"

    def test_lineage_preserves_order(self):
        """Lineage edges are in application order."""
        start = KBlock.pure("x")
        result = start >> append_suffix >> prepend_prefix >> wrap_brackets

        # Should have 3 edges in order
        assert len(result.bind_lineage) == 3
        operations = [edge.operation for edge in result.bind_lineage]
        assert operations == ["append_suffix", "prepend_prefix", "wrap_brackets"]

    def test_lineage_edge_has_timestamp(self):
        """LineageEdge includes timestamp."""
        block = KBlock.pure("content")
        result = block.bind(append_suffix)

        edge = result.bind_lineage[0]
        assert edge.timestamp is not None

    def test_lineage_with_lambda(self):
        """Lineage works with lambda functions."""
        block = KBlock.pure("content")

        # Lambda has no __name__ but getattr returns "transform" as fallback
        result = block.bind(lambda x: KBlock.pure(x.upper()))

        assert len(result.bind_lineage) == 1
        edge = result.bind_lineage[0]
        # Lambda gets fallback name
        assert edge.operation in ["<lambda>", "transform"]


# -----------------------------------------------------------------------------
# Pure and Map Tests
# -----------------------------------------------------------------------------


class TestPureAndMap:
    """Test pure (return) and map (functor)."""

    def test_pure_creates_valid_kblock(self):
        """Pure creates a valid K-Block with content."""
        block = KBlock.pure("hello")

        assert block.content == "hello"
        assert block.base_content == "hello"
        assert block.path == "anonymous"
        assert block.id is not None
        assert block.bind_lineage == []

    def test_pure_with_custom_path(self):
        """Pure can specify a custom path."""
        block = KBlock.pure("content", path="custom/path.md")

        assert block.content == "content"
        assert block.path == "custom/path.md"

    def test_map_applies_pure_function(self):
        """Map applies a pure function to content."""
        block = KBlock.pure("hello")
        result = block.map(str.upper)

        assert result.content == "HELLO"
        # Map uses bind internally, so creates lineage
        assert len(result.bind_lineage) >= 1

    def test_map_is_bind_of_pure_composition(self):
        """map f = bind (pure . f)"""
        block = KBlock.pure("hello")

        # Using map
        via_map = block.map(str.upper)

        # Using bind(pure . f) explicitly
        via_bind = block.bind(lambda x: KBlock.pure(x.upper()))

        # Content should be equivalent
        assert via_map.content == via_bind.content


# -----------------------------------------------------------------------------
# Operator Tests
# -----------------------------------------------------------------------------


class TestRshiftOperator:
    """Test the >> operator for monadic bind."""

    def test_rshift_is_bind(self):
        """>> is syntactic sugar for bind."""
        block = KBlock.pure("hello")

        via_bind = block.bind(append_suffix)
        via_rshift = block >> append_suffix

        assert via_bind.content == via_rshift.content

    def test_rshift_chains(self):
        """>> chains multiple transformations."""
        result = KBlock.pure("a") >> append_suffix >> prepend_prefix >> wrap_brackets

        assert result.content == "[prefix_a_suffix]"

    def test_rshift_preserves_lineage(self):
        """>> preserves lineage correctly."""
        result = KBlock.pure("x") >> upper_transform >> wrap_brackets

        assert len(result.bind_lineage) == 2
        assert result.content == "[X]"


# -----------------------------------------------------------------------------
# Serialization Tests
# -----------------------------------------------------------------------------


class TestLineageSerialization:
    """Test that bind_lineage serializes and deserializes correctly."""

    def test_lineage_edge_to_dict(self):
        """LineageEdge serializes to dict."""
        edge = LineageEdge(
            from_id="kb_123",
            to_id="kb_456",
            operation="transform",
        )

        data = edge.to_dict()

        assert data["from_id"] == "kb_123"
        assert data["to_id"] == "kb_456"
        assert data["operation"] == "transform"
        assert "timestamp" in data

    def test_lineage_edge_from_dict(self):
        """LineageEdge deserializes from dict."""
        data = {
            "from_id": "kb_123",
            "to_id": "kb_456",
            "operation": "transform",
            "timestamp": "2025-01-01T00:00:00+00:00",
        }

        edge = LineageEdge.from_dict(data)

        assert edge.from_id == "kb_123"
        assert edge.to_id == "kb_456"
        assert edge.operation == "transform"

    def test_kblock_with_lineage_serializes(self):
        """K-Block with bind_lineage serializes correctly."""
        block = KBlock.pure("start")
        result = block >> append_suffix >> prepend_prefix

        data = result.to_dict()

        assert "bind_lineage" in data
        assert len(data["bind_lineage"]) == 2

    def test_kblock_with_lineage_round_trips(self):
        """K-Block with bind_lineage round-trips through serialization."""
        block = KBlock.pure("start")
        result = block >> append_suffix >> prepend_prefix

        # Serialize and deserialize
        data = result.to_dict()
        restored = KBlock.from_dict(data)

        # Content should match
        assert restored.content == result.content

        # Lineage should match
        assert len(restored.bind_lineage) == len(result.bind_lineage)
        for orig, rest in zip(result.bind_lineage, restored.bind_lineage):
            assert orig.from_id == rest.from_id
            assert orig.to_id == rest.to_id
            assert orig.operation == rest.operation


# -----------------------------------------------------------------------------
# Edge Cases
# -----------------------------------------------------------------------------


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_content(self):
        """Pure with empty content works."""
        block = KBlock.pure("")
        result = block >> append_suffix

        assert result.content == "_suffix"
        assert len(result.bind_lineage) == 1

    def test_long_chain(self):
        """Long bind chain accumulates lineage correctly."""
        block = KBlock.pure("x")

        # Chain 10 transformations
        for _ in range(10):
            block = block >> append_suffix

        assert block.content == "x" + "_suffix" * 10
        assert len(block.bind_lineage) == 10

    def test_bind_returning_complex_kblock(self):
        """Bind with function returning pre-existing K-Block works."""

        def complex_transform(content: str) -> KBlock:
            # Create a K-Block with some properties
            block = KBlock.pure(content + "_complex")
            return block

        result = KBlock.pure("start") >> complex_transform

        assert result.content == "start_complex"
        assert len(result.bind_lineage) == 1

    def test_identity_chain(self):
        """Identity function chain preserves content."""
        block = KBlock.pure("unchanged")
        result = block >> identity_transform >> identity_transform

        assert result.content == "unchanged"
        assert len(result.bind_lineage) == 2


# -----------------------------------------------------------------------------
# Witness Bridge Tests (P2: K-Block → Witness Integration)
# -----------------------------------------------------------------------------


class MockWitnessBridge:
    """
    Mock implementation of WitnessBridgeProtocol for testing.

    Records all emit_bind_mark calls for verification.
    """

    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.mark_id_counter = 0

    def emit_bind_mark(
        self,
        from_block: KBlock,
        to_block: KBlock,
        edge: LineageEdge,
        operation: str,
    ) -> str | None:
        """Record the call and return a mock mark ID."""
        self.mark_id_counter += 1
        mark_id = f"mock-mark-{self.mark_id_counter}"
        self.calls.append(
            {
                "from_id": from_block.id,
                "to_id": to_block.id,
                "operation": operation,
                "mark_id": mark_id,
            }
        )
        return mark_id


class FailingWitnessBridge:
    """Bridge that always fails to test error handling."""

    def emit_bind_mark(
        self,
        from_block: KBlock,
        to_block: KBlock,
        edge: LineageEdge,
        operation: str,
    ) -> str | None:
        """Always raises an exception."""
        raise RuntimeError("Bridge failure simulated")


class TestWitnessBridge:
    """
    Test the K-Block → Witness bridge integration (P2).

    These tests verify that:
    1. Bridge is called when configured
    2. Mark ID is attached to result metadata
    3. Bridge failures don't break K-Block operations
    4. No bridge = no mark emission (standalone mode)
    """

    def test_no_bridge_by_default(self):
        """By default, no bridge is configured."""
        # Reset to ensure clean state
        set_witness_bridge(None)

        assert get_witness_bridge() is None

        # Bind should work without any bridge
        block = KBlock.pure("content")
        result = block >> append_suffix

        assert result.content == "content_suffix"
        # No mark_id in metadata when no bridge
        assert "witness_mark_id" not in result.metadata

    def test_bridge_is_called_on_bind(self):
        """Bridge.emit_bind_mark is called when bind() executes."""
        bridge = MockWitnessBridge()
        set_witness_bridge(bridge)

        try:
            block = KBlock.pure("content")
            result = block >> append_suffix

            # Bridge should have been called once
            assert len(bridge.calls) == 1
            assert bridge.calls[0]["from_id"] == block.id
            assert bridge.calls[0]["to_id"] == result.id
            assert bridge.calls[0]["operation"] == "append_suffix"
        finally:
            set_witness_bridge(None)

    def test_mark_id_attached_to_metadata(self):
        """Mark ID from bridge is attached to result metadata."""
        bridge = MockWitnessBridge()
        set_witness_bridge(bridge)

        try:
            block = KBlock.pure("content")
            result = block >> append_suffix

            # Mark ID should be in metadata
            assert "witness_mark_id" in result.metadata
            assert result.metadata["witness_mark_id"] == "mock-mark-1"
        finally:
            set_witness_bridge(None)

    def test_bridge_called_for_each_bind(self):
        """Bridge is called for each bind in a chain."""
        bridge = MockWitnessBridge()
        set_witness_bridge(bridge)

        try:
            result = KBlock.pure("x") >> append_suffix >> prepend_prefix

            # Bridge should have been called twice
            assert len(bridge.calls) == 2
            assert bridge.calls[0]["operation"] == "append_suffix"
            assert bridge.calls[1]["operation"] == "prepend_prefix"

            # Result should have the LAST mark ID (most recent bind)
            assert result.metadata["witness_mark_id"] == "mock-mark-2"
        finally:
            set_witness_bridge(None)

    def test_bridge_failure_does_not_break_bind(self):
        """Bridge failures are caught; bind() still works."""
        bridge = FailingWitnessBridge()
        set_witness_bridge(bridge)

        try:
            block = KBlock.pure("content")
            # Should not raise even though bridge fails
            result = block >> append_suffix

            # Content and lineage should still work
            assert result.content == "content_suffix"
            assert len(result.bind_lineage) == 1

            # No mark_id since bridge failed
            assert "witness_mark_id" not in result.metadata
        finally:
            set_witness_bridge(None)

    def test_set_and_get_bridge(self):
        """set_witness_bridge and get_witness_bridge work correctly."""
        # Start clean
        set_witness_bridge(None)
        assert get_witness_bridge() is None

        # Set a bridge
        bridge = MockWitnessBridge()
        set_witness_bridge(bridge)
        assert get_witness_bridge() is bridge

        # Clear it
        set_witness_bridge(None)
        assert get_witness_bridge() is None

    def test_bridge_protocol_is_runtime_checkable(self):
        """WitnessBridgeProtocol is runtime checkable."""
        bridge = MockWitnessBridge()

        # Protocol should be recognized at runtime
        assert isinstance(bridge, WitnessBridgeProtocol)

        # Non-conforming objects should not match
        class NotABridge:
            pass

        assert not isinstance(NotABridge(), WitnessBridgeProtocol)

    def test_metadata_preserved_with_mark_id(self):
        """Existing metadata is preserved when adding mark_id."""
        bridge = MockWitnessBridge()
        set_witness_bridge(bridge)

        try:
            # Create a K-Block with some metadata
            def transform_with_metadata(content: str) -> KBlock:
                block = KBlock.pure(content + "_transformed")
                block.metadata = {"original": True, "version": 1}
                return block

            result = KBlock.pure("start") >> transform_with_metadata

            # Original metadata should be preserved
            assert result.metadata.get("original") is True
            assert result.metadata.get("version") == 1
            # Mark ID should be added
            assert result.metadata.get("witness_mark_id") == "mock-mark-1"
        finally:
            set_witness_bridge(None)
