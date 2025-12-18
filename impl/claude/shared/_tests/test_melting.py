"""
Tests for shared/melting.py - Contract-Bounded Hallucination (Pataphysics)

Tests cover:
1. @meltable decorator with postconditions
2. Contract enforcement and retries
3. ContractViolationError on exhausted retries
4. Custom pataphysics solvers
5. Utility functions (is_meltable, get_postcondition)
"""

from __future__ import annotations

import pytest

from shared.melting import (
    ContractViolationError,
    MeltingContext,
    default_pataphysics_solver,
    get_postcondition,
    is_meltable,
    meltable,
    meltable_sync,
)

# === Test Basic @meltable Behavior ===


class TestMeltableBasic:
    """Test basic @meltable decorator behavior."""

    @pytest.mark.asyncio
    async def test_meltable_passes_through_on_success(self) -> None:
        """Function that succeeds should return normally."""

        @meltable()
        async def always_works() -> int:
            return 42

        result: int = await always_works()
        assert result == 42

    @pytest.mark.asyncio
    async def test_meltable_passes_postcondition_check(self) -> None:
        """Successful result that passes postcondition should return."""

        @meltable(ensure=lambda x: x > 0)
        async def returns_positive() -> int:
            return 10

        result: int = await returns_positive()
        assert result == 10

    @pytest.mark.asyncio
    async def test_meltable_fails_postcondition_on_success(self) -> None:
        """Successful result that fails postcondition should raise."""

        @meltable(ensure=lambda x: x > 100)
        async def returns_small() -> int:
            return 10

        with pytest.raises(ContractViolationError) as exc_info:
            await returns_small()

        assert "Postcondition failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_meltable_is_marked(self) -> None:
        """Decorated function should be marked as meltable."""

        @meltable()
        async def some_func() -> int:
            return 1

        assert is_meltable(some_func)

    @pytest.mark.asyncio
    async def test_non_meltable_is_not_marked(self) -> None:
        """Non-decorated function should not be marked."""

        async def some_func() -> int:
            return 1

        assert not is_meltable(some_func)


# === Test Contract Enforcement ===


class TestContractEnforcement:
    """Test postcondition (ensure) enforcement."""

    @pytest.mark.asyncio
    async def test_ensure_probability_range(self) -> None:
        """Test probability range postcondition."""

        @meltable(ensure=lambda x: 0.0 <= x <= 1.0)
        async def valid_probability() -> float:
            return 0.5

        result: float = await valid_probability()
        assert 0.0 <= result <= 1.0

    @pytest.mark.asyncio
    async def test_ensure_non_empty_string(self) -> None:
        """Test non-empty string postcondition."""

        @meltable(ensure=lambda x: len(x) > 0)
        async def non_empty() -> str:
            return "hello"

        result: str = await non_empty()
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_postcondition_returns_ensure(self) -> None:
        """get_postcondition should return the ensure predicate."""

        def predicate(x: int) -> bool:
            return x > 0

        @meltable(ensure=predicate)
        async def some_func() -> int:
            return 1

        assert get_postcondition(some_func) is predicate

    @pytest.mark.asyncio
    async def test_get_postcondition_returns_none_if_missing(self) -> None:
        """get_postcondition should return None if no ensure."""

        @meltable()
        async def some_func() -> int:
            return 1

        assert get_postcondition(some_func) is None


# === Test Melting (Fallback) Behavior ===


class TestMeltingFallback:
    """Test fallback behavior when original function fails."""

    @pytest.mark.asyncio
    async def test_melting_invokes_solver_on_exception(self) -> None:
        """Exception should trigger pataphysics solver."""
        solver_called = False

        async def custom_solver(ctx: MeltingContext) -> int:
            nonlocal solver_called
            solver_called = True
            return 42

        @meltable(solver=custom_solver)
        async def always_fails() -> int:
            raise RuntimeError("Boom")

        result = await always_fails()
        assert solver_called
        assert result == 42

    @pytest.mark.asyncio
    async def test_melting_retries_on_contract_failure(self) -> None:
        """Solver should be retried if result fails postcondition."""
        attempt_count = 0

        async def improving_solver(ctx: MeltingContext) -> int:
            nonlocal attempt_count
            attempt_count += 1
            # First two attempts return invalid, third is valid
            if attempt_count < 3:
                return -1
            return 100

        @meltable(ensure=lambda x: x > 0, max_retries=5, solver=improving_solver)
        async def always_fails() -> int:
            raise RuntimeError("Boom")

        result = await always_fails()
        assert attempt_count == 3
        assert result == 100

    @pytest.mark.asyncio
    async def test_melting_exhausts_retries(self) -> None:
        """Should raise ContractViolationError after max_retries."""

        async def bad_solver(ctx: MeltingContext) -> int:
            return -1  # Always fails postcondition

        @meltable(ensure=lambda x: x > 0, max_retries=3, solver=bad_solver)
        async def always_fails() -> int:
            raise RuntimeError("Boom")

        with pytest.raises(ContractViolationError) as exc_info:
            await always_fails()

        assert exc_info.value.attempts == 3
        assert exc_info.value.last_result == -1
        assert exc_info.value.original_error is not None

    @pytest.mark.asyncio
    async def test_melting_context_contains_error_info(self) -> None:
        """MeltingContext should contain original error info."""
        captured_ctx: MeltingContext | None = None

        async def capturing_solver(ctx: MeltingContext) -> int:
            nonlocal captured_ctx
            captured_ctx = ctx
            return 42

        @meltable(solver=capturing_solver)
        async def fails_with_message() -> int:
            raise ValueError("specific error message")

        await fails_with_message()

        assert captured_ctx is not None
        assert captured_ctx.function_name == "fails_with_message"
        assert isinstance(captured_ctx.error, ValueError)
        assert "specific error message" in str(captured_ctx.error)


