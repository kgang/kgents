# License Infrastructure Usage Guide

## Overview

The licensing infrastructure provides tier-based feature gating for kgents with four tiers:
- **FREE**: Community tier ($0/mo, 100 API calls/day)
- **PRO**: Individual tier ($19/mo, 10k API calls/day)
- **TEAMS**: Team tier ($99/mo, 100k API calls/day)
- **ENTERPRISE**: Enterprise tier (custom pricing, unlimited)

## Quick Start

### 1. Decorating Functions with Tier Requirements

```python
from impl.claude.protocols.licensing import requires_tier, LicenseTier, LicenseError

# Sync function
@requires_tier(LicenseTier.PRO)
def soul_advise(prompt: str) -> str:
    """PRO-only feature."""
    return f"Advice: {prompt}"

# Async function
from impl.claude.protocols.licensing.gate import requires_tier_async

@requires_tier_async(LicenseTier.PRO)
async def soul_advise_async(prompt: str) -> str:
    """PRO-only async feature."""
    return f"Advice: {prompt}"
```

### 2. Setting Current User Tier

```python
from impl.claude.protocols.licensing import set_current_tier, LicenseTier

# Set tier for current context
set_current_tier(LicenseTier.PRO)

# Now PRO features will work
result = soul_advise("How do I architect this?")
```

### 3. Handling License Errors

```python
from impl.claude.protocols.licensing import LicenseError, set_current_tier, LicenseTier

set_current_tier(LicenseTier.FREE)

try:
    result = soul_advise("Need advice")
except LicenseError as e:
    print(f"Feature '{e.feature}' requires {e.required.name} tier")
    print(f"Current tier: {e.current.name}")
    print("Upgrade at https://kgents.io/pricing")
```

### 4. Checking Features Programmatically

```python
from impl.claude.protocols.licensing import (
    FeatureFlag,
    FeatureRegistry,
    is_feature_enabled,
    LicenseTier
)

# Check if a feature is enabled for a tier
if is_feature_enabled(FeatureFlag.SOUL_ADVISE, LicenseTier.PRO):
    print("Feature available!")

# Get all features for a tier
pro_features = FeatureRegistry.get_features_for_tier(LicenseTier.PRO)
print(f"PRO tier has {len(pro_features)} features")

# Get feature info
info = FeatureRegistry.get_info(FeatureFlag.SOUL_ADVISE)
print(f"Feature: {info.flag.name}")
print(f"Required tier: {info.tier.name}")
print(f"Description: {info.description}")
print(f"Category: {info.category}")
```

### 5. Using Context Objects

```python
from dataclasses import dataclass
from impl.claude.protocols.licensing import requires_tier, LicenseTier

@dataclass
class UserContext:
    user_id: str
    license_tier: LicenseTier

@requires_tier(LicenseTier.PRO)
def pro_feature(ctx: UserContext) -> str:
    """Decorator extracts tier from ctx.license_tier."""
    return f"Hello user {ctx.user_id}"

# Works if context has PRO tier
ctx = UserContext(user_id="alice", license_tier=LicenseTier.PRO)
result = pro_feature(ctx)

# Fails if context has FREE tier
ctx = UserContext(user_id="bob", license_tier=LicenseTier.FREE)
# Raises LicenseError
```

### 6. Explicit Tier Override

```python
@requires_tier(LicenseTier.PRO)
def pro_feature(license_tier: LicenseTier | None = None) -> str:
    return "success"

# Override with explicit kwarg (bypasses context)
result = pro_feature(license_tier=LicenseTier.PRO)
```

## Tier Configurations

### FREE Tier
- Price: $0/month
- API calls: 100/day
- Features: soul_reflect, status, parse_basic, trace_basic, map_basic
- Support: Community

### PRO Tier
- Price: $19/month
- API calls: 10,000/day
- Features: All FREE + soul_advise, soul_challenge, soul_explore, whatif, shadow, dialectic, etc.
- Support: Email

### TEAMS Tier
- Price: $99/month
- API calls: 100,000/day
- Max members: 10
- Features: All PRO + team_collaboration, shared_gardens, team_analytics, audit_logs
- Support: Priority

### ENTERPRISE Tier
- Price: Custom
- API calls: Unlimited
- Max members: Unlimited
- Features: All TEAMS + custom_deployment, SSO, white_label, on_premise
- Support: Dedicated with SLA

## Feature Categories

Features are organized into categories:
- **soul**: Soul dialogue modes (reflect, advise, challenge, explore, vibe, drift, tense)
- **cli**: Command-line interface features
- **code_analysis**: Code parsing and tracing
- **analysis**: Scenario and shadow analysis
- **workflow**: Approval workflows and watchers
- **monitoring**: Dashboards and analytics
- **quality**: Gatekeeper and validation
- **collaboration**: Team features
- **security**: Access control and audit logs
- **infrastructure**: Deployment and custom models
- **integration**: Custom integrations
- **branding**: White label options

## Testing

Run the full test suite:
```bash
pytest impl/claude/protocols/licensing/_tests/ -v
```

Run type checking:
```bash
mypy protocols/licensing --strict
```

## Architecture Notes

- **Context Variables**: Uses `contextvars` for thread-safe tier tracking
- **Decorator Pattern**: `@requires_tier` for declarative gating
- **Type Safety**: Full mypy strict compliance
- **Immutable Configs**: Frozen dataclasses prevent accidental mutation
- **Tier Hierarchy**: Higher tiers include all lower tier features
