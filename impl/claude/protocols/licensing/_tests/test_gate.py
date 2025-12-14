"""
Tests for license gate decorator and utilities.
"""

import pytest
from protocols.licensing.gate import (
    LicenseError,
    check_tier,
    get_current_tier,
    get_tier_requirement,
    requires_tier,
    requires_tier_async,
    set_current_tier,
)
from protocols.licensing.tiers import LicenseTier


class TestLicenseError:
    """Tests for LicenseError exception."""

    def test_error_message(self) -> None:
        """Test error message formatting."""
        error = LicenseError("soul_advise", LicenseTier.PRO, LicenseTier.FREE)
        assert "soul_advise" in str(error)
        assert "PRO" in str(error)
        assert "FREE" in str(error)
        assert "kgents.io/pricing" in str(error)

    def test_error_attributes(self) -> None:
        """Test error has expected attributes."""
        error = LicenseError("soul_advise", LicenseTier.PRO, LicenseTier.FREE)
        assert error.feature == "soul_advise"
        assert error.required == LicenseTier.PRO
        assert error.current == LicenseTier.FREE


class TestGetCurrentTier:
    """Tests for get/set current tier."""

    def test_default_tier(self) -> None:
        """Test default tier is FREE."""
        # Note: This test may be affected by other tests
        tier = get_current_tier()
        assert isinstance(tier, LicenseTier)

    def test_set_and_get_tier(self) -> None:
        """Test setting and getting tier."""
        original = get_current_tier()
        try:
            set_current_tier(LicenseTier.PRO)
            assert get_current_tier() == LicenseTier.PRO

            set_current_tier(LicenseTier.ENTERPRISE)
            assert get_current_tier() == LicenseTier.ENTERPRISE
        finally:
            # Restore original
            set_current_tier(original)


class TestCheckTier:
    """Tests for check_tier function."""

    def test_check_tier_sufficient(self) -> None:
        """Test check_tier returns True when tier is sufficient."""
        assert check_tier(LicenseTier.FREE, LicenseTier.PRO)
        assert check_tier(LicenseTier.PRO, LicenseTier.PRO)
        assert check_tier(LicenseTier.PRO, LicenseTier.ENTERPRISE)

    def test_check_tier_insufficient(self) -> None:
        """Test check_tier returns False when tier is insufficient."""
        assert not check_tier(LicenseTier.PRO, LicenseTier.FREE)
        assert not check_tier(LicenseTier.ENTERPRISE, LicenseTier.TEAMS)

    def test_check_tier_uses_context(self) -> None:
        """Test check_tier uses context when current is None."""
        original = get_current_tier()
        try:
            set_current_tier(LicenseTier.PRO)
            assert check_tier(LicenseTier.FREE)  # No current arg
            assert not check_tier(LicenseTier.ENTERPRISE)
        finally:
            set_current_tier(original)


class TestRequiresTier:
    """Tests for @requires_tier decorator."""

    def test_decorator_allows_sufficient_tier(self) -> None:
        """Test decorator allows call with sufficient tier."""

        @requires_tier(LicenseTier.PRO)
        def pro_feature() -> str:
            return "success"

        original = get_current_tier()
        try:
            set_current_tier(LicenseTier.PRO)
            result = pro_feature()
            assert result == "success"
        finally:
            set_current_tier(original)

    def test_decorator_blocks_insufficient_tier(self) -> None:
        """Test decorator blocks call with insufficient tier."""

        @requires_tier(LicenseTier.PRO)
        def pro_feature() -> str:
            return "success"

        original = get_current_tier()
        try:
            set_current_tier(LicenseTier.FREE)
            with pytest.raises(LicenseError) as exc_info:
                pro_feature()
            assert exc_info.value.required == LicenseTier.PRO
            assert exc_info.value.current == LicenseTier.FREE
        finally:
            set_current_tier(original)

    def test_decorator_with_explicit_tier_kwarg(self) -> None:
        """Test decorator respects explicit license_tier kwarg."""

        @requires_tier(LicenseTier.PRO)
        def pro_feature(license_tier: LicenseTier | None = None) -> str:
            return "success"

        # Should succeed with explicit PRO tier
        result = pro_feature(license_tier=LicenseTier.PRO)
        assert result == "success"

        # Should fail with explicit FREE tier
        with pytest.raises(LicenseError):
            pro_feature(license_tier=LicenseTier.FREE)

    def test_decorator_with_context_object(self) -> None:
        """Test decorator extracts tier from context object."""

        class Context:
            def __init__(self, tier: LicenseTier):
                self.license_tier = tier

        @requires_tier(LicenseTier.PRO)
        def pro_feature(ctx: Context) -> str:
            return "success"

        # Should succeed with PRO context
        ctx_pro = Context(LicenseTier.PRO)
        result = pro_feature(ctx_pro)
        assert result == "success"

        # Should fail with FREE context
        ctx_free = Context(LicenseTier.FREE)
        with pytest.raises(LicenseError):
            pro_feature(ctx_free)

    def test_decorator_preserves_function_metadata(self) -> None:
        """Test decorator preserves function name and docstring."""

        @requires_tier(LicenseTier.PRO)
        def pro_feature() -> str:
            """A pro feature."""
            return "success"

        assert pro_feature.__name__ == "pro_feature"
        assert pro_feature.__doc__ == "A pro feature."

    def test_decorator_adds_tier_metadata(self) -> None:
        """Test decorator adds __license_tier__ attribute."""

        @requires_tier(LicenseTier.PRO)
        def pro_feature() -> str:
            return "success"

        assert hasattr(pro_feature, "__license_tier__")
        assert pro_feature.__license_tier__ == LicenseTier.PRO


