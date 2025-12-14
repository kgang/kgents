"""
Tests for license tier definitions and configurations.
"""

import pytest
from protocols.licensing.tiers import (
    TIER_CONFIGS,
    LicenseTier,
    TierConfig,
    compare_tiers,
    get_tier_config,
)


class TestLicenseTier:
    """Tests for LicenseTier enum."""

    def test_tier_ordering(self) -> None:
        """Test that tiers have correct ordering."""
        assert LicenseTier.FREE < LicenseTier.PRO
        assert LicenseTier.PRO < LicenseTier.TEAMS
        assert LicenseTier.TEAMS < LicenseTier.ENTERPRISE

    def test_tier_comparison_ge(self) -> None:
        """Test >= comparison operator."""
        assert LicenseTier.PRO >= LicenseTier.FREE
        assert LicenseTier.PRO >= LicenseTier.PRO
        assert not (LicenseTier.FREE >= LicenseTier.PRO)

    def test_tier_comparison_le(self) -> None:
        """Test <= comparison operator."""
        assert LicenseTier.FREE <= LicenseTier.PRO
        assert LicenseTier.PRO <= LicenseTier.PRO
        assert not (LicenseTier.PRO <= LicenseTier.FREE)

    def test_tier_comparison_gt(self) -> None:
        """Test > comparison operator."""
        assert LicenseTier.PRO > LicenseTier.FREE
        assert not (LicenseTier.FREE > LicenseTier.PRO)
        assert not (LicenseTier.PRO > LicenseTier.PRO)

    def test_tier_comparison_lt(self) -> None:
        """Test < comparison operator."""
        assert LicenseTier.FREE < LicenseTier.PRO
        assert not (LicenseTier.PRO < LicenseTier.FREE)
        assert not (LicenseTier.PRO < LicenseTier.PRO)

    def test_tier_comparison_invalid_type(self) -> None:
        """Test comparison with invalid type returns NotImplemented."""
        with pytest.raises(TypeError):
            _ = LicenseTier.FREE < "FREE"


class TestTierConfig:
    """Tests for TierConfig dataclass."""

    def test_free_config(self) -> None:
        """Test FREE tier configuration."""
        config = TIER_CONFIGS[LicenseTier.FREE]
        assert config.tier == LicenseTier.FREE
        assert config.price_monthly == 0
        assert config.api_calls_per_day == 100
        assert config.support_level == "community"
        assert config.max_team_members == 1
        assert not config.custom_branding
        assert not config.priority_support
        assert not config.sla_guarantee

    def test_pro_config(self) -> None:
        """Test PRO tier configuration."""
        config = TIER_CONFIGS[LicenseTier.PRO]
        assert config.tier == LicenseTier.PRO
        assert config.price_monthly == 1900
        assert config.api_calls_per_day == 10000
        assert config.support_level == "email"
        assert config.max_team_members == 1
        assert not config.custom_branding
        assert not config.priority_support

    def test_teams_config(self) -> None:
        """Test TEAMS tier configuration."""
        config = TIER_CONFIGS[LicenseTier.TEAMS]
        assert config.tier == LicenseTier.TEAMS
        assert config.price_monthly == 9900
        assert config.api_calls_per_day == 100000
        assert config.support_level == "priority"
        assert config.max_team_members == 10
        assert config.priority_support

    def test_enterprise_config(self) -> None:
        """Test ENTERPRISE tier configuration."""
        config = TIER_CONFIGS[LicenseTier.ENTERPRISE]
        assert config.tier == LicenseTier.ENTERPRISE
        assert config.price_monthly == -1  # Custom pricing
        assert config.api_calls_per_day == -1  # Unlimited
        assert config.support_level == "dedicated"
        assert config.max_team_members == -1  # Unlimited
        assert config.custom_branding
        assert config.priority_support
        assert config.sla_guarantee

    def test_has_feature_positive(self) -> None:
        """Test has_feature returns True for included features."""
        config = TIER_CONFIGS[LicenseTier.PRO]
        assert config.has_feature("soul_advise")
        assert config.has_feature("soul_challenge")
        assert config.has_feature("whatif")

    def test_has_feature_negative(self) -> None:
        """Test has_feature returns False for excluded features."""
        config = TIER_CONFIGS[LicenseTier.FREE]
        assert not config.has_feature("soul_advise")
        assert not config.has_feature("whatif")

    def test_to_dict(self) -> None:
        """Test to_dict serialization."""
        config = TIER_CONFIGS[LicenseTier.PRO]
        data = config.to_dict()
        assert data["tier"] == "PRO"
        assert data["price_monthly"] == 1900
        assert isinstance(data["features"], list)
        assert "soul_advise" in data["features"]

    def test_config_immutability(self) -> None:
        """Test that TierConfig is immutable (frozen)."""
        config = TIER_CONFIGS[LicenseTier.PRO]
        with pytest.raises(Exception):  # FrozenInstanceError
            config.price_monthly = 2000


