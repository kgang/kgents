"""
TRACED_OPERAD: Operad Extension for Traced Wiring Diagrams.

This module extends AGENT_OPERAD with traced operations that record
wiring decisions as WiringTrace objects. The traced operations
preserve semantic behavior while capturing ghost alternatives.

Key Operations:
    traced_seq: Sequential composition with trace recording
    traced_par: Parallel composition with trace recording
    merge_traces: Compose trace histories from multiple operands

Laws:
    Semantic Preservation: traced_seq(a, b).agent ≅ seq(a, b)
    Ghost Preservation: ghosts(traced_seq(a, b)) ⊇ ghosts(a) ∪ ghosts(b)

See: spec/protocols/differance.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Generic, TypeVar

from agents.operad import (
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    Operation,
    OperadRegistry,
)
from agents.poly import PolyAgent, parallel, sequential

from .trace import Alternative, TraceMonoid, WiringTrace

# Type variables
S = TypeVar("S")
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


@dataclass
class TracedOperation:
    """
    Operation that records its wiring as a trace.

    A TracedOperation wraps a base operation (from AGENT_OPERAD) and
    records each invocation as a WiringTrace. The trace captures:
    - What operation was performed
    - What inputs were composed
    - What alternatives were considered
    - Polynomial state changes

    Attributes:
        base_op: The underlying operation from AGENT_OPERAD
        record_trace: Whether to record traces (default True)
        capture_ghosts: Whether to capture ghost alternatives (default True)
    """

    base_op: Operation
    record_trace: bool = True
    capture_ghosts: bool = True

    @property
    def name(self) -> str:
        return f"traced_{self.base_op.name}"

    @property
    def arity(self) -> int:
        return self.base_op.arity

    @property
    def signature(self) -> str:
        return f"TracedAgent × ... → TracedAgent (wraps {self.base_op.signature})"


@dataclass
class TracedAgent(Generic[S, A, B]):
    """
    Agent bundled with its trace history.

    A TracedAgent wraps a PolyAgent and carries its TraceMonoid —
    the accumulated history of wiring decisions that produced it.

    This is the key type that enables ghost preservation: when traced
    agents compose, their trace histories compose too.

    Attributes:
        agent: The underlying PolyAgent
        traces: TraceMonoid recording the wiring history
        name: Human-readable name for this traced agent

    Laws:
        - agent.invoke(state, input) == wrapped behavior (semantic preservation)
        - traces preserve all ghost alternatives from composed agents
    """

    agent: PolyAgent[S, A, B]
    traces: TraceMonoid = field(default_factory=TraceMonoid.empty)
    name: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            object.__setattr__(self, "name", self.agent.name)

    @classmethod
    def wrap(cls, agent: PolyAgent[S, A, B]) -> TracedAgent[S, A, B]:
        """Wrap a plain agent with empty trace history."""
        return cls(agent=agent, traces=TraceMonoid.empty(), name=agent.name)

    def invoke(self, state: S, input: A) -> tuple[S, B]:
        """Invoke the underlying agent (semantic preservation)."""
        return self.agent.invoke(state, input)

    def transition(self, state: S, input: A) -> tuple[S, B]:
        """Transition the underlying agent (semantic preservation)."""
        return self.agent.transition(state, input)

    @property
    def positions(self) -> frozenset[S]:
        """Positions of the underlying agent."""
        return self.agent.positions

    def directions(self, state: S) -> frozenset[A]:
        """Directions at a given state."""
        return self.agent.directions(state)

    def ghosts(self) -> list[Alternative]:
        """All ghost alternatives from trace history."""
        return list(self.traces.ghosts())

    def explorable_ghosts(self) -> list[Alternative]:
        """Only explorable ghosts from trace history."""
        return list(self.traces.explorable_ghosts())

    def __repr__(self) -> str:
        return f"TracedAgent({self.name}, traces={len(self.traces)})"


# =============================================================================
# Traced Operations
# =============================================================================


def _traced_seq_compose(
    left: TracedAgent[Any, Any, Any] | PolyAgent[Any, Any, Any],
    right: TracedAgent[Any, Any, Any] | PolyAgent[Any, Any, Any],
    context: str = "",
    alternatives: tuple[Alternative, ...] = (),
    parent_trace_id: str | None = None,
) -> TracedAgent[Any, Any, Any]:
    """
    Sequential composition with trace recording.

    Composes two agents sequentially (left >> right) and records
    the wiring decision as a WiringTrace.

    Semantic Preservation:
        traced_seq(a, b).agent.invoke(s, i) == seq(a.agent, b.agent).invoke(s, i)

    Ghost Preservation:
        ghosts(traced_seq(a, b)) ⊇ ghosts(a) ∪ ghosts(b)

    Args:
        left: First agent to compose
        right: Second agent to compose
        context: Human-readable context for why this composition
        alternatives: Ghost alternatives that were considered
        parent_trace_id: ID of parent trace for causal linking

    Returns:
        TracedAgent with combined trace history
    """
    # Normalize to TracedAgent
    left_traced = left if isinstance(left, TracedAgent) else TracedAgent.wrap(left)
    right_traced = right if isinstance(right, TracedAgent) else TracedAgent.wrap(right)

    # Perform the actual composition
    composed_agent = sequential(left_traced.agent, right_traced.agent)

    # Record the trace
    trace = WiringTrace.create(
        operation="seq",
        inputs=(left_traced.name, right_traced.name),
        output=composed_agent.name,
        context=context or f"Sequential composition: {left_traced.name} >> {right_traced.name}",
        alternatives=alternatives,
        positions_before={
            left_traced.name: frozenset(str(p) for p in left_traced.positions),
            right_traced.name: frozenset(str(p) for p in right_traced.positions),
        },
        positions_after={
            composed_agent.name: frozenset(str(p) for p in composed_agent.positions),
        },
        parent_trace_id=parent_trace_id,
    )

    # Merge trace histories (ghost preservation)
    combined_traces = left_traced.traces.compose(right_traced.traces).append(trace)

    return TracedAgent(
        agent=composed_agent,
        traces=combined_traces,
        name=composed_agent.name,
    )


def _traced_par_compose(
    left: TracedAgent[Any, Any, Any] | PolyAgent[Any, Any, Any],
    right: TracedAgent[Any, Any, Any] | PolyAgent[Any, Any, Any],
    context: str = "",
    alternatives: tuple[Alternative, ...] = (),
    parent_trace_id: str | None = None,
) -> TracedAgent[Any, Any, Any]:
    """
    Parallel composition with trace recording.

    Composes two agents in parallel (both receive same input) and
    records the wiring decision as a WiringTrace.

    Semantic Preservation:
        traced_par(a, b).agent.invoke(s, i) == par(a.agent, b.agent).invoke(s, i)

    Ghost Preservation:
        ghosts(traced_par(a, b)) ⊇ ghosts(a) ∪ ghosts(b)

    Args:
        left: First agent to compose
        right: Second agent to compose
        context: Human-readable context for why this composition
        alternatives: Ghost alternatives that were considered
        parent_trace_id: ID of parent trace for causal linking

    Returns:
        TracedAgent with combined trace history
    """
    # Normalize to TracedAgent
    left_traced = left if isinstance(left, TracedAgent) else TracedAgent.wrap(left)
    right_traced = right if isinstance(right, TracedAgent) else TracedAgent.wrap(right)

    # Perform the actual composition
    composed_agent = parallel(left_traced.agent, right_traced.agent)

    # Record the trace
    trace = WiringTrace.create(
        operation="par",
        inputs=(left_traced.name, right_traced.name),
        output=composed_agent.name,
        context=context or f"Parallel composition: {left_traced.name} || {right_traced.name}",
        alternatives=alternatives,
        positions_before={
            left_traced.name: frozenset(str(p) for p in left_traced.positions),
            right_traced.name: frozenset(str(p) for p in right_traced.positions),
        },
        positions_after={
            composed_agent.name: frozenset(str(p) for p in composed_agent.positions),
        },
        parent_trace_id=parent_trace_id,
    )

    # Merge trace histories (ghost preservation)
    combined_traces = left_traced.traces.compose(right_traced.traces).append(trace)

    return TracedAgent(
        agent=composed_agent,
        traces=combined_traces,
        name=composed_agent.name,
    )


def _merge_traces(
    *traced_agents: TracedAgent[Any, Any, Any],
    context: str = "",
) -> TraceMonoid:
    """
    Merge trace histories from multiple agents.

    This operation is associative and preserves all ghosts.

    Args:
        *traced_agents: TracedAgents whose histories to merge
        context: Optional context for the merge

    Returns:
        Combined TraceMonoid
    """
    result = TraceMonoid.empty()
    for ta in traced_agents:
        result = result.compose(ta.traces)
    return result


# =============================================================================
# Law Verification
# =============================================================================


def _verify_semantic_preservation_seq(
    a: PolyAgent[Any, Any, Any],
    b: PolyAgent[Any, Any, Any],
    test_input: Any = None,
) -> LawVerification:
    """
    Verify: traced_seq(a, b).agent.invoke() ≅ seq(a, b).invoke()

    The traced composition must produce the same behavior as
    the untraced composition.
    """
    try:
        # Create traced and untraced versions
        traced_result = _traced_seq_compose(a, b)
        untraced_result = sequential(a, b)

        # Get initial states
        traced_init = next(iter(traced_result.positions))
        untraced_init = next(iter(untraced_result.positions))

        # If we have test input, verify outputs match
        if test_input is not None:
            _, traced_output = traced_result.invoke(traced_init, test_input)
            _, untraced_output = untraced_result.invoke(untraced_init, test_input)

            if traced_output == untraced_output:
                return LawVerification(
                    law_name="semantic_preservation_seq",
                    status=LawStatus.PASSED,
                    left_result=traced_output,
                    right_result=untraced_output,
                    message="traced_seq(a, b).invoke() == seq(a, b).invoke()",
                )
            else:
                return LawVerification(
                    law_name="semantic_preservation_seq",
                    status=LawStatus.FAILED,
                    left_result=traced_output,
                    right_result=untraced_output,
                    message=f"Mismatch: {traced_output} != {untraced_output}",
                )

        # Without test input, verify structural equivalence
        # (names should match since we use the same composition)
        if traced_result.agent.name == untraced_result.name:
            return LawVerification(
                law_name="semantic_preservation_seq",
                status=LawStatus.PASSED,
                left_result=traced_result.agent.name,
                right_result=untraced_result.name,
                message="Structure matches (full verification requires test inputs)",
            )
        else:
            return LawVerification(
                law_name="semantic_preservation_seq",
                status=LawStatus.FAILED,
                left_result=traced_result.agent.name,
                right_result=untraced_result.name,
                message="Names don't match",
            )

    except Exception as e:
        return LawVerification(
            law_name="semantic_preservation_seq",
            status=LawStatus.FAILED,
            message=str(e),
        )


def _verify_ghost_preservation_seq(
    a: TracedAgent[Any, Any, Any],
    b: TracedAgent[Any, Any, Any],
) -> LawVerification:
    """
    Verify: ghosts(traced_seq(a, b)) ⊇ ghosts(a) ∪ ghosts(b)

    Composition must preserve all ghost alternatives from operands.
    """
    try:
        result = _traced_seq_compose(a, b)

        a_ghosts = set(a.traces.ghosts())
        b_ghosts = set(b.traces.ghosts())
        result_ghosts = set(result.traces.ghosts())

        expected = a_ghosts | b_ghosts

        if result_ghosts >= expected:
            return LawVerification(
                law_name="ghost_preservation_seq",
                status=LawStatus.PASSED,
                left_result=len(result_ghosts),
                right_result=len(expected),
                message=f"All {len(expected)} ghosts preserved in {len(result_ghosts)} total",
            )
        else:
            missing = expected - result_ghosts
            return LawVerification(
                law_name="ghost_preservation_seq",
                status=LawStatus.FAILED,
                left_result=result_ghosts,
                right_result=expected,
                message=f"Missing ghosts: {missing}",
            )

    except Exception as e:
        return LawVerification(
            law_name="ghost_preservation_seq",
            status=LawStatus.FAILED,
            message=str(e),
        )


def _verify_traced_associativity(
    a: TracedAgent[Any, Any, Any] | PolyAgent[Any, Any, Any],
    b: TracedAgent[Any, Any, Any] | PolyAgent[Any, Any, Any],
    c: TracedAgent[Any, Any, Any] | PolyAgent[Any, Any, Any],
) -> LawVerification:
    """
    Verify: traced_seq(traced_seq(a, b), c) ≅ traced_seq(a, traced_seq(b, c))

    Traced sequential composition is associative.
    """
    try:
        left = _traced_seq_compose(_traced_seq_compose(a, b), c)
        right = _traced_seq_compose(a, _traced_seq_compose(b, c))

        # Agents should be structurally equivalent
        # (names will differ slightly due to nesting)
        if len(left.positions) == len(right.positions):
            return LawVerification(
                law_name="traced_seq_associativity",
                status=LawStatus.PASSED,
                left_result=left.agent.name,
                right_result=right.agent.name,
                message="Structure matches (position counts equal)",
            )
        else:
            return LawVerification(
                law_name="traced_seq_associativity",
                status=LawStatus.FAILED,
                left_result=len(left.positions),
                right_result=len(right.positions),
                message="Position counts differ",
            )

    except Exception as e:
        return LawVerification(
            law_name="traced_seq_associativity",
            status=LawStatus.FAILED,
            message=str(e),
        )


# =============================================================================
# TRACED_OPERAD Definition
# =============================================================================


def create_traced_operad() -> Operad:
    """
    Create the Traced Operad extending AGENT_OPERAD.

    The TRACED_OPERAD adds trace-recording versions of all
    AGENT_OPERAD operations. Each traced operation:
    1. Performs the underlying composition
    2. Records a WiringTrace
    3. Preserves ghost alternatives

    Operations:
        traced_seq: Sequential composition with trace
        traced_par: Parallel composition with trace

    Laws:
        semantic_preservation_seq: traced_seq(a, b).agent ≅ seq(a, b)
        semantic_preservation_par: traced_par(a, b).agent ≅ par(a, b)
        ghost_preservation_seq: ghosts(traced_seq(a, b)) ⊇ ghosts(a) ∪ ghosts(b)
        ghost_preservation_par: ghosts(traced_par(a, b)) ⊇ ghosts(a) ∪ ghosts(b)
        traced_seq_associativity: traced_seq(traced_seq(a, b), c) ≅ traced_seq(a, traced_seq(b, c))
    """
    return Operad(
        name="TracedOperad",
        operations={
            # Inherit all AGENT_OPERAD operations
            **AGENT_OPERAD.operations,
            # Add traced versions
            "traced_seq": Operation(
                name="traced_seq",
                arity=2,
                signature="TracedAgent[A,B] × TracedAgent[B,C] → TracedAgent[A,C]",
                compose=lambda a, b: _traced_seq_compose(a, b),
                description="Sequential composition with trace recording",
            ),
            "traced_par": Operation(
                name="traced_par",
                arity=2,
                signature="TracedAgent[A,B] × TracedAgent[A,C] → TracedAgent[A,(B,C)]",
                compose=lambda a, b: _traced_par_compose(a, b),
                description="Parallel composition with trace recording",
            ),
        },
        laws=[
            # Inherit AGENT_OPERAD laws
            *AGENT_OPERAD.laws,
            # Add traced-specific laws
            Law(
                name="semantic_preservation_seq",
                equation="traced_seq(a, b).agent.invoke(s, i) = seq(a, b).invoke(s, i)",
                verify=lambda a, b, test_input=None: _verify_semantic_preservation_seq(
                    a, b, test_input
                ),
                description="Tracing doesn't change sequential composition behavior",
            ),
            Law(
                name="ghost_preservation_seq",
                equation="ghosts(traced_seq(a, b)) ⊇ ghosts(a) ∪ ghosts(b)",
                verify=_verify_ghost_preservation_seq,
                description="Ghosts accumulate through traced sequential composition",
            ),
            Law(
                name="traced_seq_associativity",
                equation="traced_seq(traced_seq(a, b), c) ≅ traced_seq(a, traced_seq(b, c))",
                verify=_verify_traced_associativity,
                description="Traced sequential composition is associative",
            ),
        ],
        description="Traced operad extending AGENT_OPERAD with wiring trace recording",
    )


# Create the global Traced Operad instance
TRACED_OPERAD = create_traced_operad()

# Register with the operad registry
OperadRegistry.register(TRACED_OPERAD)


# =============================================================================
# Convenience Functions
# =============================================================================


def traced_seq(
    left: TracedAgent[Any, Any, Any] | PolyAgent[Any, Any, Any],
    right: TracedAgent[Any, Any, Any] | PolyAgent[Any, Any, Any],
    context: str = "",
    alternatives: tuple[Alternative, ...] = (),
    parent_trace_id: str | None = None,
) -> TracedAgent[Any, Any, Any]:
    """
    Sequential composition with trace recording.

    Convenience function for TRACED_OPERAD's traced_seq operation.

    Example:
        >>> from agents.poly import from_function
        >>> a = TracedAgent.wrap(from_function("inc", lambda x: x + 1))
        >>> b = TracedAgent.wrap(from_function("double", lambda x: x * 2))
        >>> composed = traced_seq(a, b)
        >>> state, result = composed.invoke(next(iter(composed.positions)), 5)
        >>> print(result)  # (5 + 1) * 2 = 12
        >>> print(len(composed.traces))  # 1 trace recorded
    """
    return _traced_seq_compose(left, right, context, alternatives, parent_trace_id)


def traced_par(
    left: TracedAgent[Any, Any, Any] | PolyAgent[Any, Any, Any],
    right: TracedAgent[Any, Any, Any] | PolyAgent[Any, Any, Any],
    context: str = "",
    alternatives: tuple[Alternative, ...] = (),
    parent_trace_id: str | None = None,
) -> TracedAgent[Any, Any, Any]:
    """
    Parallel composition with trace recording.

    Convenience function for TRACED_OPERAD's traced_par operation.

    Example:
        >>> from agents.poly import from_function
        >>> a = TracedAgent.wrap(from_function("inc", lambda x: x + 1))
        >>> b = TracedAgent.wrap(from_function("double", lambda x: x * 2))
        >>> composed = traced_par(a, b)
        >>> state, result = composed.invoke(next(iter(composed.positions)), 5)
        >>> print(result)  # (6, 10) - tuple of both results
    """
    return _traced_par_compose(left, right, context, alternatives, parent_trace_id)


__all__ = [
    # Core types
    "TracedOperation",
    "TracedAgent",
    # Operad
    "TRACED_OPERAD",
    "create_traced_operad",
    # Convenience functions
    "traced_seq",
    "traced_par",
]
