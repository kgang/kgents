"""
Tests for Kleisli Witness Composition.

These tests verify:
1. Monad laws (left identity, right identity, associativity)
2. Kleisli composition preserves traces
3. Witnessed decorator works correctly
4. Utility functions work as expected

Theory validation:
    The Writer monad laws are the foundation of witnessed composition.
    If these laws fail, the entire witness system is unsound.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import pytest

from services.witness.kleisli import (
    Witnessed,
    kleisli_chain,
    kleisli_compose,
    link_marks,
    merge_witnessed,
    witness_value,
    witnessed_operation,
    witnessed_sync,
)
from services.witness.mark import Mark, Response, Stimulus, UmweltSnapshot, generate_mark_id

# =============================================================================
# Test Fixtures
# =============================================================================


def mock_mark(action: str) -> Mark:
    """Create a mock mark for testing."""
    return Mark(
        id=generate_mark_id(),
        origin="test",
        stimulus=Stimulus(kind="test", content=action, source="test"),
        response=Response(kind="test", content=f"result of {action}", success=True),
        umwelt=UmweltSnapshot.system(),
        timestamp=datetime.now(timezone.utc),
        tags=("test", action),
    )


# =============================================================================
# Monad Law Tests
# =============================================================================


class TestMonadLaws:
    """Test Writer monad laws for Witnessed."""

    def test_left_identity(self):
        """
        Left identity: pure(a) >>= f ≡ f(a)

        Lifting a value into Witnessed and then binding should give
        the same result as applying f directly.
        """
        a = "test_value"
        f = lambda x: Witnessed(value=x.upper(), marks=[mock_mark("f")])

        lhs = Witnessed.pure(a).bind(f)
        rhs = f(a)

        # Values must be equal
        assert lhs.value == rhs.value
        # Both should have one mark from f
        assert len(lhs.marks) == 1
        assert len(rhs.marks) == 1

    def test_right_identity(self):
        """
        Right identity: m >>= pure ≡ m

        Binding with pure should return the original value.
        """
        m = Witnessed(value="test", marks=[mock_mark("original")])

        lhs = m.bind(Witnessed.pure)

        # Value must be preserved
        assert lhs.value == m.value
        # Marks should be preserved (pure adds no marks)
        assert len(lhs.marks) == len(m.marks)

    def test_associativity(self):
        """
        Associativity: (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)

        The order of binding should not matter for the value.
        """
        m = Witnessed.pure(5)
        f = lambda x: Witnessed(value=x * 2, marks=[mock_mark("f")])
        g = lambda x: Witnessed(value=x + 1, marks=[mock_mark("g")])

        # Left-associated
        lhs = m.bind(f).bind(g)

        # Right-associated
        rhs = m.bind(lambda x: f(x).bind(g))

        # Values must be equal
        assert lhs.value == rhs.value
        # Both should have marks from f and g
        assert len(lhs.marks) == 2
        assert len(rhs.marks) == 2


# =============================================================================
# Kleisli Composition Tests
# =============================================================================


class TestKleisliComposition:
    """Test Kleisli composition of witnessed operations."""

    def test_kleisli_compose_preserves_traces(self):
        """
        (f >=> g)(a) should have traces from both f and g.
        """
        f = lambda x: Witnessed(value=x * 2, marks=[mock_mark("f")])
        g = lambda x: Witnessed(value=x + 1, marks=[mock_mark("g")])

        composed = kleisli_compose(f, g)
        result = composed(5)

        assert result.value == 11  # (5 * 2) + 1
        assert len(result.marks) == 2
        # Verify order: f's mark should come first
        assert "f" in result.marks[0].tags
        assert "g" in result.marks[1].tags

    def test_kleisli_compose_empty_traces(self):
        """Composing operations with no marks should still work."""
        f = lambda x: Witnessed.pure(x * 2)
        g = lambda x: Witnessed.pure(x + 1)

        composed = kleisli_compose(f, g)
        result = composed(5)

        assert result.value == 11
        assert len(result.marks) == 0

    def test_kleisli_chain_multiple(self):
        """Chain multiple Kleisli arrows."""
        f = lambda x: Witnessed(value=x * 2, marks=[mock_mark("f")])
        g = lambda x: Witnessed(value=x + 1, marks=[mock_mark("g")])
        h = lambda x: Witnessed(value=x ** 2, marks=[mock_mark("h")])

        chained = kleisli_chain(f, g, h)
        result = chained(3)

        # (3 * 2) = 6, (6 + 1) = 7, (7 ** 2) = 49
        assert result.value == 49
        assert len(result.marks) == 3
        # Verify order
        assert "f" in result.marks[0].tags
        assert "g" in result.marks[1].tags
        assert "h" in result.marks[2].tags

    def test_kleisli_chain_single(self):
        """Chain with single function should just return that function."""
        f = lambda x: Witnessed(value=x * 2, marks=[mock_mark("f")])

        chained = kleisli_chain(f)
        result = chained(5)

        assert result.value == 10
        assert len(result.marks) == 1

    def test_kleisli_chain_empty_raises(self):
        """Chain with no functions should raise."""
        with pytest.raises(ValueError):
            kleisli_chain()


# =============================================================================
# Witnessed Operations Tests
# =============================================================================


class TestWitnessedOperations:
    """Test witnessed operation decorators."""

    @pytest.mark.asyncio
    async def test_witnessed_operation_basic(self):
        """Basic witnessed operation should produce mark."""

        @witnessed_operation(action="double")
        async def double(x: int) -> int:
            return x * 2

        result = await double(5)

        assert result.value == 10
        assert len(result.marks) == 1
        assert result.marks[0].stimulus.content == "double"

    @pytest.mark.asyncio
    async def test_witnessed_operation_with_reasoning(self):
        """Witnessed operation with reasoning function."""

        @witnessed_operation(
            action="analyze",
            reasoning_fn=lambda x: f"Analyzed input of length {len(x)}",
        )
        async def analyze(text: str) -> str:
            return text.upper()

        result = await analyze("hello")

        assert result.value == "HELLO"
        assert len(result.marks) == 1
        assert "Analyzed input of length 5" in result.marks[0].response.metadata.get("reasoning", "")

    @pytest.mark.asyncio
    async def test_witnessed_operation_with_principles(self):
        """Witnessed operation with constitutional principles."""

        @witnessed_operation(
            action="compose",
            principles=("composable", "generative"),
        )
        async def compose(a: str, b: str) -> str:
            return f"{a} + {b}"

        result = await compose("foo", "bar")

        assert result.value == "foo + bar"
        assert "composable" in result.marks[0].tags
        assert "generative" in result.marks[0].tags

    def test_witnessed_sync_basic(self):
        """Synchronous witnessed operation."""

        @witnessed_sync(action="compute")
        def compute(x: int) -> int:
            return x ** 2

        result = compute(5)

        assert result.value == 25
        assert len(result.marks) == 1
        assert result.marks[0].stimulus.content == "compute"

    @pytest.mark.asyncio
    async def test_witnessed_operations_compose(self):
        """Witnessed operations can be composed with Kleisli."""

        @witnessed_operation(action="step1")
        async def step1(x: int) -> int:
            return x * 2

        @witnessed_operation(action="step2")
        async def step2(x: int) -> int:
            return x + 10

        # Start with pure value
        result = Witnessed.pure(5)

        # Chain the operations
        result = await result.bind_async(step1)
        result = await result.bind_async(step2)

        assert result.value == 20  # (5 * 2) + 10
        assert len(result.marks) == 2
        assert result.marks[0].stimulus.content == "step1"
        assert result.marks[1].stimulus.content == "step2"


# =============================================================================
# Utility Function Tests
# =============================================================================


class TestUtilityFunctions:
    """Test witness utility functions."""

    def test_witness_value_basic(self):
        """witness_value creates Witnessed with one mark."""
        result = witness_value(42, action="initial", reasoning="Starting value")

        assert result.value == 42
        assert len(result.marks) == 1
        assert "witnessed_value" in result.marks[0].tags

    def test_witness_value_with_metadata(self):
        """witness_value can include metadata."""
        result = witness_value(
            "test",
            action="init",
            reasoning="Testing",
            custom_field="custom_value",
        )

        assert result.value == "test"
        assert result.marks[0].metadata.get("custom_field") == "custom_value"

    def test_link_marks_creates_causal_links(self):
        """link_marks creates links between consecutive marks."""
        # Create witnessed with multiple marks
        marks = [mock_mark(f"step{i}") for i in range(3)]
        witnessed = Witnessed(value="result", marks=marks)

        linked = link_marks(witnessed)

        assert linked.value == witnessed.value
        assert len(linked.marks) == 3
        # First mark has no links
        assert len(linked.marks[0].links) == 0
        # Subsequent marks have links to previous
        assert len(linked.marks[1].links) == 1
        assert len(linked.marks[2].links) == 1

    def test_link_marks_empty(self):
        """link_marks handles empty or single marks."""
        empty = Witnessed(value="x", marks=[])
        single = Witnessed(value="x", marks=[mock_mark("only")])

        assert link_marks(empty).marks == []
        assert len(link_marks(single).marks) == 1

    def test_merge_witnessed(self):
        """merge_witnessed combines marks from multiple sources."""
        w1 = Witnessed(value=1, marks=[mock_mark("a"), mock_mark("b")])
        w2 = Witnessed(value=2, marks=[mock_mark("c")])
        w3 = Witnessed(value=3, marks=[mock_mark("d"), mock_mark("e")])

        merged = merge_witnessed(w1, w2, w3)

        assert len(merged) == 5
        # Should be sorted by timestamp (in creation order for this test)

    def test_latest_mark(self):
        """latest_mark returns the most recent mark."""
        marks = [mock_mark(f"step{i}") for i in range(3)]
        witnessed = Witnessed(value="result", marks=marks)

        latest = witnessed.latest_mark()

        assert latest is not None
        assert "step2" in latest.tags

    def test_marks_by_origin(self):
        """marks_by_origin filters by origin."""
        mark1 = Mark(
            origin="witness",
            stimulus=Stimulus(kind="test", content="a", source="test"),
            response=Response(kind="test", content="", success=True),
            umwelt=UmweltSnapshot.system(),
        )
        mark2 = Mark(
            origin="brain",
            stimulus=Stimulus(kind="test", content="b", source="test"),
            response=Response(kind="test", content="", success=True),
            umwelt=UmweltSnapshot.system(),
        )
        witnessed = Witnessed(value="x", marks=[mark1, mark2])

        witness_marks = witnessed.marks_by_origin("witness")
        brain_marks = witnessed.marks_by_origin("brain")

        assert len(witness_marks) == 1
        assert len(brain_marks) == 1

    def test_marks_with_tag(self):
        """marks_with_tag filters by tag."""
        mark1 = mock_mark("tagged")
        witnessed = Witnessed(value="x", marks=[mark1])

        tagged = witnessed.marks_with_tag("tagged")

        assert len(tagged) == 1


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for witnessed composition."""

    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test a full witnessed pipeline."""

        @witnessed_operation(action="parse", principles=("composable",))
        async def parse(text: str) -> dict:
            return {"original": text, "length": len(text)}

        @witnessed_operation(action="validate", principles=("ethical",))
        async def validate(data: dict) -> dict:
            return {**data, "valid": True}

        @witnessed_operation(action="transform", principles=("generative",))
        async def transform(data: dict) -> str:
            return f"Processed: {data['original']}"

        # Execute pipeline
        result = Witnessed.pure("hello world")
        result = await result.bind_async(parse)
        result = await result.bind_async(validate)
        result = await result.bind_async(transform)

        assert result.value == "Processed: hello world"
        assert len(result.marks) == 3

        # Verify each step
        assert result.marks[0].stimulus.content == "parse"
        assert result.marks[1].stimulus.content == "validate"
        assert result.marks[2].stimulus.content == "transform"

    def test_verify_laws_method(self):
        """The verify_laws method should work."""
        m = Witnessed.pure("test")
        f = lambda x: Witnessed(value=x.upper(), marks=[mock_mark("f")])

        laws = m.verify_laws(f)

        assert laws["left_identity"] is True
        assert laws["right_identity"] is True


# =============================================================================
# Property-Based Tests (Hypothesis)
# =============================================================================

# Note: These would use hypothesis for property-based testing.
# For now, we have the explicit law tests above.


class TestMonadLawsParametric:
    """Parametric tests for monad laws with various types."""

    @pytest.mark.parametrize("value", [0, 1, -1, 100, "", "hello", [], [1, 2, 3]])
    def test_right_identity_various_types(self, value):
        """Right identity should hold for various value types."""
        m = Witnessed(value=value, marks=[mock_mark("original")])
        lhs = m.bind(Witnessed.pure)
        assert lhs.value == m.value

    @pytest.mark.parametrize("n", [1, 2, 3, 5, 10])
    def test_composition_chain_length(self, n):
        """Kleisli chains of various lengths should work."""
        functions = [
            lambda x: Witnessed(value=x + i, marks=[mock_mark(f"step{i}")])
            for i in range(n)
        ]

        # Need to capture i properly
        def make_fn(i):
            return lambda x: Witnessed(value=x + i, marks=[mock_mark(f"step{i}")])

        functions = [make_fn(i) for i in range(n)]
        chained = kleisli_chain(*functions)

        result = chained(0)

        expected_value = sum(range(n))  # 0 + 0 + 1 + 2 + ... + (n-1)
        assert result.value == expected_value
        assert len(result.marks) == n