class TestTierFeatures:
    """Tests for feature sets across tiers."""

    def test_free_features(self) -> None:
        """Test FREE tier has expected features."""
        config = TIER_CONFIGS[LicenseTier.FREE]
        assert "soul_reflect" in config.features
        assert "status" in config.features
        assert "parse_basic" in config.features

    def test_pro_includes_free(self) -> None:
        """Test PRO tier includes all FREE features."""
        free_features = TIER_CONFIGS[LicenseTier.FREE].features
        pro_features = TIER_CONFIGS[LicenseTier.PRO].features
        assert free_features.issubset(pro_features)

    def test_teams_includes_pro(self) -> None:
        """Test TEAMS tier includes all PRO features."""
        pro_features = TIER_CONFIGS[LicenseTier.PRO].features
        teams_features = TIER_CONFIGS[LicenseTier.TEAMS].features
        assert pro_features.issubset(teams_features)

    def test_enterprise_includes_teams(self) -> None:
        """Test ENTERPRISE tier includes all TEAMS features."""
        teams_features = TIER_CONFIGS[LicenseTier.TEAMS].features
        enterprise_features = TIER_CONFIGS[LicenseTier.ENTERPRISE].features
        assert teams_features.issubset(enterprise_features)

    def test_tier_exclusive_features(self) -> None:
        """Test each tier has exclusive features."""
        free = TIER_CONFIGS[LicenseTier.FREE].features
        pro = TIER_CONFIGS[LicenseTier.PRO].features
        teams = TIER_CONFIGS[LicenseTier.TEAMS].features
        enterprise = TIER_CONFIGS[LicenseTier.ENTERPRISE].features

        # PRO has features not in FREE
        pro_exclusive = pro - free
        assert len(pro_exclusive) > 0
        assert "soul_advise" in pro_exclusive

        # TEAMS has features not in PRO
        teams_exclusive = teams - pro
        assert len(teams_exclusive) > 0
        assert "team_collaboration" in teams_exclusive

        # ENTERPRISE has features not in TEAMS
        enterprise_exclusive = enterprise - teams
        assert len(enterprise_exclusive) > 0
        assert "custom_deployment" in enterprise_exclusive


class TestGetTierConfig:
    """Tests for get_tier_config function."""

    def test_get_free_config(self) -> None:
        """Test getting FREE tier config."""
        config = get_tier_config(LicenseTier.FREE)
        assert config.tier == LicenseTier.FREE

    def test_get_pro_config(self) -> None:
        """Test getting PRO tier config."""
        config = get_tier_config(LicenseTier.PRO)
        assert config.tier == LicenseTier.PRO

    def test_all_tiers_have_config(self) -> None:
        """Test all tiers have a configuration."""
        for tier in LicenseTier:
            config = get_tier_config(tier)
            assert config.tier == tier


class TestCompareTiers:
    """Tests for compare_tiers function."""

    def test_compare_less_than(self) -> None:
        """Test comparison returns -1 for less than."""
        result = compare_tiers(LicenseTier.FREE, LicenseTier.PRO)
        assert result == -1

    def test_compare_equal(self) -> None:
        """Test comparison returns 0 for equal."""
        result = compare_tiers(LicenseTier.PRO, LicenseTier.PRO)
        assert result == 0

    def test_compare_greater_than(self) -> None:
        """Test comparison returns 1 for greater than."""
        result = compare_tiers(LicenseTier.ENTERPRISE, LicenseTier.TEAMS)
        assert result == 1
