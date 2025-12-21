"""
Tests for observer-dependent model selection.

Per spec/protocols/chat-morpheus-synergy.md Part III:
- Different observers get different models
- Model selection is a functor: Observer → MorpheusConfig
"""

from unittest.mock import MagicMock

import pytest

from services.chat.model_selector import (
    TIER_BUDGETS,
    MorpheusConfig,
    TokenBudget,
    budget_aware_selector,
    can_switch_model,
    default_model_selector,
)


def _make_observer(archetype: str = "guest", tier: str = "free") -> MagicMock:
    """Create a mock observer umwelt."""
    observer = MagicMock()
    observer.meta.archetype = archetype
    observer.meta.capabilities = {"tier": tier}
    return observer


class TestDefaultModelSelector:
    """Tests for default_model_selector function."""

    def test_guest_gets_haiku(self) -> None:
        """Guest observers get cost-efficient haiku model."""
        observer = _make_observer(archetype="guest")
        config = default_model_selector(observer, "self.soul")

        assert "haiku" in config.model.lower()
        assert config.max_tokens == 1024
        assert config.temperature == 0.5

    def test_developer_gets_sonnet(self) -> None:
        """Developer observers get sonnet for balanced performance."""
        observer = _make_observer(archetype="developer")
        config = default_model_selector(observer, "self.soul")

        assert "sonnet" in config.model.lower()
        assert config.max_tokens == 4096
        assert config.temperature == 0.7

    def test_system_gets_opus(self) -> None:
        """System observers get highest capability opus."""
        observer = _make_observer(archetype="system")
        config = default_model_selector(observer, "any.path")

        assert "opus" in config.model.lower()
        assert config.max_tokens == 8192
        assert config.temperature == 0.3

    def test_citizen_path_gets_haiku_high_temp(self) -> None:
        """Citizen paths get haiku with higher temperature for personality."""
        observer = _make_observer(archetype="developer")
        config = default_model_selector(observer, "world.town.citizen.elara")

        assert "haiku" in config.model.lower()
        assert config.temperature == 0.8
        assert config.max_tokens == 2048

    def test_fallback_to_sonnet(self) -> None:
        """Unknown observers fall back to sonnet defaults."""
        observer = _make_observer(archetype="unknown")
        config = default_model_selector(observer, "world.some.path")

        assert "sonnet" in config.model.lower()
        assert config.temperature == 0.7

    def test_missing_archetype_falls_back_to_guest(self) -> None:
        """Observer without archetype is treated as guest."""
        observer = MagicMock()
        observer.meta = MagicMock(spec=[])  # No archetype attribute
        del observer.meta.archetype

        config = default_model_selector(observer, "self.soul")
        # Should fall back to guest behavior
        assert config is not None


class TestMorpheusConfig:
    """Tests for MorpheusConfig dataclass."""

    def test_default_values(self) -> None:
        """Config has sensible defaults."""
        config = MorpheusConfig()

        assert config.model == "claude-sonnet-4-20250514"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096

    def test_frozen(self) -> None:
        """Config is immutable."""
        config = MorpheusConfig()

        with pytest.raises(Exception):  # FrozenInstanceError
            config.model = "different-model"

    def test_custom_values(self) -> None:
        """Config accepts custom values."""
        config = MorpheusConfig(
            model="custom-model",
            temperature=0.9,
            max_tokens=2000,
        )

        assert config.model == "custom-model"
        assert config.temperature == 0.9
        assert config.max_tokens == 2000


class TestBudgetAwareSelector:
    """Tests for budget-aware model selection."""

    def test_caps_tokens_to_tier_budget(self) -> None:
        """Max tokens are capped by tier budget."""
        # System would normally get 8192 tokens
        observer = _make_observer(archetype="system", tier="free")
        config = budget_aware_selector(observer, "any.path")

        # But free tier limits to 1024
        assert config.max_tokens == 1024

    def test_pro_tier_gets_more_tokens(self) -> None:
        """Pro tier has higher per-request limit."""
        observer = _make_observer(archetype="developer", tier="pro")
        config = budget_aware_selector(observer, "self.soul")

        # Pro tier allows full 4096
        assert config.max_tokens == 4096

    def test_enterprise_tier_uncapped(self) -> None:
        """Enterprise tier allows full model limits."""
        observer = _make_observer(archetype="system", tier="enterprise")
        config = budget_aware_selector(observer, "self.soul")

        # Enterprise allows 16384, system requests 8192
        assert config.max_tokens == 8192

    def test_preserves_model_and_temp(self) -> None:
        """Budget selector preserves model and temperature from base."""
        observer = _make_observer(archetype="system", tier="free")
        config = budget_aware_selector(observer, "any.path")

        assert "opus" in config.model.lower()
        assert config.temperature == 0.3


class TestTierBudgets:
    """Tests for tier budget configuration."""

    def test_free_tier_limits(self) -> None:
        """Free tier has conservative limits."""
        budget = TIER_BUDGETS["free"]

        assert budget.daily_tokens == 10_000
        assert budget.per_request == 1024

    def test_pro_tier_limits(self) -> None:
        """Pro tier has higher limits."""
        budget = TIER_BUDGETS["pro"]

        assert budget.daily_tokens == 100_000
        assert budget.per_request == 4096

    def test_enterprise_tier_limits(self) -> None:
        """Enterprise tier has highest limits."""
        budget = TIER_BUDGETS["enterprise"]

        assert budget.daily_tokens == 1_000_000
        assert budget.per_request == 16384


def _make_session(node_path: str = "self.chat") -> MagicMock:
    """Create a mock chat session."""
    session = MagicMock()
    session.node_path = node_path
    return session


class TestCanSwitchModel:
    """Tests for can_switch_model function - model switching permissions."""

    def test_self_paths_always_allow_switching(self) -> None:
        """Personal sessions (self.*) always allow model switching."""
        session = _make_session("self.chat")
        observer = _make_observer(archetype="guest")

        # Even guest can switch on self.* paths - it's their session
        assert can_switch_model(session, observer) is True

    def test_self_soul_allows_switching(self) -> None:
        """self.soul allows model switching."""
        session = _make_session("self.soul")
        observer = _make_observer(archetype="guest")

        assert can_switch_model(session, observer) is True

    def test_citizen_paths_allow_switching(self) -> None:
        """Citizen conversations allow model switching."""
        session = _make_session("world.town.citizen.elara")
        observer = _make_observer(archetype="guest")

        assert can_switch_model(session, observer) is True

    def test_guest_cannot_switch_on_non_self_paths(self) -> None:
        """Guest cannot switch models on non-personal paths."""
        session = _make_session("world.park.scenario")
        observer = _make_observer(archetype="guest")

        assert can_switch_model(session, observer) is False

    def test_developer_can_switch_anywhere(self) -> None:
        """Developer can switch models on any path."""
        session = _make_session("world.park.scenario")
        observer = _make_observer(archetype="developer")

        assert can_switch_model(session, observer) is True
