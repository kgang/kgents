"""
Tests for AGENTESE Category Laws

Phase 5: Composition & Category Laws

Tests verify:
- Identity law: Id >> f == f == f >> Id
- Associativity law: (f >> g) >> h == f >> (g >> h)
- Minimal Output Principle enforcement
- ComposedPath composition
- IdentityPath behavior
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, AsyncGenerator, cast

import pytest

from ..exceptions import CompositionViolationError, LawCheckFailed
from ..laws import (
    IDENTITY,
    # Law verification
    CategoryLawVerifier,
    Composable,
    Composed,
    # Core types
    Id,
    LawEnforcingComposition,
    LawVerificationResult,
    SimpleMorphism,
    # Helpers
    compose,
    create_enforcing_composition,
    create_verifier,
    # Track B (Law Enforcer): Event emission
    emit_law_check_event,
    enforce_minimal_output,
    # Minimal output
    is_single_logical_unit,
    morphism,
    pipe,
    # Track B (Law Enforcer): Verification with events
    raise_if_failed,
    verify_and_emit_associativity,
    verify_and_emit_identity,
)
from ..logos import ComposedPath, Logos
from ..node import BasicRendering
from .conftest import MockNode, MockUmwelt

# === Test Helpers ===


@dataclass
class IncrementMorphism:
    """Test morphism that increments a number."""

    name: str = "increment"

    async def invoke(self, input: int) -> int:
        return input + 1

    def __rshift__(self, other: Composable[int, Any]) -> Composed[int, Any]:
        return Composed(self, other)


@dataclass
class DoubleMorphism:
    """Test morphism that doubles a number."""

    name: str = "double"

    async def invoke(self, input: int) -> int:
        return input * 2

    def __rshift__(self, other: Composable[int, Any]) -> Composed[int, Any]:
        return Composed(self, other)


@dataclass
class SquareMorphism:
    """Test morphism that squares a number."""

    name: str = "square"

    async def invoke(self, input: int) -> int:
        return input**2

    def __rshift__(self, other: Composable[int, Any]) -> Composed[int, Any]:
        return Composed(self, other)


@dataclass
class ListMorphism:
    """Test morphism that returns a list (forbidden!)."""

    name: str = "to_list"

    async def invoke(self, input: int) -> list[int]:
        return [input, input + 1, input + 2]

    def __rshift__(self, other: Composable[list[int], Any]) -> Composed[int, Any]:
        return Composed(self, other)


@dataclass
class GeneratorMorphism:
    """Test morphism that returns a generator (allowed)."""

    name: str = "to_generator"

    async def invoke(self, input: int) -> AsyncGenerator[int, None]:
        for i in range(input):
            yield i

    def __rshift__(self, other: Composable[Any, Any]) -> Composed[int, Any]:
        return Composed(self, other)  # type: ignore[arg-type]


# === Identity Tests ===


class TestIdentity:
    """Tests for the Identity morphism."""

    @pytest.mark.asyncio
    async def test_identity_returns_input_unchanged(self) -> None:
        """Identity morphism returns input unchanged."""
        result = await Id.invoke(42)
        assert result == 42

    @pytest.mark.asyncio
    async def test_identity_with_string(self) -> None:
        """Identity works with strings."""
        result = await Id.invoke("hello")
        assert result == "hello"

    @pytest.mark.asyncio
    async def test_identity_with_dict(self) -> None:
        """Identity works with dicts."""
        data = {"key": "value"}
        result = await Id.invoke(data)
        assert result == data

    @pytest.mark.asyncio
    async def test_identity_with_none(self) -> None:
        """Identity works with None."""
        result = await Id.invoke(None)
        assert result is None

    def test_identity_name(self) -> None:
        """Identity has name 'Id'."""
        assert Id.name == "Id"

    def test_identity_singleton(self) -> None:
        """IDENTITY constant is the same as Id."""
        assert IDENTITY is Id

    def test_left_identity_composition(self) -> None:
        """Id >> f returns f."""
        f = IncrementMorphism()
        composed = Id >> f
        assert composed is f

    def test_right_identity_composition(self) -> None:
        """f >> Id returns f (via __rrshift__)."""
        f = IncrementMorphism()
        # Since IncrementMorphism doesn't implement __rrshift__,
        # we need to test via Composed
        composed = Composed(f, Id)
        assert composed.first is f
        assert composed.second is Id


# === Composed Tests ===


class TestComposed:
    """Tests for the Composed morphism."""

    @pytest.mark.asyncio
    async def test_composed_executes_in_order(self) -> None:
        """Composed morphisms execute left-to-right."""
        inc = IncrementMorphism()
        dbl = DoubleMorphism()
        # (x + 1) * 2
        composed = inc >> dbl
        result = await composed.invoke(5)
        assert result == 12  # (5 + 1) * 2 = 12

    @pytest.mark.asyncio
    async def test_composed_name(self) -> None:
        """Composed morphism has descriptive name."""
        inc = IncrementMorphism()
        dbl = DoubleMorphism()
        composed = inc >> dbl
        assert composed.name == "(increment >> double)"

    @pytest.mark.asyncio
    async def test_triple_composition(self) -> None:
        """Three morphisms can be composed."""
        inc = IncrementMorphism()
        dbl = DoubleMorphism()
        sqr = SquareMorphism()
        # ((x + 1) * 2) ^ 2
        composed = inc >> dbl >> sqr
        result = await composed.invoke(5)
        assert result == 144  # ((5 + 1) * 2) ^ 2 = 12^2 = 144

    @pytest.mark.asyncio
    async def test_composed_preserves_associativity_structurally(self) -> None:
        """Right-association preserves structural associativity."""
        inc = IncrementMorphism()
        dbl = DoubleMorphism()
        sqr = SquareMorphism()

        # (f >> g) >> h
        left_grouped = (inc >> dbl) >> sqr
        # f >> (g >> h)
        right_grouped = inc >> (dbl >> sqr)

        # Both should produce same result
        left_result = await left_grouped.invoke(5)
        right_result = await right_grouped.invoke(5)
        assert left_result == right_result == 144


# === Category Law Verification ===


class TestCategoryLawVerifier:
    """Tests for CategoryLawVerifier."""

    @pytest.fixture
    def verifier(self) -> CategoryLawVerifier:
        return CategoryLawVerifier()

    @pytest.fixture
    def inc(self) -> IncrementMorphism:
        return IncrementMorphism()

    @pytest.fixture
    def dbl(self) -> DoubleMorphism:
        return DoubleMorphism()

    @pytest.fixture
    def sqr(self) -> SquareMorphism:
        return SquareMorphism()

    @pytest.mark.asyncio
    async def test_verify_left_identity_passes(
        self, verifier: CategoryLawVerifier, inc: IncrementMorphism
    ) -> None:
        """Left identity law passes for well-behaved morphism."""
        result = await verifier.verify_left_identity(inc, 5)
        assert result.passed
        assert result.law == "left_identity"
        assert result.left_result == 6  # (Id >> inc)(5) = 6
        assert result.right_result == 6  # inc(5) = 6

    @pytest.mark.asyncio
    async def test_verify_right_identity_passes(
        self, verifier: CategoryLawVerifier, inc: IncrementMorphism
    ) -> None:
        """Right identity law passes for well-behaved morphism."""
        result = await verifier.verify_right_identity(inc, 5)
        assert result.passed
        assert result.law == "right_identity"

    @pytest.mark.asyncio
    async def test_verify_identity_passes(
        self, verifier: CategoryLawVerifier, inc: IncrementMorphism
    ) -> None:
        """Full identity law verification passes."""
        result = await verifier.verify_identity(inc, 5)
        assert result.passed
        assert result.law == "identity"

    @pytest.mark.asyncio
    async def test_verify_associativity_passes(
        self,
        verifier: CategoryLawVerifier,
        inc: IncrementMorphism,
        dbl: DoubleMorphism,
        sqr: SquareMorphism,
    ) -> None:
        """Associativity law passes for well-behaved morphisms."""
        result = await verifier.verify_associativity(inc, dbl, sqr, 5)
        assert result.passed
        assert result.law == "associativity"
        # Both should be 144: ((5+1)*2)^2
        assert result.left_result == 144
        assert result.right_result == 144

    @pytest.mark.asyncio
    async def test_verify_all(
        self,
        verifier: CategoryLawVerifier,
        inc: IncrementMorphism,
        dbl: DoubleMorphism,
        sqr: SquareMorphism,
    ) -> None:
        """verify_all checks all laws."""
        results = await verifier.verify_all(inc, dbl, sqr, 5)
        assert len(results) == 3
        assert all(r.passed for r in results)
        assert {r.law for r in results} == {
            "left_identity",
            "right_identity",
            "associativity",
        }

    @pytest.mark.asyncio
    async def test_result_is_boolean(
        self, verifier: CategoryLawVerifier, inc: IncrementMorphism
    ) -> None:
        """LawVerificationResult can be used as boolean."""
        result = await verifier.verify_left_identity(inc, 5)
        assert bool(result) is True

    @pytest.mark.asyncio
    async def test_custom_comparator(self) -> None:
        """Custom comparator for result equality."""

        # Use approximate comparison
        def approx_equal(a: Any, b: Any) -> bool:
            return cast(bool, abs(a - b) < 0.01)

        verifier = CategoryLawVerifier(comparator=approx_equal)
        result = await verifier.verify_left_identity(IncrementMorphism(), 5)
        assert result.passed


# === Minimal Output Principle ===


class TestMinimalOutputPrinciple:
    """Tests for the Minimal Output Principle."""

    def test_single_value_is_allowed(self) -> None:
        """Single values are valid returns."""
        assert is_single_logical_unit(42) is True
        assert is_single_logical_unit("hello") is True
        assert is_single_logical_unit({"key": "value"}) is True

    def test_renderable_is_allowed(self) -> None:
        """Renderable objects are valid returns."""
        rendering = BasicRendering(summary="test")
        assert is_single_logical_unit(rendering) is True

    def test_list_is_forbidden(self) -> None:
        """Lists are forbidden returns."""
        assert is_single_logical_unit([1, 2, 3]) is False

    def test_tuple_is_forbidden(self) -> None:
        """Tuples are forbidden returns."""
        assert is_single_logical_unit((1, 2, 3)) is False

    def test_set_is_forbidden(self) -> None:
        """Sets are forbidden returns."""
        assert is_single_logical_unit({1, 2, 3}) is False

    def test_empty_list_is_forbidden(self) -> None:
        """Even empty lists are forbidden."""
        assert is_single_logical_unit([]) is False

    def test_generator_is_allowed(self) -> None:
        """Generators (lazy sequences) are allowed."""
        gen = (x for x in range(10))
        assert is_single_logical_unit(gen) is True

    def test_none_is_allowed(self) -> None:
        """None is a valid single unit."""
        assert is_single_logical_unit(None) is True

    def test_dataclass_is_allowed(self) -> None:
        """Dataclasses are valid single units."""

        @dataclass
        class Point:
            x: int
            y: int

        assert is_single_logical_unit(Point(1, 2)) is True

    def test_enforce_raises_on_list(self) -> None:
        """enforce_minimal_output raises on list."""
        with pytest.raises(CompositionViolationError) as exc_info:
            enforce_minimal_output([1, 2, 3])

        error = exc_info.value
        assert "Array return" in str(error)
        assert error.law_violated == "minimal_output"

    def test_enforce_returns_valid_value(self) -> None:
        """enforce_minimal_output returns valid values unchanged."""
        value = {"key": "value"}
        result = enforce_minimal_output(value)
        assert result == value

    def test_enforce_with_context(self) -> None:
        """enforce_minimal_output includes context in error."""
        with pytest.raises(CompositionViolationError) as exc_info:
            enforce_minimal_output([1, 2], "world.users.manifest")

        error = exc_info.value
        assert "list" in str(error)


# === Compose and Pipe Helpers ===


class TestComposeHelper:
    """Tests for the compose() helper function."""

    @pytest.mark.asyncio
    async def test_compose_two(self) -> None:
        """compose() works with two morphisms."""
        composed = compose(IncrementMorphism(), DoubleMorphism())
        result = await composed.invoke(5)
        assert result == 12

    @pytest.mark.asyncio
    async def test_compose_three(self) -> None:
        """compose() works with three morphisms."""
        composed = compose(
            IncrementMorphism(),
            DoubleMorphism(),
            SquareMorphism(),
        )
        result = await composed.invoke(5)
        assert result == 144

    def test_compose_single_returns_itself(self) -> None:
        """compose() with single morphism returns it."""
        f = IncrementMorphism()
        composed = compose(f)
        assert composed is f

    def test_compose_requires_at_least_one(self) -> None:
        """compose() requires at least one morphism."""
        with pytest.raises(ValueError):
            compose()


class TestPipeHelper:
    """Tests for the pipe() helper function."""

    @pytest.mark.asyncio
    async def test_pipe_single(self) -> None:
        """pipe() works with single morphism."""
        result = await pipe(5, IncrementMorphism())
        assert result == 6

    @pytest.mark.asyncio
    async def test_pipe_multiple(self) -> None:
        """pipe() works with multiple morphisms."""
        result = await pipe(
            5,
            IncrementMorphism(),
            DoubleMorphism(),
            SquareMorphism(),
        )
        assert result == 144

    @pytest.mark.asyncio
    async def test_pipe_empty(self) -> None:
        """pipe() with no morphisms returns input."""
        result = await pipe(42)
        assert result == 42


# === SimpleMorphism and Decorator ===


class TestSimpleMorphism:
    """Tests for SimpleMorphism helper."""

    @pytest.mark.asyncio
    async def test_simple_morphism_sync(self) -> None:
        """SimpleMorphism wraps sync functions."""
        m = SimpleMorphism("add_one", lambda x: x + 1)
        result = await m.invoke(5)
        assert result == 6

    @pytest.mark.asyncio
    async def test_simple_morphism_async(self) -> None:
        """SimpleMorphism wraps async functions."""

        async def async_add(x: int) -> int:
            return x + 1

        m = SimpleMorphism("async_add", async_add)
        result = await m.invoke(5)
        assert result == 6

    def test_simple_morphism_composition(self) -> None:
        """SimpleMorphism can be composed."""
        add = SimpleMorphism("add", lambda x: x + 1)
        mul = SimpleMorphism("mul", lambda x: x * 2)
        composed = add >> mul
        assert isinstance(composed, Composed)


class TestMorphismDecorator:
    """Tests for @morphism decorator."""

    def test_morphism_decorator(self) -> None:
        """@morphism creates SimpleMorphism."""

        @morphism("double")
        def double(x: int) -> int:
            return x * 2

        assert isinstance(double, SimpleMorphism)
        assert double.name == "double"

    @pytest.mark.asyncio
    async def test_decorated_morphism_invokes(self) -> None:
        """Decorated morphism can be invoked."""

        @morphism("triple")
        def triple(x: int) -> int:
            return x * 3

        result = await triple.invoke(5)
        assert result == 15


# === Law-Enforcing Composition ===


class TestLawEnforcingComposition:
    """Tests for LawEnforcingComposition."""

    @pytest.mark.asyncio
    async def test_enforcing_composition_invokes(self) -> None:
        """LawEnforcingComposition invokes correctly."""
        composed = Composed(IncrementMorphism(), DoubleMorphism())
        enforcing = LawEnforcingComposition(composed)
        result = await enforcing.invoke(5)
        assert result == 12

    @pytest.mark.asyncio
    async def test_enforcing_composition_checks_output(self) -> None:
        """LawEnforcingComposition enforces minimal output."""
        composed = Composed(IncrementMorphism(), ListMorphism())
        enforcing = LawEnforcingComposition(composed)
        with pytest.raises(CompositionViolationError):
            await enforcing.invoke(5)

    def test_enforcing_composition_name(self) -> None:
        """LawEnforcingComposition has descriptive name."""
        composed = Composed(IncrementMorphism(), DoubleMorphism())
        enforcing = LawEnforcingComposition(composed)
        assert "Verified" in enforcing.name
        assert "increment" in enforcing.name

    def test_enforcing_composition_chains(self) -> None:
        """LawEnforcingComposition can be chained."""
        composed = Composed(IncrementMorphism(), DoubleMorphism())
        enforcing = LawEnforcingComposition(composed)
        chained = enforcing >> SquareMorphism()
        assert isinstance(chained, LawEnforcingComposition)


# === ComposedPath Tests ===


class TestComposedPath:
    """Tests for ComposedPath from logos.py."""

    @pytest.fixture
    def logos(self) -> Logos:
        """Create Logos with test nodes."""
        logos = Logos()
        # Register nodes that return single values
        logos.register(
            "world.test",
            MockNode(
                handle="world.test",
                _affordances={"default": ("process",)},
            ),
        )
        return logos

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt()

    def test_composed_path_len(self, logos: Logos) -> None:
        """ComposedPath has length."""
        path = logos.compose("a.b.c", "d.e.f")
        assert len(path) == 2

    def test_composed_path_iter(self, logos: Logos) -> None:
        """ComposedPath is iterable."""
        path = logos.compose("a.b.c", "d.e.f", "g.h.i")
        paths = list(path)
        assert paths == ["a.b.c", "d.e.f", "g.h.i"]

    def test_composed_path_name(self, logos: Logos) -> None:
        """ComposedPath has readable name."""
        path = logos.compose("a.b.c", "d.e.f")
        assert path.name == "a.b.c >> d.e.f"

    def test_composed_path_rshift_string(self, logos: Logos) -> None:
        """ComposedPath >> string appends path."""
        path = logos.compose("a.b.c")
        extended = path >> "d.e.f"
        assert len(extended) == 2
        assert list(extended) == ["a.b.c", "d.e.f"]

    def test_composed_path_rshift_composed(self, logos: Logos) -> None:
        """ComposedPath >> ComposedPath combines paths."""
        path1 = logos.compose("a.b.c")
        path2 = logos.compose("d.e.f", "g.h.i")
        combined = path1 >> path2
        assert len(combined) == 3
        assert list(combined) == ["a.b.c", "d.e.f", "g.h.i"]

    def test_composed_path_equality(self, logos: Logos) -> None:
        """ComposedPath equality based on paths."""
        path1 = logos.compose("a.b.c", "d.e.f")
        path2 = logos.compose("a.b.c", "d.e.f")
        path3 = logos.compose("a.b.c")
        assert path1 == path2
        assert path1 != path3

    def test_without_enforcement(self, logos: Logos) -> None:
        """without_enforcement creates version without output checks."""
        path = logos.compose("a.b.c")
        assert path._enforce_minimal_output is True
        relaxed = path.without_enforcement()
        assert relaxed._enforce_minimal_output is False


class TestIdentityPath:
    """Tests for IdentityPath from logos.py."""

    @pytest.fixture
    def logos(self) -> Logos:
        return Logos()

    @pytest.fixture
    def observer(self) -> MockUmwelt:
        return MockUmwelt()

    def test_identity_path_name(self, logos: Logos) -> None:
        """IdentityPath has name 'Id'."""
        id_path = logos.identity()
        assert id_path.name == "Id"

    @pytest.mark.asyncio
    async def test_identity_path_invoke(
        self, logos: Logos, observer: MockUmwelt
    ) -> None:
        """IdentityPath invoke returns input unchanged."""
        id_path = logos.identity()
        result = await id_path.invoke(cast(Any, observer), initial_input="test")
        assert result == "test"

    def test_identity_path_rshift_string(self, logos: Logos) -> None:
        """IdentityPath >> string creates ComposedPath."""
        id_path = logos.identity()
        path = id_path >> "world.house.manifest"
        assert isinstance(path, ComposedPath)
        assert list(path) == ["world.house.manifest"]

    def test_identity_path_rshift_composed(self, logos: Logos) -> None:
        """IdentityPath >> ComposedPath returns ComposedPath unchanged."""
        id_path = logos.identity()
        composed = logos.compose("a.b.c", "d.e.f")
        result = id_path >> composed
        assert result is composed


class TestLogosPath:
    """Tests for logos.path() helper."""

    @pytest.fixture
    def logos(self) -> Logos:
        return Logos()

    def test_path_creates_composed(self, logos: Logos) -> None:
        """logos.path() creates single-path ComposedPath."""
        path = logos.path("world.house.manifest")
        assert isinstance(path, ComposedPath)
        assert len(path) == 1

    def test_path_chainable(self, logos: Logos) -> None:
        """logos.path() result is chainable."""
        path = logos.path("a.b.c") >> "d.e.f" >> "g.h.i"
        assert len(path) == 3


# === Category Law Property Tests ===


@pytest.mark.law
class TestCategoryLaws:
    """Property tests for category laws (marked with 'law' marker)."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_value", [0, 1, -1, 100, -100])
    async def test_identity_law_left(self, input_value: int) -> None:
        """Id >> f == f for all inputs."""
        f = IncrementMorphism()
        verifier = CategoryLawVerifier()
        result = await verifier.verify_left_identity(f, input_value)
        assert result.passed, f"Left identity failed for input {input_value}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_value", [0, 1, -1, 100, -100])
    async def test_identity_law_right(self, input_value: int) -> None:
        """f >> Id == f for all inputs."""
        f = IncrementMorphism()
        verifier = CategoryLawVerifier()
        result = await verifier.verify_right_identity(f, input_value)
        assert result.passed, f"Right identity failed for input {input_value}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_value", [0, 1, 2, 5, 10])
    async def test_associativity_law(self, input_value: int) -> None:
        """(f >> g) >> h == f >> (g >> h) for all inputs."""
        f = IncrementMorphism()
        g = DoubleMorphism()
        h = SquareMorphism()
        verifier = CategoryLawVerifier()
        result = await verifier.verify_associativity(f, g, h, input_value)
        assert result.passed, f"Associativity failed for input {input_value}"

    @pytest.mark.asyncio
    async def test_composition_is_closed(self) -> None:
        """Composition of composables is composable."""
        f = IncrementMorphism()
        g = DoubleMorphism()
        fg = f >> g
        h = SquareMorphism()
        # Should be able to compose again
        fgh = fg >> h
        assert hasattr(fgh, "invoke")
        assert hasattr(fgh, "__rshift__")


