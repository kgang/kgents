"""
Tests for Polynomial Agent Protocol.

These tests verify:
1. PolyAgent construction and invocation
2. State-dependent behavior
3. Composition operations (sequential, parallel)
4. Wiring diagram semantics
"""

from typing import Any

import pytest

from agents.poly import (
    PolyAgent,
    WiringDiagram,
    constant,
    from_function,
    identity,
    parallel,
    sequential,
    stateful,
)


class TestPolyAgentConstruction:
    """Tests for PolyAgent construction."""

    def test_identity_construction(self) -> None:
        """Identity agent has single state and passes through."""
        id_agent = identity()
        assert id_agent.name == "Id"
        assert len(id_agent.positions) == 1
        assert "ready" in id_agent.positions

    def test_constant_construction(self) -> None:
        """Constant agent always outputs same value."""
        const = constant(42, name="FortyTwo")
        assert const.name == "FortyTwo"

        state, output = const.invoke("ready", "anything")
        assert output == 42

    def test_from_function_construction(self) -> None:
        """Function agent lifts pure function."""
        double: PolyAgent[str, int, int] = from_function("Double", lambda x: x * 2)
        assert double.name == "Double"

        state, output = double.invoke("ready", 21)
        assert output == 42

    def test_stateful_construction(self) -> None:
        """Stateful agent maintains state across invocations."""
        states = frozenset({"on", "off"})

        def toggle(s: str, _: Any) -> tuple[str, str]:
            return ("off" if s == "on" else "on", s)

        toggle_agent = stateful("Toggle", states, "off", toggle)

        state, output = toggle_agent.invoke("off", None)
        assert state == "on"
        assert output == "off"

        state, output = toggle_agent.invoke("on", None)
        assert state == "off"
        assert output == "on"


class TestPolyAgentInvocation:
    """Tests for PolyAgent invocation."""

    def test_invoke_valid_state(self) -> None:
        """Invoke with valid state succeeds."""
        id_agent = identity()
        state, output = id_agent.invoke("ready", "hello")
        assert state == "ready"
        assert output == "hello"

    def test_invoke_invalid_state_raises(self) -> None:
        """Invoke with invalid state raises ValueError."""
        id_agent = identity()
        with pytest.raises(ValueError, match="Invalid state"):
            id_agent.invoke("invalid", "hello")

    def test_run_sequence(self) -> None:
        """Run processes sequence of inputs."""
        double: PolyAgent[str, int, int] = from_function("Double", lambda x: x * 2)
        final_state, outputs = double.run("ready", [1, 2, 3])

        assert final_state == "ready"
        assert outputs == [2, 4, 6]


class TestSequentialComposition:
    """Tests for sequential composition."""

    def test_sequential_composition(self) -> None:
        """Sequential composition threads output to input."""
        double: PolyAgent[str, int, int] = from_function("Double", lambda x: x * 2)
        add_one: PolyAgent[str, int, int] = from_function("AddOne", lambda x: x + 1)

        composed = sequential(double, add_one)

        assert ">>" in composed.name

        # Product state space
        initial_state = ("ready", "ready")
        state, output = composed.invoke(initial_state, 5)

        # 5 * 2 = 10, 10 + 1 = 11
        assert output == 11
        assert state == ("ready", "ready")

    def test_sequential_preserves_state(self) -> None:
        """Sequential composition preserves state product."""
        states_a = frozenset({"a1", "a2"})
        states_b = frozenset({"b1", "b2"})

        agent_a: PolyAgent[str, Any, Any] = stateful(
            "A",
            states_a,
            "a1",
            lambda s, x: ("a2" if s == "a1" else "a1", x),
        )
        agent_b: PolyAgent[str, Any, Any] = stateful(
            "B",
            states_b,
            "b1",
            lambda s, x: ("b2" if s == "b1" else "b1", x),
        )

        composed = sequential(agent_a, agent_b)

        # Initial state is product
        state, _ = composed.invoke(("a1", "b1"), 1)
        assert state == ("a2", "b2")

        # Both agents transition
        state, _ = composed.invoke(("a2", "b2"), 2)
        assert state == ("a1", "b1")


class TestParallelComposition:
    """Tests for parallel composition."""

    def test_parallel_composition(self) -> None:
        """Parallel composition runs both on same input."""
        double: PolyAgent[str, int, int] = from_function("Double", lambda x: x * 2)
        square: PolyAgent[str, int, int] = from_function("Square", lambda x: x ** 2)

        composed = parallel(double, square)

        initial_state = ("ready", "ready")
        state, output = composed.invoke(initial_state, 5)

        # (5 * 2, 5 ** 2) = (10, 25)
        assert output == (10, 25)
        assert state == ("ready", "ready")

    def test_parallel_state_product(self) -> None:
        """Parallel composition has product state space."""
        double: PolyAgent[str, int, int] = from_function("Double", lambda x: x * 2)
        square: PolyAgent[str, int, int] = from_function("Square", lambda x: x ** 2)

        composed = parallel(double, square)

        # Product of positions
        expected_positions = frozenset({("ready", "ready")})
        assert composed.positions == expected_positions


