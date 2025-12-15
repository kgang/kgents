"""Tests for unified model router (Track B)."""

from agents.town.model_router import (
    DEGRADATION_CHAIN,
    LOD_MODELS,
    ModelName,
    ModelSelection,
    degrade_model,
    get_model_for_lod,
    get_model_for_operation,
    select_model,
)


class TestModelRouter:
    """Test unified model routing logic."""

    def test_select_model_lod0_cached(self) -> None:
        """LOD 0 returns cached model."""
        selection = select_model(action="lod0", tier="TOURIST")
        assert selection.model == "cached"

    def test_select_model_lod3_haiku(self) -> None:
        """LOD 3 returns haiku model."""
        selection = select_model(action="lod3", tier="TOURIST")
        assert selection.model == "haiku"

    def test_select_model_lod5_opus(self) -> None:
        """LOD 5 returns opus for FOUNDER tier."""
        selection = select_model(action="lod5", tier="FOUNDER")
        assert selection.model == "opus"
        assert not selection.degraded

    def test_select_model_lod5_degraded_tourist(self) -> None:
        """LOD 5 degrades to haiku for TOURIST tier."""
        selection = select_model(action="lod5", tier="TOURIST")
        assert selection.model == "haiku"
        assert selection.degraded

    def test_select_model_lod5_degraded_resident(self) -> None:
        """LOD 5 degrades to haiku for RESIDENT tier."""
        selection = select_model(action="lod5", tier="RESIDENT")
        assert selection.model == "haiku"
        assert selection.degraded

    def test_select_model_lod5_degraded_citizen(self) -> None:
        """LOD 5 degrades to sonnet for CITIZEN tier."""
        selection = select_model(action="lod5", tier="CITIZEN")
        assert selection.model == "sonnet"
        assert selection.degraded

    def test_select_model_operation_greet(self) -> None:
        """Greet operation uses haiku."""
        selection = select_model(action="greet", tier="TOURIST")
        assert selection.model == "haiku"

    def test_select_model_operation_trade(self) -> None:
        """Trade operation uses sonnet for appropriate tier."""
        selection = select_model(action="trade", tier="CITIZEN")
        assert selection.model == "sonnet"

    def test_select_model_operation_trade_degraded(self) -> None:
        """Trade operation degrades for TOURIST tier."""
        selection = select_model(action="trade", tier="TOURIST")
        assert selection.model == "haiku"
        assert selection.degraded

    def test_select_model_inhabit_session(self) -> None:
        """INHABIT session uses haiku."""
        selection = select_model(action="inhabit_session", tier="RESIDENT")
        assert selection.model == "haiku"

    def test_select_model_inhabit_force(self) -> None:
        """INHABIT force uses sonnet for CITIZEN tier."""
        selection = select_model(action="inhabit_force", tier="CITIZEN")
        assert selection.model == "sonnet"

    def test_select_model_branch_none(self) -> None:
        """Branch actions need no model."""
        selection = select_model(action="branch_create", tier="CITIZEN")
        assert selection.model == "none"

    def test_select_model_cached_flag(self) -> None:
        """Cache hit returns cached model."""
        selection = select_model(action="lod5", tier="FOUNDER", is_cached=True)
        assert selection.model == "cached"
        assert "Cache hit" in selection.reason

    def test_select_model_credit_degradation(self) -> None:
        """Low credits causes degradation."""
        selection = select_model(action="lod5", tier="FOUNDER", remaining_credits=50)
        assert selection.model == "haiku"
        assert selection.degraded

    def test_select_model_credit_degradation_medium(self) -> None:
        """Medium credits degrades to sonnet."""
        selection = select_model(action="lod5", tier="FOUNDER", remaining_credits=200)
        assert selection.model == "sonnet"
        assert selection.degraded


class TestDegradation:
    """Test model degradation chain."""

    def test_degrade_opus_to_sonnet(self) -> None:
        """Opus degrades to sonnet."""
        assert degrade_model(ModelName.OPUS) == ModelName.SONNET

    def test_degrade_sonnet_to_haiku(self) -> None:
        """Sonnet degrades to haiku."""
        assert degrade_model(ModelName.SONNET) == ModelName.HAIKU

    def test_degrade_haiku_to_template(self) -> None:
        """Haiku degrades to template."""
        assert degrade_model(ModelName.HAIKU) == ModelName.TEMPLATE

    def test_degrade_template_stays_template(self) -> None:
        """Template can't degrade further."""
        assert degrade_model(ModelName.TEMPLATE) == ModelName.TEMPLATE


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_get_model_for_lod(self) -> None:
        """get_model_for_lod returns correct models."""
        assert get_model_for_lod(0) == "cached"
        assert get_model_for_lod(1) == "haiku"
        assert get_model_for_lod(4) == "sonnet"
        assert get_model_for_lod(5) == "opus"

    def test_get_model_for_operation(self) -> None:
        """get_model_for_operation returns correct models."""
        assert get_model_for_operation("greet") == "haiku"
        assert get_model_for_operation("trade") == "sonnet"
        assert get_model_for_operation("unknown") == "haiku"


class TestConstants:
    """Test constants are properly defined."""

    def test_lod_models_complete(self) -> None:
        """All 6 LOD levels defined."""
        assert len(LOD_MODELS) == 6
        assert all(lod in LOD_MODELS for lod in range(6))

    def test_degradation_chain_order(self) -> None:
        """Degradation chain is in correct order."""
        assert DEGRADATION_CHAIN == [
            ModelName.OPUS,
            ModelName.SONNET,
            ModelName.HAIKU,
            ModelName.TEMPLATE,
        ]


def test_count_verification() -> None:
    """Verify test count for CI tracking."""
    import ast
    import inspect

    source = inspect.getsourcefile(TestModelRouter)
    assert source is not None
    with open(source) as f:
        tree = ast.parse(f.read())

    count = sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    )
    # 15 tests in TestModelRouter + 4 in TestDegradation + 2 in TestConvenienceFunctions
    # + 2 in TestConstants + this test = 24
    assert count >= 24, f"Expected at least 24 tests, found {count}"