# === Factory Function Tests ===


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_verifier_default(self) -> None:
        """create_verifier() returns default verifier."""
        verifier = create_verifier()
        assert isinstance(verifier, CategoryLawVerifier)

    def test_create_verifier_custom_comparator(self) -> None:
        """create_verifier() accepts custom comparator."""
        verifier = create_verifier(comparator=lambda a, b: True)
        assert verifier.comparator(1, 2) is True

    def test_create_enforcing_composition_multiple(self) -> None:
        """create_enforcing_composition() with multiple morphisms."""
        ec = create_enforcing_composition(
            IncrementMorphism(),
            DoubleMorphism(),
        )
        assert isinstance(ec, LawEnforcingComposition)

    def test_create_enforcing_composition_single(self) -> None:
        """create_enforcing_composition() with single morphism."""
        ec = create_enforcing_composition(IncrementMorphism())
        assert isinstance(ec, LawEnforcingComposition)


# === Track B (Law Enforcer): LawCheckFailed Tests ===


class TestLawCheckFailed:
    """Tests for LawCheckFailed exception (Track B: Law Enforcer)."""

    def test_basic_construction(self) -> None:
        """LawCheckFailed can be constructed with basic args."""
        exc = LawCheckFailed("test message", law="identity", locus="f >> g")
        assert exc.law == "identity"
        assert exc.locus == "f >> g"
        assert "test message" in str(exc)

    def test_identity_law_why(self) -> None:
        """LawCheckFailed provides why for identity law."""
        exc = LawCheckFailed("test", law="identity")
        assert exc.why is not None
        assert "Id >> f" in exc.why or "should equal" in exc.why

    def test_associativity_law_why(self) -> None:
        """LawCheckFailed provides why for associativity law."""
        exc = LawCheckFailed("test", law="associativity")
        assert exc.why is not None
        assert "(f >> g) >> h" in exc.why or "should equal" in exc.why

    def test_identity_law_suggestion(self) -> None:
        """LawCheckFailed provides suggestion for identity law."""
        exc = LawCheckFailed("test", law="identity")
        assert exc.suggestion is not None
        assert "pure" in exc.suggestion.lower() or "state" in exc.suggestion.lower()

    def test_associativity_law_suggestion(self) -> None:
        """LawCheckFailed provides suggestion for associativity law."""
        exc = LawCheckFailed("test", law="associativity")
        assert exc.suggestion is not None
        assert "output" in exc.suggestion.lower() or "type" in exc.suggestion.lower()

    def test_from_verification_factory(self) -> None:
        """from_verification creates LawCheckFailed from verification result."""
        exc = LawCheckFailed.from_verification(
            law="associativity",
            locus="a >> b >> c",
            left_result="left",
            right_result="right",
        )
        assert exc.law == "associativity"
        assert exc.locus == "a >> b >> c"
        assert exc.left_result == "left"
        assert exc.right_result == "right"
        assert "a >> b >> c" in str(exc)

    def test_related_includes_locus(self) -> None:
        """LawCheckFailed includes locus in related paths."""
        exc = LawCheckFailed("test", law="identity", locus="test.path")
        assert exc.related is not None
        assert "test.path" in exc.related


