"""
Tests for feature flag registry and management.
"""

import pytest

from protocols.licensing.features import (
    FeatureFlag,
    FeatureInfo,
    FeatureRegistry,
    get_feature_tier,
    get_tier_features,
    is_feature_enabled,
)
from protocols.licensing.tiers import LicenseTier


class TestFeatureFlag:
    """Tests for FeatureFlag enum."""

    def test_feature_key_property(self) -> None:
        """Test feature_key property returns lowercase name."""
        assert FeatureFlag.SOUL_REFLECT.feature_key == "soul_reflect"
        assert FeatureFlag.SOUL_ADVISE.feature_key == "soul_advise"
        assert FeatureFlag.TEAM_COLLABORATION.feature_key == "team_collaboration"

    def test_all_flags_have_unique_values(self) -> None:
        """Test all feature flags have unique values."""
        values = [flag.value for flag in FeatureFlag]
        assert len(values) == len(set(values))

    def test_flag_count(self) -> None:
        """Test we have expected number of features."""
        flags = list(FeatureFlag)
        # Should have 30+ features across all tiers
        assert len(flags) >= 30


class TestFeatureRegistry:
    """Tests for FeatureRegistry class."""

    def test_get_tier_free_features(self) -> None:
        """Test getting tier for FREE features."""
        assert FeatureRegistry.get_tier(FeatureFlag.SOUL_REFLECT) == LicenseTier.FREE
        assert FeatureRegistry.get_tier(FeatureFlag.STATUS) == LicenseTier.FREE
        assert FeatureRegistry.get_tier(FeatureFlag.PARSE_BASIC) == LicenseTier.FREE

    def test_get_tier_pro_features(self) -> None:
        """Test getting tier for PRO features."""
        assert FeatureRegistry.get_tier(FeatureFlag.SOUL_ADVISE) == LicenseTier.PRO
        assert FeatureRegistry.get_tier(FeatureFlag.SOUL_CHALLENGE) == LicenseTier.PRO
        assert FeatureRegistry.get_tier(FeatureFlag.WHATIF) == LicenseTier.PRO

    def test_get_tier_teams_features(self) -> None:
        """Test getting tier for TEAMS features."""
        assert FeatureRegistry.get_tier(FeatureFlag.TEAM_COLLABORATION) == LicenseTier.TEAMS
        assert FeatureRegistry.get_tier(FeatureFlag.SHARED_GARDENS) == LicenseTier.TEAMS

    def test_get_tier_enterprise_features(self) -> None:
        """Test getting tier for ENTERPRISE features."""
        assert FeatureRegistry.get_tier(FeatureFlag.CUSTOM_DEPLOYMENT) == LicenseTier.ENTERPRISE
        assert FeatureRegistry.get_tier(FeatureFlag.SSO) == LicenseTier.ENTERPRISE

    def test_get_description(self) -> None:
        """Test getting feature descriptions."""
        desc = FeatureRegistry.get_description(FeatureFlag.SOUL_REFLECT)
        assert len(desc) > 0
        assert isinstance(desc, str)

    def test_get_category(self) -> None:
        """Test getting feature categories."""
        assert FeatureRegistry.get_category(FeatureFlag.SOUL_REFLECT) == "soul"
        assert FeatureRegistry.get_category(FeatureFlag.STATUS) == "cli"
        assert FeatureRegistry.get_category(FeatureFlag.TEAM_COLLABORATION) == "collaboration"

    def test_get_info(self) -> None:
        """Test getting full feature info."""
        info = FeatureRegistry.get_info(FeatureFlag.SOUL_ADVISE)
        assert info.flag == FeatureFlag.SOUL_ADVISE
        assert info.tier == LicenseTier.PRO
        assert len(info.description) > 0
        assert info.category == "soul"

    def test_get_features_for_tier_free(self) -> None:
        """Test getting features for FREE tier."""
        features = FeatureRegistry.get_features_for_tier(LicenseTier.FREE)
        assert FeatureFlag.SOUL_REFLECT in features
        assert FeatureFlag.STATUS in features
        # Should not include PRO features
        assert FeatureFlag.SOUL_ADVISE not in features

    def test_get_features_for_tier_pro(self) -> None:
        """Test getting features for PRO tier."""
        features = FeatureRegistry.get_features_for_tier(LicenseTier.PRO)
        # Should include FREE features
        assert FeatureFlag.SOUL_REFLECT in features
        # Should include PRO features
        assert FeatureFlag.SOUL_ADVISE in features
        assert FeatureFlag.WHATIF in features
        # Should not include TEAMS features
        assert FeatureFlag.TEAM_COLLABORATION not in features

    def test_get_features_for_tier_teams(self) -> None:
        """Test getting features for TEAMS tier."""
        features = FeatureRegistry.get_features_for_tier(LicenseTier.TEAMS)
        # Should include PRO features
        assert FeatureFlag.SOUL_ADVISE in features
        # Should include TEAMS features
        assert FeatureFlag.TEAM_COLLABORATION in features
        # Should not include ENTERPRISE features
        assert FeatureFlag.CUSTOM_DEPLOYMENT not in features

    def test_get_features_for_tier_enterprise(self) -> None:
        """Test getting features for ENTERPRISE tier."""
        features = FeatureRegistry.get_features_for_tier(LicenseTier.ENTERPRISE)
        # Should include all features
        assert FeatureFlag.SOUL_REFLECT in features
        assert FeatureFlag.SOUL_ADVISE in features
        assert FeatureFlag.TEAM_COLLABORATION in features
        assert FeatureFlag.CUSTOM_DEPLOYMENT in features

    def test_get_features_by_category_soul(self) -> None:
        """Test getting features by soul category."""
        features = FeatureRegistry.get_features_by_category("soul")
        assert FeatureFlag.SOUL_REFLECT in features
        assert FeatureFlag.SOUL_ADVISE in features
        assert FeatureFlag.SOUL_VIBE in features
        # Should not include non-soul features
        assert FeatureFlag.STATUS not in features

    def test_get_features_by_category_collaboration(self) -> None:
        """Test getting features by collaboration category."""
        features = FeatureRegistry.get_features_by_category("collaboration")
        assert FeatureFlag.TEAM_COLLABORATION in features
        assert FeatureFlag.SHARED_GARDENS in features

    def test_is_enabled_sufficient_tier(self) -> None:
        """Test is_enabled returns True for sufficient tier."""
        assert FeatureRegistry.is_enabled(FeatureFlag.SOUL_REFLECT, LicenseTier.FREE)
        assert FeatureRegistry.is_enabled(FeatureFlag.SOUL_REFLECT, LicenseTier.PRO)
        assert FeatureRegistry.is_enabled(FeatureFlag.SOUL_ADVISE, LicenseTier.PRO)
        assert FeatureRegistry.is_enabled(FeatureFlag.SOUL_ADVISE, LicenseTier.ENTERPRISE)

    def test_is_enabled_insufficient_tier(self) -> None:
        """Test is_enabled returns False for insufficient tier."""
        assert not FeatureRegistry.is_enabled(FeatureFlag.SOUL_ADVISE, LicenseTier.FREE)
        assert not FeatureRegistry.is_enabled(FeatureFlag.TEAM_COLLABORATION, LicenseTier.PRO)
        assert not FeatureRegistry.is_enabled(FeatureFlag.CUSTOM_DEPLOYMENT, LicenseTier.TEAMS)


