"""
Tests for the Prompt Monad.

Verifies the three monadic laws:
1. Left Identity:  unit(x) >>= f ≡ f(x)
2. Right Identity: m >>= unit ≡ m
3. Associativity:  (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)

Also tests:
- Functor map preserves structure
- Trace accumulation
- Provenance tracking
- Combinators (sequence, traverse, join)
"""

import pytest

from protocols.prompt.monad import (
    PromptM,
    Source,
    join,
    lift_provenance,
    lift_trace,
    sequence,
    traverse,
)
from protocols.prompt.section_base import Section

# =============================================================================
# Monadic Law Tests
# =============================================================================


class TestMonadicLaws:
    """
    Tests for the three monadic laws.

    These are the fundamental guarantees that make PromptM a valid monad.
    All transformations must preserve these laws.
    """

    def test_left_identity(self) -> None:
        """
        Left Identity Law: unit(x) >>= f ≡ f(x)

        Lifting a value and immediately binding should be
        equivalent to just applying the function.
        """
        x = Section(name="test", content="hello", token_cost=5, required=True)

        def f(s):
            return PromptM.unit(s.with_content(s.content.upper()))

        # Left side: unit(x).bind(f)
        left = PromptM.unit(x).bind(f)

        # Right side: f(x)
        right = f(x)

        assert left.value.content == right.value.content
        assert left.value.name == right.value.name

    def test_right_identity(self) -> None:
        """
        Right Identity Law: m >>= unit ≡ m

        Binding with unit should not change the monad's value.
        """
        section = Section(name="test", content="hello", token_cost=5, required=True)
        m = PromptM(
            value=section,
            reasoning_trace=("trace1",),
            provenance=(Source.FILE,),
        )

        # m.bind(unit) should equal m in value
        result = m.bind(PromptM.unit)

        assert result.value.content == m.value.content
        assert result.value.name == m.value.name
        # Traces accumulate, but provenance remains
        assert "trace1" in result.reasoning_trace

    def test_associativity(self) -> None:
        """
        Associativity Law: (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)

        Chaining binds should be associative.
        """
        section = Section(name="test", content="hello", token_cost=5, required=True)
        m = PromptM.unit(section)

        def f(s):
            return PromptM(
                value=s.with_content(s.content.upper()),
                reasoning_trace=("uppercased",),
                provenance=(),
            )

        def g(s):
            return PromptM(
                value=s.with_content(s.content + "!"),
                reasoning_trace=("exclaimed",),
                provenance=(),
            )

        # Left side: (m >>= f) >>= g
        left = m.bind(f).bind(g)

        # Right side: m >>= (λx. f(x) >>= g)
        right = m.bind(lambda x: f(x).bind(g))

        assert left.value.content == right.value.content
        assert left.value.content == "HELLO!"

    def test_associativity_with_traces(self) -> None:
        """Associativity should also preserve trace ordering."""
        m = PromptM(
            value="start",
            reasoning_trace=("m",),
            provenance=(),
        )

        def f(x):
            return PromptM(
                value=x + "_f",
                reasoning_trace=("f",),
                provenance=(Source.FILE,),
            )

        def g(x):
            return PromptM(
                value=x + "_g",
                reasoning_trace=("g",),
                provenance=(Source.LLM,),
            )

        left = m.bind(f).bind(g)
        right = m.bind(lambda x: f(x).bind(g))

        assert left.reasoning_trace == right.reasoning_trace
        assert left.provenance == right.provenance


# =============================================================================
# Functor Tests
# =============================================================================


class TestFunctor:
    """Tests for the functor (map) operation."""

    def test_map_transforms_value(self) -> None:
        """Map applies function to wrapped value."""
        m = PromptM.unit("hello")
        result = m.map(str.upper)
        assert result.value == "HELLO"

    def test_map_preserves_trace(self) -> None:
        """Map does not change reasoning trace."""
        m = PromptM(
            value="hello",
            reasoning_trace=("trace1", "trace2"),
            provenance=(Source.FILE,),
        )
        result = m.map(str.upper)

        assert result.reasoning_trace == ("trace1", "trace2")
        assert result.provenance == (Source.FILE,)

    def test_map_identity(self) -> None:
        """Functor identity: map(id) ≡ id"""
        m = PromptM.unit("hello")
        result = m.map(lambda x: x)
        assert result.value == m.value

    def test_map_composition(self) -> None:
        """Functor composition: map(f . g) ≡ map(f) . map(g)"""
        m = PromptM.unit("hello")
        f = str.upper

        def g(s):
            return s + "!"

        # map(f . g)
        left = m.map(lambda x: f(g(x)))

        # map(f) . map(g)
        right = m.map(g).map(f)

        assert left.value == right.value