class TestWiringDiagram:
    """Tests for wiring diagrams."""

    def test_wiring_diagram_compose(self) -> None:
        """WiringDiagram.compose creates sequential agent."""
        double: PolyAgent[str, int, int] = from_function("Double", lambda x: x * 2)
        add_one: PolyAgent[str, int, int] = from_function("AddOne", lambda x: x + 1)

        diagram = WiringDiagram("test", double, add_one)
        composed = diagram.compose()

        state, output = composed.invoke(("ready", "ready"), 5)
        assert output == 11

    def test_wiring_diagram_positions(self) -> None:
        """WiringDiagram has product positions."""
        double: PolyAgent[str, int, int] = from_function("Double", lambda x: x * 2)
        add_one: PolyAgent[str, int, int] = from_function("AddOne", lambda x: x + 1)

        diagram = WiringDiagram("test", double, add_one)

        expected = frozenset({("ready", "ready")})
        assert diagram.composed_positions == expected


class TestCompositionLaws:
    """Tests for categorical laws of composition."""

    def test_identity_law_left(self) -> None:
        """Id >> f = f (left identity)."""
        f: PolyAgent[str, int, int] = from_function("F", lambda x: x + 1)
        id_agent = identity()

        composed = sequential(id_agent, f)

        # Id >> f should behave like f
        _, result_composed = composed.invoke(("ready", "ready"), 5)
        _, result_f = f.invoke("ready", 5)

        assert result_composed == result_f

    def test_identity_law_right(self) -> None:
        """f >> Id = f (right identity)."""
        f: PolyAgent[str, int, int] = from_function("F", lambda x: x + 1)
        id_agent = identity()

        composed = sequential(f, id_agent)

        # f >> Id should behave like f
        _, result_composed = composed.invoke(("ready", "ready"), 5)
        _, result_f = f.invoke("ready", 5)

        assert result_composed == result_f

    def test_associativity_law(self) -> None:
        """(f >> g) >> h = f >> (g >> h) (associativity)."""
        f: PolyAgent[str, int, int] = from_function("F", lambda x: x + 1)
        g: PolyAgent[str, int, int] = from_function("G", lambda x: x * 2)
        h: PolyAgent[str, int, int] = from_function("H", lambda x: x - 3)

        # (f >> g) >> h
        left = sequential(sequential(f, g), h)

        # f >> (g >> h)
        right = sequential(f, sequential(g, h))

        # Apply to test input
        _, result_left = left.invoke((("ready", "ready"), "ready"), 5)
        _, result_right = right.invoke(("ready", ("ready", "ready")), 5)

        # Both should equal: ((5 + 1) * 2) - 3 = 9
        assert result_left == result_right == 9


class TestStateDependentBehavior:
    """Tests for mode-dependent behavior (the key polynomial insight)."""

    def test_state_dependent_directions(self) -> None:
        """Different states accept different inputs."""
        states = frozenset({"locked", "unlocked"})

        def directions(s: str) -> frozenset[str]:
            if s == "locked":
                return frozenset({"unlock"})
            return frozenset({"lock", "use"})

        def transition(s: str, action: str) -> tuple[str, str]:
            if s == "locked" and action == "unlock":
                return "unlocked", "door opened"
            if s == "unlocked" and action == "lock":
                return "locked", "door closed"
            if s == "unlocked" and action == "use":
                return "unlocked", "entered"
            return s, "invalid action"

        door = PolyAgent(
            name="Door",
            positions=states,
            _directions=directions,
            _transition=transition,
        )

        # Locked state only accepts "unlock"
        locked_dirs = door.directions("locked")
        assert "unlock" in locked_dirs
        assert "use" not in locked_dirs

        # Unlocked accepts "lock" and "use"
        unlocked_dirs = door.directions("unlocked")
        assert "lock" in unlocked_dirs
        assert "use" in unlocked_dirs

    def test_mode_transition(self) -> None:
        """Agent transitions between modes based on input."""
        modes = frozenset({"idle", "active", "done"})

        def transition(mode: str, cmd: str) -> tuple[str, str]:
            if mode == "idle" and cmd == "start":
                return "active", "started"
            if mode == "active" and cmd == "finish":
                return "done", "finished"
            if mode == "active" and cmd == "reset":
                return "idle", "reset"
            return mode, "no-op"

        workflow = stateful(
            "Workflow",
            modes,
            "idle",
            transition,
            lambda s: frozenset({"start"})
            if s == "idle"
            else frozenset({"finish", "reset"})
            if s == "active"
            else frozenset(),
        )

        # Start from idle
        state, output = workflow.invoke("idle", "start")
        assert state == "active"
        assert output == "started"

        # Finish from active
        state, output = workflow.invoke("active", "finish")
        assert state == "done"
        assert output == "finished"

        # Done accepts nothing
        done_dirs = workflow.directions("done")
        assert len(done_dirs) == 0
