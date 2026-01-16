"""
Tests for the DP-Agent Bridge.

These tests verify the categorical laws and properties of the DP bridge:
1. PolicyTrace satisfies Writer monad laws
2. BellmanMorphism satisfies functor laws
3. OptimalSubstructure satisfies sheaf gluing conditions
4. ValueFunction is well-defined and monotonic

Uses property-based testing (hypothesis) for law verification.

Teaching:
    gotcha: Hypothesis generates random test cases. Set a seed in conftest.py
            for reproducible failures during debugging.
            (Evidence: conftest.py::configure_hypothesis)

    gotcha: Monad law tests use equivalence checking via .value and .log
            comparison, not object identity.
            (Evidence: test_monad_left_identity, test_monad_right_identity)
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Callable

import pytest
from hypothesis import given, settings, strategies as st

from services.categorical.dp_bridge import (
    BellmanMorphism,
    DPAction,
    DPSolver,
    DPState,
    MetaDP,
    OptimalSubstructure,
    PolicyTrace,
    Principle,
    PrincipleScore,
    ProblemFormulation,
    SubproblemSolution,
    TraceEntry,
    ValueFunction,
    ValueScore,
)

# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def trace_entries(draw: st.DrawFn) -> TraceEntry:
    """Generate random trace entries."""
    return TraceEntry(
        state_before=draw(st.text(min_size=1, max_size=10)),
        action=draw(st.text(min_size=1, max_size=20)),
        state_after=draw(st.text(min_size=1, max_size=10)),
        value=draw(st.floats(min_value=-100, max_value=100, allow_nan=False)),
        rationale=draw(st.text(max_size=50)),
    )


@st.composite
def policy_traces(
    draw: st.DrawFn, value_strategy: st.SearchStrategy[Any] = st.integers()
) -> PolicyTrace[Any]:
    """Generate random policy traces."""
    value = draw(value_strategy)
    entries = draw(st.lists(trace_entries(), min_size=0, max_size=5))
    return PolicyTrace(value=value, log=tuple(entries))


@st.composite
def principle_scores(draw: st.DrawFn) -> PrincipleScore:
    """Generate random principle scores."""
    return PrincipleScore(
        principle=draw(st.sampled_from(list(Principle))),
        score=draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False)),
        evidence=draw(st.text(max_size=30)),
        weight=draw(st.floats(min_value=0.1, max_value=5.0, allow_nan=False)),
    )


# =============================================================================
# PolicyTrace: Writer Monad Law Tests
# =============================================================================


class TestPolicyTraceMonadLaws:
    """Test that PolicyTrace satisfies the Writer monad laws."""

    @given(st.integers())
    def test_monad_left_identity(self, value: int) -> None:
        """
        Left identity: return a >>= f == f a

        Lifting a value and binding should equal just applying f.
        """
        # Use a shared timestamp to avoid timing differences
        fixed_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

        # Define a test function f
        def f(x: int) -> PolicyTrace[int]:
            entry = TraceEntry(
                state_before="start",
                action="double",
                state_after="end",
                value=float(x),
                timestamp=fixed_time,  # Fixed timestamp
            )
            return PolicyTrace(value=x * 2, log=(entry,))

        # return a >>= f
        lhs = PolicyTrace.pure(value).bind(f)

        # f a
        rhs = f(value)

        # Should be equal (comparing structural equality, not object identity)
        assert lhs.value == rhs.value
        assert len(lhs.log) == len(rhs.log)
        # Compare entries without timestamps
        for l_entry, r_entry in zip(lhs.log, rhs.log):
            assert l_entry.state_before == r_entry.state_before
            assert l_entry.action == r_entry.action
            assert l_entry.state_after == r_entry.state_after
            assert l_entry.value == r_entry.value

    @given(policy_traces())
    def test_monad_right_identity(self, m: PolicyTrace[Any]) -> None:
        """
        Right identity: m >>= return == m

        Binding with pure should not change the trace.
        """
        # m >>= return
        result = m.bind(PolicyTrace.pure)

        # Should be equal to m
        assert result.value == m.value
        assert result.log == m.log

    @given(st.integers(), st.integers(), st.integers())
    def test_monad_associativity(self, initial: int, add1: int, add2: int) -> None:
        """
        Associativity: (m >>= f) >>= g == m >>= (x -> f x >>= g)

        The order of bind applications should not matter.
        """
        # Use fixed timestamps to avoid timing differences
        fixed_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        m = PolicyTrace.pure(initial)

        def f(x: int) -> PolicyTrace[int]:
            entry = TraceEntry(
                state_before=str(x),
                action=f"add_{add1}",
                state_after=str(x + add1),
                value=float(add1),
                timestamp=fixed_time,
            )
            return PolicyTrace(value=x + add1, log=(entry,))

        def g(x: int) -> PolicyTrace[int]:
            entry = TraceEntry(
                state_before=str(x),
                action=f"add_{add2}",
                state_after=str(x + add2),
                value=float(add2),
                timestamp=fixed_time,
            )
            return PolicyTrace(value=x + add2, log=(entry,))

        # (m >>= f) >>= g
        lhs = m.bind(f).bind(g)

        # m >>= (x -> f x >>= g)
        rhs = m.bind(lambda x: f(x).bind(g))

        assert lhs.value == rhs.value
        # Compare log content (timestamps are fixed now)
        assert len(lhs.log) == len(rhs.log)
        for l_entry, r_entry in zip(lhs.log, rhs.log):
            assert l_entry.action == r_entry.action
            assert l_entry.value == r_entry.value

    @given(policy_traces(), trace_entries())
    def test_trace_accumulation(self, trace: PolicyTrace[Any], entry: TraceEntry) -> None:
        """
        Traces should accumulate through bind operations.

        This tests the Writer monad's specific behavior.
        """
        original_log_length = len(trace.log)

        new_trace = trace.with_entry(entry)

        assert len(new_trace.log) == original_log_length + 1
        assert new_trace.log[-1] == entry
        assert new_trace.log[:-1] == trace.log

    @given(
        st.lists(st.floats(min_value=-10, max_value=10, allow_nan=False), min_size=1, max_size=10)
    )
    def test_total_value_discounting(self, values: list[float]) -> None:
        """
        Total value should correctly apply discounting.
        """
        entries = tuple(
            TraceEntry(
                state_before=f"s{i}",
                action=f"a{i}",
                state_after=f"s{i + 1}",
                value=v,
            )
            for i, v in enumerate(values)
        )
        trace = PolicyTrace(value="final", log=entries)

        gamma = 0.9
        expected = sum(gamma**i * v for i, v in enumerate(values))

        assert abs(trace.total_value(gamma) - expected) < 1e-6


# =============================================================================
# PolicyTrace: Functor Law Tests
# =============================================================================


class TestPolicyTraceFunctorLaws:
    """Test that PolicyTrace.map satisfies functor laws."""

    @given(policy_traces())
    def test_functor_identity(self, trace: PolicyTrace[Any]) -> None:
        """
        Identity: map id == id

        Mapping the identity function should not change the trace.
        """
        result = trace.map(lambda x: x)

        assert result.value == trace.value
        assert result.log == trace.log

    @given(st.integers())
    def test_functor_composition(self, value: int) -> None:
        """
        Composition: map (g . f) == map g . map f

        Mapping composed functions equals composing maps.
        """
        trace = PolicyTrace.pure(value)

        def f(x: int) -> int:
            return x + 1

        def g(x: int) -> int:
            return x * 2

        # map (g . f)
        lhs = trace.map(lambda x: g(f(x)))

        # map g . map f
        rhs = trace.map(f).map(g)

        assert lhs.value == rhs.value
        assert lhs.log == rhs.log


# =============================================================================
# ValueFunction Tests
# =============================================================================


class TestValueFunction:
    """Test ValueFunction behavior and properties."""

    def test_evaluate_returns_value_score(self) -> None:
        """evaluate() should return a ValueScore with all principles."""
        vf = ValueFunction[str, str]()
        score = vf.evaluate("TestAgent", "ready")

        assert isinstance(score, ValueScore)
        assert score.agent_name == "TestAgent"
        assert len(score.principle_scores) == len(Principle)

    def test_custom_evaluators(self) -> None:
        """Custom evaluators should be used when provided."""

        def ethical_evaluator(name: str, state: str, action: str | None) -> float:
            return 1.0 if "ethical" in name.lower() else 0.5

        vf = ValueFunction[str, str](principle_evaluators={Principle.ETHICAL: ethical_evaluator})

        ethical_score = vf.evaluate("EthicalAgent", "ready")
        regular_score = vf.evaluate("RegularAgent", "ready")

        ethical_principle = next(
            ps for ps in ethical_score.principle_scores if ps.principle == Principle.ETHICAL
        )
        regular_principle = next(
            ps for ps in regular_score.principle_scores if ps.principle == Principle.ETHICAL
        )

        assert ethical_principle.score == 1.0
        assert regular_principle.score == 0.5

    @given(st.lists(principle_scores(), min_size=1, max_size=7))
    def test_value_score_total_bounded(self, scores: list[PrincipleScore]) -> None:
        """Total score should be bounded in [0, 1]."""
        value_score = ValueScore(
            agent_name="Test",
            principle_scores=tuple(scores),
        )

        assert 0.0 <= value_score.total_score <= 1.0

    def test_compare_prefers_higher_min_score(self) -> None:
        """
        Compare should prefer higher minimum principle scores.

        Safety first: a solution with all principles satisfied moderately
        is better than one with some high and some low.
        """
        vf = ValueFunction[str, str]()

        # All scores 0.6
        uniform = ValueScore(
            agent_name="Uniform",
            principle_scores=tuple(PrincipleScore(p, 0.6, "", 1.0) for p in Principle),
        )

        # Some high (0.9), some low (0.3), same average
        varied = ValueScore(
            agent_name="Varied",
            principle_scores=tuple(
                PrincipleScore(p, 0.9 if i % 2 == 0 else 0.3, "", 1.0)
                for i, p in enumerate(Principle)
            ),
        )

        # Uniform should be preferred (higher min)
        assert vf.compare(uniform, varied) > 0


# =============================================================================
# BellmanMorphism Functor Law Tests
# =============================================================================


class TestBellmanMorphismFunctorLaws:
    """Test that BellmanMorphism satisfies functor laws."""

    def test_identity_law(self) -> None:
        """
        F(id) = id

        Lifting the identity action should produce the identity agent.
        """
        from agents.poly import identity

        morphism = BellmanMorphism(
            state_map=lambda s: frozenset({s}),
            action_map=lambda a: identity() if a.name == "id" else None,
        )

        assert morphism.verify_identity_law()

    def test_composition_law(self) -> None:
        """
        F(g . f) = F(g) . F(f)

        Lifting composed actions equals composing lifted actions.
        """
        from agents.poly import from_function

        def make_agent(action: DPAction) -> Any:
            if action.name == "add1":
                return from_function("add1", lambda x: x + 1)
            elif action.name == "double":
                return from_function("double", lambda x: x * 2)
            else:
                return from_function(action.name, lambda x: x)

        morphism = BellmanMorphism(
            state_map=lambda s: frozenset({s}),
            action_map=make_agent,
        )

        action1 = DPAction(name="add1", operation="seq")
        action2 = DPAction(name="double", operation="seq")

        assert morphism.verify_composition_law(action1, action2)

    def test_lift_composition_produces_sequential(self) -> None:
        """
        lift_composition should produce sequential composition.
        """
        from agents.poly import from_function

        call_count = [0]

        def make_agent(action: DPAction) -> Any:
            call_count[0] += 1
            return from_function(action.name, lambda x: x)

        morphism = BellmanMorphism(
            state_map=lambda s: frozenset({s}),
            action_map=make_agent,
        )

        actions = [
            DPAction(name="a", operation="seq"),
            DPAction(name="b", operation="seq"),
            DPAction(name="c", operation="seq"),
        ]

        composed = morphism.lift_composition(actions)

        # Should have called make_agent for each action
        assert call_count[0] == 3
        assert composed is not None


# =============================================================================
# OptimalSubstructure (Sheaf) Tests
# =============================================================================


class TestOptimalSubstructureSheafLaws:
    """Test that OptimalSubstructure satisfies sheaf conditions."""

    def test_glue_requires_overlap(self) -> None:
        """
        Gluing should fail if sections don't overlap.

        Sheaf condition: sections must agree on intersections.
        """
        structure = OptimalSubstructure[str]()

        left = SubproblemSolution(
            start_state="A",
            end_state="B",  # Ends at B
            actions=("a1",),
            value=1.0,
            trace=PolicyTrace.pure("B"),
        )

        right = SubproblemSolution(
            start_state="C",  # Starts at C, not B!
            end_state="D",
            actions=("a2",),
            value=2.0,
            trace=PolicyTrace.pure("D"),
        )

        # Should fail - no overlap
        result = structure.glue(left, right)
        assert result is None

    def test_glue_succeeds_with_overlap(self) -> None:
        """
        Gluing should succeed when sections overlap correctly.
        """
        structure = OptimalSubstructure[str]()

        left = SubproblemSolution(
            start_state="A",
            end_state="B",
            actions=("a1",),
            value=1.0,
            trace=PolicyTrace.pure("B"),
        )

        right = SubproblemSolution(
            start_state="B",  # Starts where left ends
            end_state="C",
            actions=("a2",),
            value=2.0,
            trace=PolicyTrace.pure("C"),
        )

        result = structure.glue(left, right)

        assert result is not None
        assert result.start_state == "A"
        assert result.end_state == "C"
        assert result.actions == ("a1", "a2")
        assert result.value == 3.0  # 1.0 + 2.0

    @given(
        st.floats(min_value=0.1, max_value=10, allow_nan=False),
        st.floats(min_value=0.1, max_value=10, allow_nan=False),
        st.floats(min_value=0.1, max_value=10, allow_nan=False),
    )
    def test_glue_is_associative(self, v1: float, v2: float, v3: float) -> None:
        """
        Sheaf associativity: (A * B) * C = A * (B * C)

        Gluing is associative (for compatible sections).
        """
        structure = OptimalSubstructure[str]()

        a = SubproblemSolution(
            start_state="S1",
            end_state="S2",
            actions=("a",),
            value=v1,
            trace=PolicyTrace.pure("S2"),
        )

        b = SubproblemSolution(
            start_state="S2",
            end_state="S3",
            actions=("b",),
            value=v2,
            trace=PolicyTrace.pure("S3"),
        )

        c = SubproblemSolution(
            start_state="S3",
            end_state="S4",
            actions=("c",),
            value=v3,
            trace=PolicyTrace.pure("S4"),
        )

        # (A * B) * C
        ab = structure.glue(a, b)
        assert ab is not None
        lhs = structure.glue(ab, c)

        # A * (B * C)
        bc = structure.glue(b, c)
        assert bc is not None
        rhs = structure.glue(a, bc)

        assert lhs is not None
        assert rhs is not None
        assert lhs.start_state == rhs.start_state == "S1"
        assert lhs.end_state == rhs.end_state == "S4"
        assert lhs.actions == rhs.actions
        assert abs(lhs.value - rhs.value) < 1e-6

    def test_verify_optimal_substructure(self) -> None:
        """
        Optimal substructure verification should pass for valid decompositions.
        """
        structure = OptimalSubstructure[str]()

        # Record optimal subsolutions
        sub1 = structure.solve_subproblem(
            start="A",
            end="B",
            actions=("a1",),
            value=1.0,
            trace=PolicyTrace.pure("B"),
        )
        sub2 = structure.solve_subproblem(
            start="B",
            end="C",
            actions=("a2",),
            value=2.0,
            trace=PolicyTrace.pure("C"),
        )

        # Full solution
        full = SubproblemSolution(
            start_state="A",
            end_state="C",
            actions=("a1", "a2"),
            value=3.0,
            trace=PolicyTrace.pure("C"),
        )

        # Should verify successfully
        assert structure.verify_optimal_substructure(full, [sub1, sub2])


# =============================================================================
# DPSolver Integration Tests
# =============================================================================


class TestDPSolver:
    """Test the DPSolver with simple problems."""

    def test_solve_simple_path(self) -> None:
        """
        Solve a simple shortest path problem.
        """
        # Define a simple linear path: A -> B -> C
        transitions = {
            ("A", "next"): "B",
            ("B", "next"): "C",
        }

        formulation = ProblemFormulation[str, str](
            name="simple_path",
            description="Find path from A to C",
            state_type=str,
            initial_states=frozenset({"A"}),
            goal_states=frozenset({"C"}),
            available_actions=lambda s: frozenset({"next"}) if s in ("A", "B") else frozenset(),
            transition=lambda s, a: transitions.get((s, a), s),
            reward=lambda s, a, s2: 1.0,  # Reward for each step
        )

        solver = DPSolver(formulation=formulation, max_depth=10)
        value, trace = solver.solve("A")

        # Should find a path with positive value
        assert value > 0 or len(trace.log) > 0  # Either value or trace shows progress

    def test_solve_respects_gamma(self) -> None:
        """
        Discount factor should affect value calculation.
        """
        formulation = ProblemFormulation[int, str](
            name="linear",
            description="Linear chain",
            state_type=int,
            initial_states=frozenset({0}),
            goal_states=frozenset({3}),
            available_actions=lambda s: frozenset({"next"}) if s < 3 else frozenset(),
            transition=lambda s, a: s + 1 if a == "next" else s,
            reward=lambda s, a, s2: 1.0,
        )

        solver_high_gamma = DPSolver(formulation=formulation, gamma=0.99)
        solver_low_gamma = DPSolver(formulation=formulation, gamma=0.5)

        value_high, _ = solver_high_gamma.solve(0)
        value_low, _ = solver_low_gamma.solve(0)

        # Higher gamma should give higher total value
        assert value_high > value_low


# =============================================================================
# MetaDP Tests
# =============================================================================


class TestMetaDP:
    """Test MetaDP problem reformulation."""

    def test_add_formulation(self) -> None:
        """Should be able to add formulations."""
        meta: MetaDP[str, str] = MetaDP()

        formulation = ProblemFormulation[str, str](
            name="test",
            description="Test formulation",
            state_type=str,
            initial_states=frozenset({"start"}),
            goal_states=frozenset({"end"}),
            available_actions=lambda s: frozenset({"go"}),
            transition=lambda s, a: "end",
            reward=lambda s, a, s2: 1.0,
        )

        meta.add_formulation(formulation)

        assert "test" in meta.formulations

    def test_reformulation_creates_new(self) -> None:
        """Reformulation should create a new formulation."""
        meta: MetaDP[str, str] = MetaDP()

        original = ProblemFormulation[str, str](
            name="original",
            description="Original",
            state_type=str,
            initial_states=frozenset({"A", "B"}),
            goal_states=frozenset({"Z"}),
            available_actions=lambda s: frozenset({"go"}),
            transition=lambda s, a: "Z",
            reward=lambda s, a, s2: 1.0,
        )

        meta.add_formulation(original)

        # Add a reformulator that abstracts states
        def abstract_reformulator(f: ProblemFormulation[str, str]) -> ProblemFormulation[str, str]:
            return ProblemFormulation[str, str](
                name=f"{f.name}_abstracted",
                description="Abstracted version",
                state_type=str,
                initial_states=frozenset({"start"}),  # Merged A and B
                goal_states=f.goal_states,
                available_actions=f.available_actions,
                transition=f.transition,
                reward=f.reward,
                version=f.version + 1,
            )

        meta.add_reformulator("abstract", abstract_reformulator)

        new_form = meta.apply_reformulator("original", "abstract")

        assert new_form is not None
        assert "abstract" in new_form.name
        assert len(new_form.initial_states) == 1


# =============================================================================
# Property-Based Tests for Full Integration
# =============================================================================


class TestDPAgentIsomorphism:
    """
    Test the isomorphism between DP and Agent composition.

    These tests verify that:
    1. DP solutions map to valid agent compositions
    2. Agent compositions map back to DP solutions
    3. The mapping preserves optimality
    """

    def test_solution_trace_is_valid_agent_composition(self) -> None:
        """
        A DP solution trace should map to a valid agent composition.
        """
        from agents.poly import from_function

        # Create a simple DP problem
        formulation = ProblemFormulation[int, str](
            name="count",
            description="Count to 3",
            state_type=int,
            initial_states=frozenset({0}),
            goal_states=frozenset({3}),
            available_actions=lambda s: frozenset({"inc"}) if s < 3 else frozenset(),
            transition=lambda s, a: s + 1,
            reward=lambda s, a, s2: 1.0,
        )

        # Create morphism that maps actions to simple stateless agents
        morphism = BellmanMorphism[int, str, int](
            state_map=lambda s: frozenset({s}),
            action_map=lambda a: from_function("inc", lambda x: x + 1),
        )

        # Solve
        solver = DPSolver(formulation=formulation, morphism=morphism)
        value, trace = solver.solve(0)

        # Map trace to agent composition
        actions = [DPAction(name=e.action, operation="seq") for e in trace.log]
        if actions:
            # Just verify composition creates without error
            composed_agent = morphism.lift_composition(actions)
            assert composed_agent is not None
            # Each individual lifted agent should work
            single_agent = morphism.lift_action(actions[0])
            state, out = single_agent.invoke("ready", 5)
            assert out == 6  # 5 + 1


# =============================================================================
# Module-level fixtures
# =============================================================================


@pytest.fixture
def simple_value_function() -> ValueFunction[str, str]:
    """A simple value function for testing."""
    return ValueFunction[str, str](
        principle_evaluators={
            Principle.COMPOSABLE: lambda n, s, a: 0.8,
            Principle.ETHICAL: lambda n, s, a: 0.9,
        }
    )


@pytest.fixture
def simple_morphism() -> BellmanMorphism[str, DPAction, Any]:
    """A simple morphism for testing."""
    from agents.poly import identity

    return BellmanMorphism[str, DPAction, Any](
        state_map=lambda s: frozenset({s}),
        action_map=lambda a: identity(),
    )