# =============================================================================
# Trace and Provenance Tests
# =============================================================================


class TestTraceAccumulation:
    """Tests for reasoning trace accumulation."""

    def test_bind_accumulates_traces(self) -> None:
        """Bind should accumulate traces from both monads."""
        m = PromptM(
            value="start",
            reasoning_trace=("step1",),
            provenance=(),
        )

        def f(x):
            return PromptM(
                value=x + "_end",
                reasoning_trace=("step2",),
                provenance=(),
            )

        result = m.bind(f)

        assert result.reasoning_trace == ("step1", "step2")

    def test_with_trace_adds_entry(self) -> None:
        """with_trace adds a single trace entry."""
        m = PromptM.unit("hello")
        result = m.with_trace("processed")

        assert result.reasoning_trace == ("processed",)
        assert result.value == "hello"

    def test_trace_chain(self) -> None:
        """Multiple with_trace calls chain correctly."""
        m = PromptM.unit("hello")
        result = m.with_trace("step1").with_trace("step2").with_trace("step3")

        assert result.reasoning_trace == ("step1", "step2", "step3")


class TestProvenance:
    """Tests for provenance tracking."""

    def test_bind_accumulates_provenance(self) -> None:
        """Bind should accumulate provenance from both monads."""
        m = PromptM(
            value="start",
            reasoning_trace=(),
            provenance=(Source.FILE,),
        )

        def f(x):
            return PromptM(
                value=x + "_end",
                reasoning_trace=(),
                provenance=(Source.LLM,),
            )

        result = m.bind(f)

        assert result.provenance == (Source.FILE, Source.LLM)

    def test_with_provenance_adds_source(self) -> None:
        """with_provenance adds a source."""
        m = PromptM.unit("hello")
        result = m.with_provenance(Source.TEMPLATE)

        assert result.provenance == (Source.TEMPLATE,)

    def test_all_sources_exist(self) -> None:
        """All expected source types exist."""
        expected_sources = [
            Source.TEMPLATE,
            Source.FILE,
            Source.GIT,
            Source.LLM,
            Source.HABIT,
            Source.TEXTGRAD,
            Source.FUSION,
            Source.ROLLBACK,
            Source.USER,
        ]
        for source in expected_sources:
            assert isinstance(source, Source)


# =============================================================================
# Combinator Tests
# =============================================================================


class TestCombinators:
    """Tests for monadic combinators."""

    def test_sequence_empty(self) -> None:
        """Sequence of empty list returns empty list."""
        result = sequence([])
        assert result.value == []

    def test_sequence_collects_values(self) -> None:
        """Sequence collects values from list of monads."""
        monads = [PromptM.unit(1), PromptM.unit(2), PromptM.unit(3)]
        result = sequence(monads)

        assert result.value == [1, 2, 3]

    def test_sequence_accumulates_traces(self) -> None:
        """Sequence accumulates traces from all monads."""
        monads = [
            PromptM(value=1, reasoning_trace=("a",), provenance=()),
            PromptM(value=2, reasoning_trace=("b",), provenance=()),
            PromptM(value=3, reasoning_trace=("c",), provenance=()),
        ]
        result = sequence(monads)

        assert result.reasoning_trace == ("a", "b", "c")

    def test_traverse_maps_and_sequences(self) -> None:
        """Traverse maps function and sequences results."""
        items = ["a", "b", "c"]
        result = traverse(items, lambda x: PromptM.unit(x.upper()))

        assert result.value == ["A", "B", "C"]

    def test_join_flattens(self) -> None:
        """Join flattens nested monad."""
        inner = PromptM(
            value="hello",
            reasoning_trace=("inner",),
            provenance=(Source.LLM,),
        )
        outer = PromptM(
            value=inner,
            reasoning_trace=("outer",),
            provenance=(Source.FILE,),
        )

        result = join(outer)

        assert result.value == "hello"
        assert result.reasoning_trace == ("outer", "inner")
        assert result.provenance == (Source.FILE, Source.LLM)


# =============================================================================
# Lifting Function Tests
# =============================================================================


