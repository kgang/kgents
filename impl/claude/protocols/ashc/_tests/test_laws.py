"""Tests for L0 composition laws.

These tests verify the categorical laws that L0 must satisfy:
- Identity: Id >> f == f == f >> Id
- Associativity: (f >> g) >> h == f >> (g >> h)
- Witness completeness: Every run emits witness when requested
- Fail-fast: Errors halt immediately
"""

import pytest

from protocols.ashc import L0Error, L0Program, L0Result
from protocols.ashc.primitives import L0Primitives, get_primitives


class TestIdentityLaw:
    """Tests for identity law: Id >> f == f == f >> Id"""

    @pytest.mark.asyncio
    async def test_left_identity(self) -> None:
        """Id >> f == f"""
        prims = get_primitives()

        # Identity function
        async def identity(x: int) -> int:
            return x

        # Test function
        def double(x: int) -> int:
            return x * 2

        # Compose: identity >> double
        composed = prims.compose(identity, double)

        # Test with multiple values
        for x in [0, 1, 5, 100, -10]:
            composed_result = await composed(x)
            direct_result = double(x)
            assert composed_result == direct_result, f"Left identity failed for {x}"

    @pytest.mark.asyncio
    async def test_right_identity(self) -> None:
        """f >> Id == f"""
        prims = get_primitives()

        # Identity function
        async def identity(x: int) -> int:
            return x

        # Test function
        def double(x: int) -> int:
            return x * 2

        # Compose: double >> identity
        composed = prims.compose(double, identity)

        # Test with multiple values
        for x in [0, 1, 5, 100, -10]:
            composed_result = await composed(x)
            direct_result = double(x)
            assert composed_result == direct_result, f"Right identity failed for {x}"


class TestAssociativityLaw:
    """Tests for associativity: (f >> g) >> h == f >> (g >> h)"""

    @pytest.mark.asyncio
    async def test_associativity_simple(self) -> None:
        """(f >> g) >> h == f >> (g >> h) for simple functions."""
        prims = get_primitives()

        def add_one(x: int) -> int:
            return x + 1

        def double(x: int) -> int:
            return x * 2

        def square(x: int) -> int:
            return x**2

        # Left grouping: (add_one >> double) >> square
        left = prims.compose(prims.compose(add_one, double), square)

        # Right grouping: add_one >> (double >> square)
        right = prims.compose(add_one, prims.compose(double, square))

        # Test with multiple values
        for x in [0, 1, 2, 3, 5, 10]:
            left_result = await left(x)
            right_result = await right(x)
            assert left_result == right_result, f"Associativity failed for {x}"

    @pytest.mark.asyncio
    async def test_associativity_with_async(self) -> None:
        """Associativity holds for async functions."""
        prims = get_primitives()

        async def add_one(x: int) -> int:
            return x + 1

        async def double(x: int) -> int:
            return x * 2

        async def square(x: int) -> int:
            return x**2

        left = prims.compose(prims.compose(add_one, double), square)
        right = prims.compose(add_one, prims.compose(double, square))

        for x in [0, 1, 2, 3]:
            left_result = await left(x)
            right_result = await right(x)
            assert left_result == right_result

    @pytest.mark.asyncio
    async def test_associativity_mixed(self) -> None:
        """Associativity holds for mixed sync/async."""
        prims = get_primitives()

        def add_one(x: int) -> int:
            return x + 1

        async def double(x: int) -> int:
            return x * 2

        def square(x: int) -> int:
            return x**2

        left = prims.compose(prims.compose(add_one, double), square)
        right = prims.compose(add_one, prims.compose(double, square))

        for x in [0, 1, 2, 3]:
            left_result = await left(x)
            right_result = await right(x)
            assert left_result == right_result