# === Test Default Solver ===


class TestDefaultSolver:
    """Test the default pataphysics solver."""

    @pytest.mark.asyncio
    async def test_default_solver_returns_none(self) -> None:
        """Default solver returns None."""
        ctx = MeltingContext(
            function_name="test",
            args=(),
            kwargs={},
            error=Exception("test"),
        )
        result = await default_pataphysics_solver(ctx)
        assert result is None

    @pytest.mark.asyncio
    async def test_meltable_with_default_solver_and_none_postcondition(self) -> None:
        """Meltable with default solver and no postcondition should return None."""

        @meltable()  # No ensure, uses default solver
        async def always_fails() -> None:
            raise RuntimeError("Boom")

        result: None = await always_fails()
        assert result is None


# === Test Synchronous @meltable_sync ===


class TestMeltableSync:
    """Test @meltable_sync for synchronous functions."""

    def test_meltable_sync_passes_through_on_success(self) -> None:
        """Sync function that succeeds should return normally."""

        @meltable_sync()
        def always_works() -> int:
            return 42

        result: int = always_works()
        assert result == 42

    def test_meltable_sync_uses_default_on_failure(self) -> None:
        """Sync function that fails should use default value."""

        @meltable_sync(default=99)
        def always_fails() -> int:
            raise RuntimeError("Boom")

        result = always_fails()
        assert result == 99

    def test_meltable_sync_validates_default(self) -> None:
        """Default value must satisfy postcondition."""

        @meltable_sync(ensure=lambda x: x > 0, default=100)
        def always_fails() -> int:
            raise RuntimeError("Boom")

        result = always_fails()
        assert result == 100

    def test_meltable_sync_rejects_invalid_default(self) -> None:
        """Invalid default should raise ContractViolationError."""

        @meltable_sync(ensure=lambda x: x > 0, default=-1)
        def always_fails() -> int:
            raise RuntimeError("Boom")

        with pytest.raises(ContractViolationError):
            always_fails()

    def test_meltable_sync_is_marked(self) -> None:
        """Sync decorated function should be marked as meltable."""

        @meltable_sync(default=0)
        def some_func() -> int:
            return 1

        assert is_meltable(some_func)


# === Test ContractViolationError ===


class TestContractViolationError:
    """Test ContractViolationError exception."""

    def test_error_str_includes_message(self) -> None:
        """Error string should include message."""
        error = ContractViolationError("Test error")
        assert "Test error" in str(error)

    def test_error_str_includes_attempts(self) -> None:
        """Error string should include attempt count."""
        error = ContractViolationError("Test error", attempts=5)
        assert "5 attempts" in str(error)

    def test_error_str_includes_original_error_type(self) -> None:
        """Error string should include original error type."""
        original = ValueError("original")
        error = ContractViolationError("Test error", original_error=original)
        assert "ValueError" in str(error)

    def test_error_is_frozen(self) -> None:
        """Error should be frozen (immutable)."""
        error = ContractViolationError("Test")
        with pytest.raises(AttributeError):
            error.message = "changed"  # type: ignore[misc]


# === Test MeltingContext ===


class TestMeltingContext:
    """Test MeltingContext dataclass."""

    def test_context_stores_function_name(self) -> None:
        """Context should store function name."""
        ctx = MeltingContext(
            function_name="my_func",
            args=(),
            kwargs={},
            error=Exception("test"),
        )
        assert ctx.function_name == "my_func"

    def test_context_stores_args_and_kwargs(self) -> None:
        """Context should store args and kwargs."""
        ctx = MeltingContext(
            function_name="func",
            args=(1, 2, 3),
            kwargs={"a": "b"},
            error=Exception("test"),
        )
        assert ctx.args == (1, 2, 3)
        assert ctx.kwargs == {"a": "b"}

    def test_context_default_attempt_is_zero(self) -> None:
        """Default attempt should be 0."""
        ctx = MeltingContext(
            function_name="func",
            args=(),
            kwargs={},
            error=Exception("test"),
        )
        assert ctx.attempt == 0

    def test_context_is_frozen(self) -> None:
        """Context should be frozen (immutable)."""
        ctx = MeltingContext(
            function_name="func",
            args=(),
            kwargs={},
            error=Exception("test"),
        )
        with pytest.raises(AttributeError):
            ctx.function_name = "changed"  # type: ignore[misc]