class TestLiftingFunctions:
    """Tests for lift_trace and lift_provenance."""

    def test_lift_trace(self) -> None:
        """lift_trace creates function that adds trace."""
        m = PromptM.unit("hello")
        result = m.bind(lift_trace("processed"))

        assert result.value == "hello"
        assert result.reasoning_trace == ("processed",)

    def test_lift_provenance(self) -> None:
        """lift_provenance creates function that adds source."""
        m = PromptM.unit("hello")
        result = m.bind(lift_provenance(Source.FILE))

        assert result.value == "hello"
        assert result.provenance == (Source.FILE,)

    def test_lift_chain(self) -> None:
        """Lifting functions can be chained."""
        m = PromptM.unit("hello")
        result = (
            m.bind(lift_trace("step1")).bind(lift_provenance(Source.FILE)).bind(lift_trace("step2"))
        )

        assert result.reasoning_trace == ("step1", "step2")
        assert result.provenance == (Source.FILE,)


# =============================================================================
# Operator Tests
# =============================================================================


class TestOperators:
    """Tests for operator overloads."""

    def test_rshift_is_bind(self) -> None:
        """>> operator is alias for bind."""
        m = PromptM.unit("hello")

        def f(x):
            return PromptM.unit(x.upper())

        result1 = m >> f
        result2 = m.bind(f)

        assert result1.value == result2.value

    def test_or_is_map(self) -> None:
        """| operator is alias for map."""
        m = PromptM.unit("hello")

        result1 = m | str.upper
        result2 = m.map(str.upper)

        assert result1.value == result2.value

    def test_operator_chaining(self) -> None:
        """Operators can be chained fluently."""
        m = PromptM.unit("hello")
        result = m | str.upper | (lambda s: s + "!")

        assert result.value == "HELLO!"


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests with Section types."""

    def test_section_transformation_chain(self) -> None:
        """Chain of section transformations works correctly."""
        section = Section(name="test", content="hello", token_cost=5, required=True)

        result = (
            PromptM.unit(section)
            .with_trace("Starting transformation")
            .with_provenance(Source.TEMPLATE)
            .map(lambda s: s.with_content(s.content.upper()))
            .with_trace("Uppercased content")
            .map(lambda s: s.with_content(s.content + " WORLD"))
            .with_trace("Appended text")
        )

        assert result.value.content == "HELLO WORLD"
        assert len(result.reasoning_trace) == 3
        assert Source.TEMPLATE in result.provenance

    def test_checkpoint_preservation(self) -> None:
        """Checkpoint ID is preserved through transformations."""
        m = PromptM.unit("hello").with_checkpoint("ckpt-123")
        result = m.map(str.upper).map(lambda s: s + "!")

        assert result.checkpoint_id == "ckpt-123"

    def test_checkpoint_overwritten_by_bind(self) -> None:
        """Later bind can set new checkpoint."""
        m = PromptM.unit("hello").with_checkpoint("old")

        def f(x):
            return PromptM(
                value=x.upper(),
                reasoning_trace=(),
                provenance=(),
                checkpoint_id="new",
            )

        result = m.bind(f)
        assert result.checkpoint_id == "new"


# =============================================================================
# Property-Based Tests (if hypothesis available)
# =============================================================================


try:
    from hypothesis import given, strategies as st

    class TestMonadProperties:
        """Property-based tests for monad laws."""

        @given(st.text(min_size=1, max_size=100))
        def test_left_identity_property(self, x: str) -> None:
            """Left identity holds for arbitrary strings."""

            def f(s):
                return PromptM.unit(s.upper())

            left = PromptM.unit(x).bind(f)
            right = f(x)

            assert left.value == right.value

        @given(st.text(min_size=1, max_size=100))
        def test_right_identity_property(self, x: str) -> None:
            """Right identity holds for arbitrary strings."""
            m = PromptM.unit(x)
            result = m.bind(PromptM.unit)

            assert result.value == m.value

        @given(st.text(min_size=1, max_size=50))
        def test_associativity_property(self, x: str) -> None:
            """Associativity holds for arbitrary strings."""
            m = PromptM.unit(x)

            def f(s):
                return PromptM.unit(s.upper())

            def g(s):
                return PromptM.unit(s + "!")

            left = m.bind(f).bind(g)
            right = m.bind(lambda a: f(a).bind(g))

            assert left.value == right.value

except ImportError:
    # hypothesis not installed
    pass


__all__ = [
    "TestMonadicLaws",
    "TestFunctor",
    "TestTraceAccumulation",
    "TestProvenance",
    "TestCombinators",
    "TestLiftingFunctions",
    "TestOperators",
    "TestIntegration",
]
