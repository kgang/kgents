"""
Hypothesis strategies for property-based testing.

Philosophy: Spec is compression; strategies generate from that compression.

Phase 3 of test evolution plan:
- Agent strategies for random composition
- DNA strategies for constraint fuzzing
- Type strategies for boundary testing
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeVar

# Hypothesis imports are optional
try:
    from hypothesis import assume, given, settings
    from hypothesis import strategies as st

    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    st = None  # type: ignore[assignment]
    given = None  # type: ignore[assignment]
    settings = None  # type: ignore[assignment,misc]
    assume = None  # type: ignore[assignment]


A = TypeVar("A")
B = TypeVar("B")


# =============================================================================
# Agent Strategies
# =============================================================================


if HYPOTHESIS_AVAILABLE:

    @st.composite
    def simple_agents(draw, input_type=int, output_type=int):
        """
        Generate simple deterministic agents.

        These agents apply an offset to their input, making them
        easy to verify composition laws.
        """

        @dataclass
        class GeneratedAgent:
            name: str
            _offset: int

            async def invoke(self, x: int) -> int:
                return x + self._offset

            def __rshift__(self, other):
                from typing import cast

                from bootstrap import Agent, compose

                return compose(cast(Agent[Any, Any], self), other)

        name = draw(st.text(min_size=1, max_size=10, alphabet="abcdefghijklmnop"))
        offset = draw(st.integers(min_value=-100, max_value=100))

        return GeneratedAgent(name=f"Agent_{name}", _offset=offset)

    @st.composite
    def agent_chains(draw, min_length=2, max_length=5):
        """Generate chains of composable agents."""
        length = draw(st.integers(min_value=min_length, max_value=max_length))
        return [draw(simple_agents()) for _ in range(length)]

    # =============================================================================
    # DNA Strategies
    # =============================================================================

    @st.composite
    def valid_dna(draw):
        """Generate valid DNA configurations."""
        from protocols.config.dna import BaseDNA

        exploration = draw(st.floats(min_value=0.01, max_value=0.5))

        return BaseDNA(exploration_budget=exploration)

    @st.composite
    def invalid_dna(draw):
        """Generate intentionally invalid DNA for constraint testing."""
        from protocols.config.dna import BaseDNA

        # Invalid: exploration <= 0 or > 0.5
        invalid_exploration = draw(
            st.one_of(
                st.floats(min_value=-1.0, max_value=0.0),
                st.floats(min_value=0.51, max_value=1.0),
            )
        )

        return BaseDNA(exploration_budget=invalid_exploration)

    @st.composite
    def hypothesis_dna(draw):
        """Generate valid HypothesisDNA for B-gent testing."""
        from protocols.config.dna import HypothesisDNA

        confidence = draw(st.floats(min_value=0.1, max_value=0.8))
        max_hypotheses = draw(st.integers(min_value=1, max_value=10))

        return HypothesisDNA(
            confidence_threshold=confidence,
            falsification_required=True,
            max_hypotheses=max_hypotheses,
        )

    # =============================================================================
    # Type Strategies
    # =============================================================================

    @st.composite
    def type_names(draw):
        """Generate valid type names."""
        base_types = ["int", "str", "float", "bool", "None", "Any"]
        generic_bases = ["List", "Dict", "Optional", "Tuple"]

        if draw(st.booleans()):
            return draw(st.sampled_from(base_types))
        else:
            base = draw(st.sampled_from(generic_bases))
            inner = draw(st.sampled_from(base_types))
            return f"{base}[{inner}]"

    # =============================================================================
    # Input Strategies
    # =============================================================================

    @st.composite  # type: ignore[untyped-decorator]
    def json_like_values(draw: Any) -> Any:
        """Generate JSON-compatible values for testing."""
        return draw(
            st.one_of(
                st.none(),
                st.booleans(),
                st.integers(),
                st.floats(allow_nan=False),
                st.text(max_size=100),
                st.lists(st.integers(), max_size=10),
                st.dictionaries(
                    st.text(min_size=1, max_size=20), st.integers(), max_size=5
                ),
            )
        )

    @st.composite  # type: ignore[untyped-decorator]
    def boundary_inputs(draw: Any) -> Any:
        """Generate boundary-case inputs for stress testing."""
        return draw(
            st.one_of(
                st.just(""),  # Empty string
                st.text(min_size=10000, max_size=10001),  # Very long string
                st.just(0),  # Zero
                st.just(-1),  # Negative
                st.just(2**31 - 1),  # Max int32
                st.just(2**63 - 1),  # Max int64
                st.just([]),  # Empty list
                st.just({}),  # Empty dict
                st.just(None),  # None
            )
        )

else:
    # Fallback stubs when hypothesis is not available

    def simple_agents(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        """Stub: hypothesis not available."""
        raise ImportError("hypothesis package required for property-based testing")

    def agent_chains(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        """Stub: hypothesis not available."""
        raise ImportError("hypothesis package required for property-based testing")

    def valid_dna(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        """Stub: hypothesis not available."""
        raise ImportError("hypothesis package required for property-based testing")

    def invalid_dna(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        """Stub: hypothesis not available."""
        raise ImportError("hypothesis package required for property-based testing")

    def type_names(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        """Stub: hypothesis not available."""
        raise ImportError("hypothesis package required for property-based testing")

    def hypothesis_dna(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        """Stub: hypothesis not available."""
        raise ImportError("hypothesis package required for property-based testing")

    def json_like_values(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        """Stub: hypothesis not available."""
        raise ImportError("hypothesis package required for property-based testing")

    def boundary_inputs(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        """Stub: hypothesis not available."""
        raise ImportError("hypothesis package required for property-based testing")