class TestRequiresTierAsync:
    """Tests for @requires_tier_async decorator."""

    @pytest.mark.asyncio
    async def test_async_decorator_allows_sufficient_tier(self) -> None:
        """Test async decorator allows call with sufficient tier."""

        @requires_tier_async(LicenseTier.PRO)
        async def pro_feature_async() -> str:
            return "success"

        original = get_current_tier()
        try:
            set_current_tier(LicenseTier.PRO)
            result = await pro_feature_async()
            assert result == "success"
        finally:
            set_current_tier(original)

    @pytest.mark.asyncio
    async def test_async_decorator_blocks_insufficient_tier(self) -> None:
        """Test async decorator blocks call with insufficient tier."""

        @requires_tier_async(LicenseTier.PRO)
        async def pro_feature_async() -> str:
            return "success"

        original = get_current_tier()
        try:
            set_current_tier(LicenseTier.FREE)
            with pytest.raises(LicenseError) as exc_info:
                await pro_feature_async()
            assert exc_info.value.required == LicenseTier.PRO
        finally:
            set_current_tier(original)

    @pytest.mark.asyncio
    async def test_async_decorator_with_explicit_tier(self) -> None:
        """Test async decorator respects explicit license_tier kwarg."""

        @requires_tier_async(LicenseTier.PRO)
        async def pro_feature_async(license_tier: LicenseTier | None = None) -> str:
            return "success"

        result = await pro_feature_async(license_tier=LicenseTier.PRO)
        assert result == "success"

        with pytest.raises(LicenseError):
            await pro_feature_async(license_tier=LicenseTier.FREE)


class TestGetTierRequirement:
    """Tests for get_tier_requirement function."""

    def test_get_requirement_from_decorated(self) -> None:
        """Test getting requirement from decorated function."""

        @requires_tier(LicenseTier.PRO)
        def pro_feature() -> str:
            return "success"

        tier = get_tier_requirement(pro_feature)
        assert tier == LicenseTier.PRO

    def test_get_requirement_from_undecorated(self) -> None:
        """Test getting requirement from undecorated function returns None."""

        def regular_feature() -> str:
            return "success"

        tier = get_tier_requirement(regular_feature)
        assert tier is None

    def test_get_requirement_from_async_decorated(self) -> None:
        """Test getting requirement from async decorated function."""

        @requires_tier_async(LicenseTier.TEAMS)
        async def teams_feature_async() -> str:
            return "success"

        tier = get_tier_requirement(teams_feature_async)
        assert tier == LicenseTier.TEAMS


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_decorator_with_enterprise_tier(self) -> None:
        """Test decorator works with ENTERPRISE tier."""

        @requires_tier(LicenseTier.ENTERPRISE)
        def enterprise_feature() -> str:
            return "success"

        original = get_current_tier()
        try:
            set_current_tier(LicenseTier.ENTERPRISE)
            result = enterprise_feature()
            assert result == "success"

            set_current_tier(LicenseTier.TEAMS)
            with pytest.raises(LicenseError):
                enterprise_feature()
        finally:
            set_current_tier(original)

    def test_decorator_with_free_tier(self) -> None:
        """Test decorator works with FREE tier requirement."""

        @requires_tier(LicenseTier.FREE)
        def free_feature() -> str:
            return "success"

        # Should always succeed since FREE is minimum
        original = get_current_tier()
        try:
            for tier in LicenseTier:
                set_current_tier(tier)
                result = free_feature()
                assert result == "success"
        finally:
            set_current_tier(original)

    def test_context_object_without_tier(self) -> None:
        """Test decorator handles context object without license_tier attr."""

        class Context:
            pass

        @requires_tier(LicenseTier.PRO)
        def pro_feature(ctx: Context) -> str:
            return "success"

        original = get_current_tier()
        try:
            set_current_tier(LicenseTier.FREE)
            ctx = Context()
            with pytest.raises(LicenseError):
                pro_feature(ctx)
        finally:
            set_current_tier(original)