class TestWitnessCompleteness:
    """Tests for witness completeness: every pass emits witness when requested."""

    @pytest.mark.asyncio
    async def test_witness_emitted_for_each_pass(self) -> None:
        """Each witness statement produces a witness."""
        prog = L0Program("witness_complete")

        # Define multiple passes
        inp = prog.define("input", prog.literal({"step": 0}))
        step1 = prog.define("step1", prog.literal({"step": 1}))
        step2 = prog.define("step2", prog.literal({"step": 2}))
        out = prog.define("output", prog.literal({"step": 3}))

        # Witness each transition
        prog.witness("pass_0_1", inp, step1)
        prog.witness("pass_1_2", step1, step2)
        prog.witness("pass_2_3", step2, out)

        result = await prog.run()

        # Verify all witnesses present
        assert len(result.witnesses) == 3
        pass_names = [w.pass_name for w in result.witnesses]
        assert "pass_0_1" in pass_names
        assert "pass_1_2" in pass_names
        assert "pass_2_3" in pass_names

    @pytest.mark.asyncio
    async def test_witness_captures_actual_values(self) -> None:
        """Witness captures the actual computed values."""
        prog = L0Program("witness_values")

        def transform(x: int) -> int:
            return x * 2 + 1

        inp = prog.define("inp", prog.literal(5))
        out = prog.define("out", prog.call(transform, x=inp))
        prog.witness("transform", inp, out)

        result = await prog.run()

        # Verify input/output captured correctly
        assert len(result.witnesses) == 1
        witness = result.witnesses[0]
        assert witness.input_data["_value"] == 5  # Input was 5
        assert witness.output_data["_value"] == 11  # Output was 5*2+1=11


class TestFailFast:
    """Tests for fail-fast behavior: errors halt immediately."""

    @pytest.mark.asyncio
    async def test_error_halts_before_emit(self) -> None:
        """Error in define halts before emit can run."""
        prog = L0Program("fail_before_emit")

        def bad() -> int:
            raise ValueError("intentional")

        prog.define("x", prog.call(bad))
        prog.emit("should_not_happen", prog.handle("x"))

        with pytest.raises(L0Error):
            await prog.run()

    @pytest.mark.asyncio
    async def test_error_halts_before_witness(self) -> None:
        """Error halts before witness can run."""
        prog = L0Program("fail_before_witness")

        def bad() -> int:
            raise ValueError("intentional")

        inp = prog.define("inp", prog.literal(1))
        prog.define("out", prog.call(bad))
        prog.witness("should_not_happen", inp, prog.handle("out"))

        with pytest.raises(L0Error):
            await prog.run()

    @pytest.mark.asyncio
    async def test_first_error_wins(self) -> None:
        """First error is the one that halts, not later ones."""
        prog = L0Program("first_error")

        def first_bad() -> int:
            raise ValueError("first error")

        def second_bad() -> int:
            raise ValueError("second error")

        prog.define("x", prog.call(first_bad))
        prog.define("y", prog.call(second_bad))

        with pytest.raises(L0Error) as exc_info:
            await prog.run()

        # The error should mention "define x", not "define y"
        assert "define x" in str(exc_info.value)


class TestClosureLaw:
    """Tests for closure: composition of agents produces an agent."""

    @pytest.mark.asyncio
    async def test_composition_is_callable(self) -> None:
        """Composed result is callable."""
        prims = get_primitives()

        def f(x: int) -> int:
            return x + 1

        def g(x: int) -> int:
            return x * 2

        composed = prims.compose(f, g)

        # Should be callable
        assert callable(composed)

    @pytest.mark.asyncio
    async def test_composition_can_be_recomposed(self) -> None:
        """Composed result can be composed again."""
        prims = get_primitives()

        def f(x: int) -> int:
            return x + 1

        def g(x: int) -> int:
            return x * 2

        def h(x: int) -> int:
            return x - 3

        fg = prims.compose(f, g)
        fgh = prims.compose(fg, h)

        result = await fgh(5)
        # (5 + 1) * 2 - 3 = 9
        assert result == 9


class TestDeterminism:
    """Tests for determinism: same input always produces same output."""

    @pytest.mark.asyncio
    async def test_program_deterministic(self) -> None:
        """Program produces same result on multiple runs."""

        async def run_program() -> L0Result:
            prog = L0Program("deterministic")

            def transform(x: int) -> int:
                return x * 2 + 1

            x = prog.define("x", prog.literal(42))
            y = prog.define("y", prog.call(transform, x=x))
            prog.emit("result", y)

            return await prog.run()

        # Run multiple times
        results = [await run_program() for _ in range(5)]

        # All should have same bindings
        for r in results:
            assert r.bindings["x"] == 42
            assert r.bindings["y"] == 85
            assert r.artifacts[0].content == 85

    @pytest.mark.asyncio
    async def test_composition_deterministic(self) -> None:
        """Composition produces same result on multiple applications."""
        prims = get_primitives()

        def f(x: int) -> int:
            return x + 1

        def g(x: int) -> int:
            return x * 2

        composed = prims.compose(f, g)

        # Apply multiple times
        results = [await composed(10) for _ in range(5)]

        # All should be identical
        assert all(r == 22 for r in results)
