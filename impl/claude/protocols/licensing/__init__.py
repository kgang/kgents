"""
License tier infrastructure for kgents.

Provides tier-based feature gating, license management, and feature flags.
"""

from protocols.licensing.features import (
    FeatureFlag,
    FeatureRegistry,
    get_feature_tier,
    is_feature_enabled,
)
from protocols.licensing.gate import (
    LicenseError,
    check_tier,
    get_current_tier,
    requires_tier,
)
from protocols.licensing.tiers import (
    TIER_CONFIGS,
    LicenseTier,
    TierConfig,
    get_tier_config,
)

__all__ = [
    # Tiers
    "LicenseTier",
    "TierConfig",
    "TIER_CONFIGS",
    "get_tier_config",
    # Gate
    "LicenseError",
    "requires_tier",
    "check_tier",
    "get_current_tier",
    # Features
    "FeatureFlag",
    "FeatureRegistry",
    "is_feature_enabled",
    "get_feature_tier",
]
