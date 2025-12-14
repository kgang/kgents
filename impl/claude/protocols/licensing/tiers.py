"""
License tier definitions and configurations.

Defines the four-tier license model:
- FREE: Community tier with basic features
- PRO: Individual tier with advanced features
- TEAMS: Team tier with collaboration features
- ENTERPRISE: Enterprise tier with full customization
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import FrozenSet


class LicenseTier(Enum):
    """License tiers with ascending privileges."""

    FREE = auto()
    PRO = auto()
    TEAMS = auto()
    ENTERPRISE = auto()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, LicenseTier):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other: object) -> bool:
        if not isinstance(other, LicenseTier):
            return NotImplemented
        return self.value <= other.value

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, LicenseTier):
            return NotImplemented
        return self.value > other.value

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, LicenseTier):
            return NotImplemented
        return self.value >= other.value


@dataclass(frozen=True)
class TierConfig:
    """Configuration for a license tier."""

    tier: LicenseTier
    price_monthly: int  # cents
    features: FrozenSet[str]
    api_calls_per_day: int
    support_level: str
    max_team_members: int = 1
    custom_branding: bool = False
    priority_support: bool = False
    sla_guarantee: bool = False

    def has_feature(self, feature: str) -> bool:
        """Check if this tier includes a specific feature."""
        return feature in self.features

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary representation."""
        return {
            "tier": self.tier.name,
            "price_monthly": self.price_monthly,
            "features": sorted(self.features),
            "api_calls_per_day": self.api_calls_per_day,
            "support_level": self.support_level,
            "max_team_members": self.max_team_members,
            "custom_branding": self.custom_branding,
            "priority_support": self.priority_support,
            "sla_guarantee": self.sla_guarantee,
        }


# Define tier configurations
TIER_CONFIGS: dict[LicenseTier, TierConfig] = {
    LicenseTier.FREE: TierConfig(
        tier=LicenseTier.FREE,
        price_monthly=0,
        features=frozenset(
            {
                "soul_reflect",
                "status",
                "parse_basic",
                "trace_basic",
                "map_basic",
            }
        ),
        api_calls_per_day=100,
        support_level="community",
        max_team_members=1,
        custom_branding=False,
        priority_support=False,
        sla_guarantee=False,
    ),
    LicenseTier.PRO: TierConfig(
        tier=LicenseTier.PRO,
        price_monthly=1900,  # $19
        features=frozenset(
            {
                # FREE features
                "soul_reflect",
                "status",
                "parse_basic",
                "trace_basic",
                "map_basic",
                # PRO-exclusive features
                "soul_advise",
                "soul_challenge",
                "soul_explore",
                "soul_vibe",
                "soul_drift",
                "soul_tense",
                "whatif",
                "shadow",
                "dialectic",
                "parse_all",
                "approve",
                "budget_dashboard",
                "garden_advanced",
                "hypnagogia",
                "watcher",
                "gatekeeper",
            }
        ),
        api_calls_per_day=10000,
        support_level="email",
        max_team_members=1,
        custom_branding=False,
        priority_support=False,
        sla_guarantee=False,
    ),
    LicenseTier.TEAMS: TierConfig(
        tier=LicenseTier.TEAMS,
        price_monthly=9900,  # $99
        features=frozenset(
            {
                # PRO features
                "soul_reflect",
                "soul_advise",
                "soul_challenge",
                "soul_explore",
                "soul_vibe",
                "soul_drift",
                "soul_tense",
                "whatif",
                "shadow",
                "dialectic",
                "parse_all",
                "approve",
                "budget_dashboard",
                "garden_advanced",
                "hypnagogia",
                "watcher",
                "gatekeeper",
                "status",
                "parse_basic",
                "trace_basic",
                "map_basic",
                # TEAMS-exclusive features
                "team_collaboration",
                "shared_gardens",
                "team_analytics",
                "role_based_access",
                "audit_logs",
                "team_dashboard",
            }
        ),
        api_calls_per_day=100000,
        support_level="priority",
        max_team_members=10,
        custom_branding=False,
        priority_support=True,
        sla_guarantee=False,
    ),
    LicenseTier.ENTERPRISE: TierConfig(
        tier=LicenseTier.ENTERPRISE,
        price_monthly=-1,  # Custom pricing
        features=frozenset(
            {
                # TEAMS features
                "soul_reflect",
                "soul_advise",
                "soul_challenge",
                "soul_explore",
                "soul_vibe",
                "soul_drift",
                "soul_tense",
                "whatif",
                "shadow",
                "dialectic",
                "parse_all",
                "approve",
                "budget_dashboard",
                "garden_advanced",
                "hypnagogia",
                "watcher",
                "gatekeeper",
                "status",
                "parse_basic",
                "trace_basic",
                "map_basic",
                "team_collaboration",
                "shared_gardens",
                "team_analytics",
                "role_based_access",
                "audit_logs",
                "team_dashboard",
                # ENTERPRISE-exclusive features
                "custom_deployment",
                "sso",
                "dedicated_support",
                "custom_integrations",
                "white_label",
                "unlimited_api",
                "custom_models",
                "on_premise",
            }
        ),
        api_calls_per_day=-1,  # Unlimited
        support_level="dedicated",
        max_team_members=-1,  # Unlimited
        custom_branding=True,
        priority_support=True,
        sla_guarantee=True,
    ),
}


def get_tier_config(tier: LicenseTier) -> TierConfig:
    """Get the configuration for a specific tier."""
    return TIER_CONFIGS[tier]


def compare_tiers(tier1: LicenseTier, tier2: LicenseTier) -> int:
    """
    Compare two tiers.

    Returns:
        -1 if tier1 < tier2
        0 if tier1 == tier2
        1 if tier1 > tier2
    """
    if tier1.value < tier2.value:
        return -1
    elif tier1.value > tier2.value:
        return 1
    else:
        return 0
