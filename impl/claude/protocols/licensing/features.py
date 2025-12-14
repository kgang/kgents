"""
Feature flag registry and management.

Provides centralized feature flag definitions and tier mappings.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

from protocols.licensing.tiers import LicenseTier, get_tier_config

if TYPE_CHECKING:
    pass


class FeatureFlag(Enum):
    """Feature flags with tier requirements."""

    # FREE tier features
    SOUL_REFLECT = auto()
    STATUS = auto()
    PARSE_BASIC = auto()
    TRACE_BASIC = auto()
    MAP_BASIC = auto()

    # PRO tier features
    SOUL_ADVISE = auto()
    SOUL_CHALLENGE = auto()
    SOUL_EXPLORE = auto()
    SOUL_VIBE = auto()
    SOUL_DRIFT = auto()
    SOUL_TENSE = auto()
    WHATIF = auto()
    SHADOW = auto()
    DIALECTIC = auto()
    PARSE_ALL = auto()
    APPROVE = auto()
    BUDGET_DASHBOARD = auto()
    GARDEN_ADVANCED = auto()
    HYPNAGOGIA = auto()
    WATCHER = auto()
    GATEKEEPER = auto()

    # TEAMS tier features
    TEAM_COLLABORATION = auto()
    SHARED_GARDENS = auto()
    TEAM_ANALYTICS = auto()
    ROLE_BASED_ACCESS = auto()
    AUDIT_LOGS = auto()
    TEAM_DASHBOARD = auto()

    # ENTERPRISE tier features
    CUSTOM_DEPLOYMENT = auto()
    SSO = auto()
    DEDICATED_SUPPORT = auto()
    CUSTOM_INTEGRATIONS = auto()
    WHITE_LABEL = auto()
    UNLIMITED_API = auto()
    CUSTOM_MODELS = auto()
    ON_PREMISE = auto()

    @property
    def feature_key(self) -> str:
        """Get the feature key string (lowercase with underscores)."""
        return self.name.lower()


@dataclass(frozen=True)
class FeatureInfo:
    """Information about a feature."""

    flag: FeatureFlag
    tier: LicenseTier
    description: str
    category: str


class FeatureRegistry:
    """Registry mapping features to tiers and metadata."""

    # Feature tier mappings
    _FEATURE_TIERS: dict[FeatureFlag, LicenseTier] = {
        # FREE
        FeatureFlag.SOUL_REFLECT: LicenseTier.FREE,
        FeatureFlag.STATUS: LicenseTier.FREE,
        FeatureFlag.PARSE_BASIC: LicenseTier.FREE,
        FeatureFlag.TRACE_BASIC: LicenseTier.FREE,
        FeatureFlag.MAP_BASIC: LicenseTier.FREE,
        # PRO
        FeatureFlag.SOUL_ADVISE: LicenseTier.PRO,
        FeatureFlag.SOUL_CHALLENGE: LicenseTier.PRO,
        FeatureFlag.SOUL_EXPLORE: LicenseTier.PRO,
        FeatureFlag.SOUL_VIBE: LicenseTier.PRO,
        FeatureFlag.SOUL_DRIFT: LicenseTier.PRO,
        FeatureFlag.SOUL_TENSE: LicenseTier.PRO,
        FeatureFlag.WHATIF: LicenseTier.PRO,
        FeatureFlag.SHADOW: LicenseTier.PRO,
        FeatureFlag.DIALECTIC: LicenseTier.PRO,
        FeatureFlag.PARSE_ALL: LicenseTier.PRO,
        FeatureFlag.APPROVE: LicenseTier.PRO,
        FeatureFlag.BUDGET_DASHBOARD: LicenseTier.PRO,
        FeatureFlag.GARDEN_ADVANCED: LicenseTier.PRO,
        FeatureFlag.HYPNAGOGIA: LicenseTier.PRO,
        FeatureFlag.WATCHER: LicenseTier.PRO,
        FeatureFlag.GATEKEEPER: LicenseTier.PRO,
        # TEAMS
        FeatureFlag.TEAM_COLLABORATION: LicenseTier.TEAMS,
        FeatureFlag.SHARED_GARDENS: LicenseTier.TEAMS,
        FeatureFlag.TEAM_ANALYTICS: LicenseTier.TEAMS,
        FeatureFlag.ROLE_BASED_ACCESS: LicenseTier.TEAMS,
        FeatureFlag.AUDIT_LOGS: LicenseTier.TEAMS,
        FeatureFlag.TEAM_DASHBOARD: LicenseTier.TEAMS,
        # ENTERPRISE
        FeatureFlag.CUSTOM_DEPLOYMENT: LicenseTier.ENTERPRISE,
        FeatureFlag.SSO: LicenseTier.ENTERPRISE,
        FeatureFlag.DEDICATED_SUPPORT: LicenseTier.ENTERPRISE,
        FeatureFlag.CUSTOM_INTEGRATIONS: LicenseTier.ENTERPRISE,
        FeatureFlag.WHITE_LABEL: LicenseTier.ENTERPRISE,
        FeatureFlag.UNLIMITED_API: LicenseTier.ENTERPRISE,
        FeatureFlag.CUSTOM_MODELS: LicenseTier.ENTERPRISE,
        FeatureFlag.ON_PREMISE: LicenseTier.ENTERPRISE,
    }

    # Feature descriptions
    _FEATURE_DESCRIPTIONS: dict[FeatureFlag, str] = {
        # FREE
        FeatureFlag.SOUL_REFLECT: "Basic soul reflection mode",
        FeatureFlag.STATUS: "Project status queries",
        FeatureFlag.PARSE_BASIC: "Basic code parsing",
        FeatureFlag.TRACE_BASIC: "Basic execution tracing",
        FeatureFlag.MAP_BASIC: "Basic codebase mapping",
        # PRO
        FeatureFlag.SOUL_ADVISE: "Soul advising mode",
        FeatureFlag.SOUL_CHALLENGE: "Soul challenge mode",
        FeatureFlag.SOUL_EXPLORE: "Soul exploration mode",
        FeatureFlag.SOUL_VIBE: "Quick vibe check",
        FeatureFlag.SOUL_DRIFT: "Soul drift tracking",
        FeatureFlag.SOUL_TENSE: "Tension surface analysis",
        FeatureFlag.WHATIF: "Scenario analysis",
        FeatureFlag.SHADOW: "Shadow analysis",
        FeatureFlag.DIALECTIC: "Dialectical reasoning",
        FeatureFlag.PARSE_ALL: "Advanced code parsing",
        FeatureFlag.APPROVE: "Change approval workflows",
        FeatureFlag.BUDGET_DASHBOARD: "Token budget dashboard",
        FeatureFlag.GARDEN_ADVANCED: "Advanced persona garden",
        FeatureFlag.HYPNAGOGIA: "Dream cycle processing",
        FeatureFlag.WATCHER: "File watcher with suggestions",
        FeatureFlag.GATEKEEPER: "Semantic gatekeeper",
        # TEAMS
        FeatureFlag.TEAM_COLLABORATION: "Team collaboration features",
        FeatureFlag.SHARED_GARDENS: "Shared persona gardens",
        FeatureFlag.TEAM_ANALYTICS: "Team usage analytics",
        FeatureFlag.ROLE_BASED_ACCESS: "Role-based access control",
        FeatureFlag.AUDIT_LOGS: "Detailed audit logging",
        FeatureFlag.TEAM_DASHBOARD: "Team dashboard",
        # ENTERPRISE
        FeatureFlag.CUSTOM_DEPLOYMENT: "Custom deployment options",
        FeatureFlag.SSO: "Single sign-on integration",
        FeatureFlag.DEDICATED_SUPPORT: "Dedicated support",
        FeatureFlag.CUSTOM_INTEGRATIONS: "Custom integrations",
        FeatureFlag.WHITE_LABEL: "White label branding",
        FeatureFlag.UNLIMITED_API: "Unlimited API calls",
        FeatureFlag.CUSTOM_MODELS: "Custom model support",
        FeatureFlag.ON_PREMISE: "On-premise deployment",
    }

    # Feature categories
    _FEATURE_CATEGORIES: dict[FeatureFlag, str] = {
        # FREE
        FeatureFlag.SOUL_REFLECT: "soul",
        FeatureFlag.STATUS: "cli",
        FeatureFlag.PARSE_BASIC: "code_analysis",
        FeatureFlag.TRACE_BASIC: "code_analysis",
        FeatureFlag.MAP_BASIC: "code_analysis",
        # PRO
        FeatureFlag.SOUL_ADVISE: "soul",
        FeatureFlag.SOUL_CHALLENGE: "soul",
        FeatureFlag.SOUL_EXPLORE: "soul",
        FeatureFlag.SOUL_VIBE: "soul",
        FeatureFlag.SOUL_DRIFT: "soul",
        FeatureFlag.SOUL_TENSE: "soul",
        FeatureFlag.WHATIF: "analysis",
        FeatureFlag.SHADOW: "analysis",
        FeatureFlag.DIALECTIC: "analysis",
        FeatureFlag.PARSE_ALL: "code_analysis",
        FeatureFlag.APPROVE: "workflow",
        FeatureFlag.BUDGET_DASHBOARD: "monitoring",
        FeatureFlag.GARDEN_ADVANCED: "soul",
        FeatureFlag.HYPNAGOGIA: "soul",
        FeatureFlag.WATCHER: "workflow",
        FeatureFlag.GATEKEEPER: "quality",
        # TEAMS
        FeatureFlag.TEAM_COLLABORATION: "collaboration",
        FeatureFlag.SHARED_GARDENS: "collaboration",
        FeatureFlag.TEAM_ANALYTICS: "monitoring",
        FeatureFlag.ROLE_BASED_ACCESS: "security",
        FeatureFlag.AUDIT_LOGS: "security",
        FeatureFlag.TEAM_DASHBOARD: "monitoring",
        # ENTERPRISE
        FeatureFlag.CUSTOM_DEPLOYMENT: "infrastructure",
        FeatureFlag.SSO: "security",
        FeatureFlag.DEDICATED_SUPPORT: "support",
        FeatureFlag.CUSTOM_INTEGRATIONS: "integration",
        FeatureFlag.WHITE_LABEL: "branding",
        FeatureFlag.UNLIMITED_API: "infrastructure",
        FeatureFlag.CUSTOM_MODELS: "infrastructure",
        FeatureFlag.ON_PREMISE: "infrastructure",
    }

    @classmethod
    def get_tier(cls, feature: FeatureFlag) -> LicenseTier:
        """Get the required tier for a feature."""
        return cls._FEATURE_TIERS[feature]

    @classmethod
    def get_description(cls, feature: FeatureFlag) -> str:
        """Get the description for a feature."""
        return cls._FEATURE_DESCRIPTIONS.get(feature, "No description available")

    @classmethod
    def get_category(cls, feature: FeatureFlag) -> str:
        """Get the category for a feature."""
        return cls._FEATURE_CATEGORIES.get(feature, "uncategorized")

    @classmethod
    def get_info(cls, feature: FeatureFlag) -> FeatureInfo:
        """Get full info for a feature."""
        return FeatureInfo(
            flag=feature,
            tier=cls.get_tier(feature),
            description=cls.get_description(feature),
            category=cls.get_category(feature),
        )

    @classmethod
    def get_features_for_tier(cls, tier: LicenseTier) -> list[FeatureFlag]:
        """Get all features available at a specific tier."""
        return [
            flag
            for flag, required_tier in cls._FEATURE_TIERS.items()
            if required_tier <= tier
        ]

    @classmethod
    def get_features_by_category(cls, category: str) -> list[FeatureFlag]:
        """Get all features in a specific category."""
        return [
            flag for flag, cat in cls._FEATURE_CATEGORIES.items() if cat == category
        ]

    @classmethod
    def is_enabled(cls, feature: FeatureFlag, tier: LicenseTier) -> bool:
        """Check if a feature is enabled for a tier."""
        required_tier = cls.get_tier(feature)
        result: bool = tier >= required_tier
        return result


def get_feature_tier(feature: FeatureFlag) -> LicenseTier:
    """Get the required tier for a feature."""
    return FeatureRegistry.get_tier(feature)


def is_feature_enabled(feature: FeatureFlag, tier: LicenseTier) -> bool:
    """Check if a feature is enabled for a tier."""
    return FeatureRegistry.is_enabled(feature, tier)


def get_tier_features(tier: LicenseTier) -> list[str]:
    """
    Get all feature keys available at a tier.

    Returns feature keys as strings (matching TierConfig.features).
    """
    config = get_tier_config(tier)
    return sorted(config.features)