# === Track B (Law Enforcer): Event Emission Tests ===


class TestLawCheckEventEmission:
    """Tests for law check event emission (Track B: Law Enforcer)."""

    def test_emit_law_check_event_without_span(self) -> None:
        """emit_law_check_event works even without active span."""
        # Should not raise - silently succeeds
        emit_law_check_event("identity", "pass", "test.path")

    def test_raise_if_failed_passes_on_success(self) -> None:
        """raise_if_failed does not raise on passing result."""
        result = LawVerificationResult(law="identity", passed=True)
        raise_if_failed(result, "test.path")  # Should not raise

    def test_raise_if_failed_raises_on_failure(self) -> None:
        """raise_if_failed raises LawCheckFailed on failing result."""
        result = LawVerificationResult(
            law="associativity",
            passed=False,
            left_result="a",
            right_result="b",
        )
        with pytest.raises(LawCheckFailed) as exc_info:
            raise_if_failed(result, "f >> g >> h")

        exc = exc_info.value
        assert exc.law == "associativity"
        assert exc.locus == "f >> g >> h"


class TestVerifyAndEmitFunctions:
    """Tests for verify_and_emit_* functions (Track B: Law Enforcer)."""

    @pytest.mark.asyncio
    async def test_verify_and_emit_identity(self) -> None:
        """verify_and_emit_identity verifies and returns result."""
        morphism = IncrementMorphism()
        result = await verify_and_emit_identity(morphism, 5, "increment")
        assert result.passed is True
        assert result.law == "identity"

    @pytest.mark.asyncio
    async def test_verify_and_emit_associativity(self) -> None:
        """verify_and_emit_associativity verifies and returns result."""
        f = IncrementMorphism()
        g = DoubleMorphism()
        h = SquareMorphism()
        result = await verify_and_emit_associativity(f, g, h, 5, "f >> g >> h")
        assert result.passed is True
        assert result.law == "associativity"

    @pytest.mark.asyncio
    async def test_verify_and_emit_associativity_builds_locus(self) -> None:
        """verify_and_emit_associativity builds locus from morphism names."""
        f = IncrementMorphism()
        g = DoubleMorphism()
        h = SquareMorphism()
        # Call without providing locus
        result = await verify_and_emit_associativity(f, g, h, 5)
        assert result.passed is True


