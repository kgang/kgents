"""
Tests for Operad Core.

These tests verify:
1. Operation structure and invocation
2. Operad composition
3. Law verification
4. Universal operad (AGENT_OPERAD)
5. Operad registry
"""

import pytest

from agents.operad import (
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import ID, from_function, identity


class TestOperation:
    """Tests for Operation dataclass."""

    def test_operation_construction(self) -> None:
        """Operation has name, arity, signature, compose."""
        op = Operation(
            name="test",
            arity=2,
            signature="A × B → C",
            compose=lambda a, b: a,
        )
        assert op.name == "test"
        assert op.arity == 2

    def test_operation_callable(self) -> None:
        """Operation is callable with correct arity."""
        double = from_function("Double", lambda x: x * 2)
        add_one = from_function("AddOne", lambda x: x + 1)

        from agents.poly import sequential

        op = Operation(
            name="seq",
            arity=2,
            signature="Agent × Agent → Agent",
            compose=sequential,
        )

        composed = op(double, add_one)
        assert composed is not None
        assert ">>" in composed.name

    def test_operation_wrong_arity_raises(self) -> None:
        """Operation with wrong arity raises ValueError."""
        op = Operation(
            name="binary",
            arity=2,
            signature="A × B → C",
            compose=lambda a, b: a,
        )

        with pytest.raises(ValueError, match="requires 2"):
            op(identity())  # Only 1 agent, need 2


class TestOperad:
    """Tests for Operad dataclass."""

    def test_operad_construction(self) -> None:
        """Operad has name, operations, laws."""
        operad = Operad(
            name="TestOperad",
            operations={
                "id": Operation("id", 0, "→ Agent", lambda: identity()),
            },
            laws=[],
        )
        assert operad.name == "TestOperad"
        assert "id" in operad.operations

    def test_operad_compose(self) -> None:
        """Operad.compose applies operation to agents."""
        double = from_function("Double", lambda x: x * 2)
        add_one = from_function("AddOne", lambda x: x + 1)

        composed = AGENT_OPERAD.compose("seq", double, add_one)

        # Verify composition works
        _, result = composed.invoke(("ready", "ready"), 5)
        assert result == 11  # (5 * 2) + 1 = 11

    def test_operad_compose_unknown_op_raises(self) -> None:
        """Operad.compose with unknown operation raises KeyError."""
        with pytest.raises(KeyError, match="Unknown operation"):
            AGENT_OPERAD.compose("nonexistent", identity())

    def test_operad_repr(self) -> None:
        """Operad has informative repr."""
        repr_str = repr(AGENT_OPERAD)
        assert "AgentOperad" in repr_str
        assert "seq" in repr_str


class TestAgentOperad:
    """Tests for the Universal Agent Operad."""

    def test_agent_operad_has_five_operations(self) -> None:
        """AGENT_OPERAD has seq, par, branch, fix, trace."""
        ops = AGENT_OPERAD.operations
        assert "seq" in ops
        assert "par" in ops
        assert "branch" in ops
        assert "fix" in ops
        assert "trace" in ops
        assert len(ops) == 5

    def test_seq_operation(self) -> None:
        """seq operation composes sequentially."""
        double = from_function("Double", lambda x: x * 2)
        add_one = from_function("AddOne", lambda x: x + 1)

        composed = AGENT_OPERAD.compose("seq", double, add_one)

        _, result = composed.invoke(("ready", "ready"), 5)
        assert result == 11  # 5 * 2 + 1

    def test_par_operation(self) -> None:
        """par operation composes in parallel."""
        double = from_function("Double", lambda x: x * 2)
        square = from_function("Square", lambda x: x ** 2)

        composed = AGENT_OPERAD.compose("par", double, square)

        _, result = composed.invoke(("ready", "ready"), 5)
        assert result == (10, 25)  # (5*2, 5**2)

    def test_trace_operation(self) -> None:
        """trace operation wraps agent with observation."""
        double = from_function("Double", lambda x: x * 2)

        traced = AGENT_OPERAD.compose("trace", double)

        assert "trace" in traced.name
        _, result = traced.invoke("ready", 5)
        assert result == 10

    def test_agent_operad_has_laws(self) -> None:
        """AGENT_OPERAD has associativity laws."""
        laws = AGENT_OPERAD.laws
        assert len(laws) >= 2
        law_names = [law.name for law in laws]
        assert "seq_associativity" in law_names
        assert "par_associativity" in law_names


class TestLawVerification:
    """Tests for law verification."""

    def test_verify_law_by_name(self) -> None:
        """Can verify a specific law by name."""
        a = from_function("A", lambda x: x + 1)
        b = from_function("B", lambda x: x * 2)
        c = from_function("C", lambda x: x - 1)

        result = AGENT_OPERAD.verify_law("seq_associativity", a, b, c)

        assert isinstance(result, LawVerification)
        # Law verification is structural, should pass
        assert result.passed or result.status == LawStatus.PASSED

    def test_verify_unknown_law(self) -> None:
        """Unknown law returns SKIPPED status."""
        result = AGENT_OPERAD.verify_law("nonexistent_law")

        assert result.status == LawStatus.SKIPPED
        assert not result.passed

    def test_verify_all_laws(self) -> None:
        """Can verify all laws at once."""
        a = from_function("A", lambda x: x + 1)
        b = from_function("B", lambda x: x * 2)
        c = from_function("C", lambda x: x - 1)

        results = AGENT_OPERAD.verify_all_laws(a, b, c)

        assert len(results) == len(AGENT_OPERAD.laws)


class TestOperadEnumeration:
    """Tests for operad enumeration (generative power)."""

    def test_enumerate_depth_zero(self) -> None:
        """Depth 0 enumeration returns primitives only."""
        from agents.poly import ID, GROUND, all_primitives

        primitives = [ID, GROUND]
        compositions = AGENT_OPERAD.enumerate(primitives, depth=0)

        assert len(compositions) == len(primitives)

    def test_enumerate_depth_one(self) -> None:
        """Depth 1 enumeration includes basic compositions."""
        id_agent = identity()
        double = from_function("Double", lambda x: x * 2)

        primitives = [id_agent, double]
        compositions = AGENT_OPERAD.enumerate(primitives, depth=1)

        # Should have more than just primitives
        assert len(compositions) > len(primitives)

    def test_enumerate_with_filter(self) -> None:
        """Enumeration respects filter function."""
        id_agent = identity()
        double = from_function("Double", lambda x: x * 2)

        # Filter: only agents with "Double" in name
        def has_double(agent) -> bool:
            return "Double" in agent.name

        compositions = AGENT_OPERAD.enumerate(
            [id_agent, double],
            depth=1,
            filter_fn=has_double,
        )

        # Should only include compositions with "Double"
        for comp in compositions:
            if comp != id_agent:  # id_agent is from primitives
                assert "Double" in comp.name or comp == double


class TestOperadRegistry:
    """Tests for operad registry."""

    def test_agent_operad_registered(self) -> None:
        """AGENT_OPERAD is registered."""
        operad = OperadRegistry.get("AgentOperad")
        assert operad is AGENT_OPERAD

    def test_register_and_get(self) -> None:
        """Can register and retrieve operads."""
        custom = Operad(name="CustomOperad", operations={}, laws=[])
        OperadRegistry.register(custom)

        retrieved = OperadRegistry.get("CustomOperad")
        assert retrieved is custom

    def test_all_operads(self) -> None:
        """Can list all registered operads."""
        all_ops = OperadRegistry.all_operads()
        assert "AgentOperad" in all_ops
        assert isinstance(all_ops["AgentOperad"], Operad)


class TestCompositionLaws:
    """Tests for categorical laws."""

    def test_seq_associativity_behavioral(self) -> None:
        """seq(seq(a,b),c) = seq(a,seq(b,c)) behaviorally."""
        f = from_function("F", lambda x: x + 1)
        g = from_function("G", lambda x: x * 2)
        h = from_function("H", lambda x: x - 1)

        # (f >> g) >> h
        left = AGENT_OPERAD.compose(
            "seq", AGENT_OPERAD.compose("seq", f, g), h
        )

        # f >> (g >> h)
        right = AGENT_OPERAD.compose(
            "seq", f, AGENT_OPERAD.compose("seq", g, h)
        )

        # Both should produce same result
        # Left state: ((ready, ready), ready)
        _, result_left = left.invoke((("ready", "ready"), "ready"), 5)
        # Right state: (ready, (ready, ready))
        _, result_right = right.invoke(("ready", ("ready", "ready")), 5)

        # ((5 + 1) * 2) - 1 = 11
        assert result_left == result_right == 11

    def test_par_associativity_behavioral(self) -> None:
        """par(par(a,b),c) = par(a,par(b,c)) structurally."""
        f = from_function("F", lambda x: x + 1)
        g = from_function("G", lambda x: x * 2)
        h = from_function("H", lambda x: x - 1)

        # (f || g) || h
        left = AGENT_OPERAD.compose(
            "par", AGENT_OPERAD.compose("par", f, g), h
        )

        # f || (g || h)
        right = AGENT_OPERAD.compose(
            "par", f, AGENT_OPERAD.compose("par", g, h)
        )

        # Execute both
        _, result_left = left.invoke((("ready", "ready"), "ready"), 5)
        _, result_right = right.invoke(("ready", ("ready", "ready")), 5)

        # Results should be nested tuples with same values
        # Left: ((6, 10), 4)
        # Right: (6, (10, 4))
        assert result_left == ((6, 10), 4)
        assert result_right == (6, (10, 4))

    def test_identity_law_seq(self) -> None:
        """seq(id, f) = f = seq(f, id) behaviorally."""
        id_agent = identity()
        f = from_function("F", lambda x: x + 1)

        # id >> f
        left = AGENT_OPERAD.compose("seq", id_agent, f)
        _, result_left = left.invoke(("ready", "ready"), 5)

        # f alone
        _, result_f = f.invoke("ready", 5)

        # f >> id
        right = AGENT_OPERAD.compose("seq", f, id_agent)
        _, result_right = right.invoke(("ready", "ready"), 5)

        assert result_left == result_f == result_right == 6