class TestFeatureInfo:
    """Tests for FeatureInfo dataclass."""

    def test_feature_info_creation(self) -> None:
        """Test creating FeatureInfo."""
        info = FeatureInfo(
            flag=FeatureFlag.SOUL_ADVISE,
            tier=LicenseTier.PRO,
            description="Soul advising mode",
            category="soul",
        )
        assert info.flag == FeatureFlag.SOUL_ADVISE
        assert info.tier == LicenseTier.PRO
        assert info.description == "Soul advising mode"
        assert info.category == "soul"

    def test_feature_info_immutability(self) -> None:
        """Test FeatureInfo is immutable (frozen)."""
        info = FeatureInfo(
            flag=FeatureFlag.SOUL_ADVISE,
            tier=LicenseTier.PRO,
            description="Test",
            category="soul",
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            info.tier = LicenseTier.FREE  # type: ignore[misc]


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_feature_tier(self) -> None:
        """Test get_feature_tier function."""
        assert get_feature_tier(FeatureFlag.SOUL_REFLECT) == LicenseTier.FREE
        assert get_feature_tier(FeatureFlag.SOUL_ADVISE) == LicenseTier.PRO
        assert get_feature_tier(FeatureFlag.TEAM_COLLABORATION) == LicenseTier.TEAMS
        assert get_feature_tier(FeatureFlag.CUSTOM_DEPLOYMENT) == LicenseTier.ENTERPRISE

    def test_is_feature_enabled(self) -> None:
        """Test is_feature_enabled function."""
        assert is_feature_enabled(FeatureFlag.SOUL_REFLECT, LicenseTier.FREE)
        assert is_feature_enabled(FeatureFlag.SOUL_ADVISE, LicenseTier.PRO)
        assert not is_feature_enabled(FeatureFlag.SOUL_ADVISE, LicenseTier.FREE)

    def test_get_tier_features(self) -> None:
        """Test get_tier_features function."""
        features = get_tier_features(LicenseTier.FREE)
        assert isinstance(features, list)
        assert "soul_reflect" in features
        assert "status" in features

        pro_features = get_tier_features(LicenseTier.PRO)
        assert "soul_advise" in pro_features
        assert "soul_reflect" in pro_features


class TestFeatureTierConsistency:
    """Tests for consistency between FeatureRegistry and TierConfig."""

    def test_registry_matches_tier_config(self) -> None:
        """Test FeatureRegistry matches TierConfig feature sets."""
        from protocols.licensing.tiers import TIER_CONFIGS

        for tier in LicenseTier:
            config = TIER_CONFIGS[tier]
            registry_features = FeatureRegistry.get_features_for_tier(tier)

            # Convert registry features to keys
            registry_keys = {f.feature_key for f in registry_features}

            # Config features should be a subset of registry (registry may have more)
            for feature_key in config.features:
                assert feature_key in registry_keys, (
                    f"Feature {feature_key} in tier {tier.name} config but not in registry"
                )

    def test_all_features_have_tier(self) -> None:
        """Test all features have a tier mapping."""
        for flag in FeatureFlag:
            tier = FeatureRegistry.get_tier(flag)
            assert isinstance(tier, LicenseTier)

    def test_all_features_have_description(self) -> None:
        """Test all features have descriptions."""
        for flag in FeatureFlag:
            desc = FeatureRegistry.get_description(flag)
            assert isinstance(desc, str)
            assert len(desc) > 0

    def test_all_features_have_category(self) -> None:
        """Test all features have categories."""
        for flag in FeatureFlag:
            category = FeatureRegistry.get_category(flag)
            assert isinstance(category, str)
            assert len(category) > 0


class TestCategoryGroups:
    """Tests for feature category groupings."""

    def test_soul_category_features(self) -> None:
        """Test soul category has expected features."""
        soul_features = FeatureRegistry.get_features_by_category("soul")
        assert len(soul_features) >= 5
        assert FeatureFlag.SOUL_REFLECT in soul_features
        assert FeatureFlag.SOUL_ADVISE in soul_features

    def test_cli_category_features(self) -> None:
        """Test cli category has features."""
        cli_features = FeatureRegistry.get_features_by_category("cli")
        assert len(cli_features) > 0
        assert FeatureFlag.STATUS in cli_features

    def test_code_analysis_category_features(self) -> None:
        """Test code_analysis category has features."""
        analysis_features = FeatureRegistry.get_features_by_category("code_analysis")
        assert len(analysis_features) > 0
        assert FeatureFlag.PARSE_BASIC in analysis_features

    def test_security_category_features(self) -> None:
        """Test security category has features."""
        security_features = FeatureRegistry.get_features_by_category("security")
        assert len(security_features) > 0
        # Should include TEAMS and ENTERPRISE security features
        assert FeatureFlag.ROLE_BASED_ACCESS in security_features
        assert FeatureFlag.SSO in security_features