# === Track B (Law Enforcer): ComposedPath Law Check Tests ===


class TestComposedPathLawChecks:
    """Tests for ComposedPath law check features (Track B: Law Enforcer)."""

    @pytest.fixture
    def logos(self) -> Logos:
        return Logos()

    def test_composed_path_default_emit_law_check(self, logos: Logos) -> None:
        """ComposedPath emits law checks by default."""
        path = logos.compose("a.b.c", "d.e.f")
        assert path._emit_law_check is True

    def test_without_law_checks(self, logos: Logos) -> None:
        """without_law_checks disables law check emission."""
        path = logos.compose("a.b.c", "d.e.f")
        relaxed = path.without_law_checks()
        assert relaxed._emit_law_check is False
        # Other settings preserved
        assert relaxed._enforce_minimal_output is True

    def test_with_law_checks(self, logos: Logos) -> None:
        """with_law_checks explicitly controls law check emission."""
        path = logos.compose("a.b.c", "d.e.f")
        relaxed = path.with_law_checks(False)
        assert relaxed._emit_law_check is False
        enabled = relaxed.with_law_checks(True)
        assert enabled._emit_law_check is True

    def test_rshift_preserves_law_check(self, logos: Logos) -> None:
        """>> operator preserves law check setting."""
        path = logos.path("a.b.c", emit_law_check=False)
        extended = path >> "d.e.f"
        assert extended._emit_law_check is False

    def test_rshift_combined_paths_and_flags(self, logos: Logos) -> None:
        """>> with ComposedPath combines law check flags (AND)."""
        path1 = logos.compose("a.b.c", emit_law_check=True)
        path2 = logos.compose("d.e.f", emit_law_check=False)
        combined = path1 >> path2
        # Should be False because both must be True
        assert combined._emit_law_check is False

    def test_logos_compose_emit_law_check_param(self, logos: Logos) -> None:
        """logos.compose accepts emit_law_check parameter."""
        path = logos.compose("a.b.c", "d.e.f", emit_law_check=False)
        assert path._emit_law_check is False

    def test_logos_path_emit_law_check_param(self, logos: Logos) -> None:
        """logos.path accepts emit_law_check parameter."""
        path = logos.path("a.b.c", emit_law_check=False)
        assert path._emit_law_check is False
