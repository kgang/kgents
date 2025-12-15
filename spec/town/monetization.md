# Agent Town Monetization Specification

> *"The spec is the source of truth. Implementation derives from it."*

**Status**: Active
**AD Reference**: AD-004 (Pre-Computed Richness), AD-007 (Generative Over Enumerative)

---

## 1. Definitions

### 1.1 Credit

A **Credit** is the atomic unit of value exchange in Agent Town.

```
Credit := { value: Rational, model_class: ModelClass }
```

Credits are consumed when users request LLM-backed operations.

### 1.2 Model Classes

| Class | Models | Base Cost (per 1K tokens) |
|-------|--------|---------------------------|
| CHEAP | Haiku | $0.00075 |
| STANDARD | Sonnet | $0.009 |
| PREMIUM | Opus | $0.045 |

### 1.3 Subscription Tier

```
SubscriptionTier := TOURIST | RESIDENT | CITIZEN | FOUNDER
```

Each tier grants:
- A set of **included actions** (monthly allowance)
- Access to **gated features** (INHABIT, branching)
- A **credit multiplier** (bulk discount)

---

## 2. Pricing Laws

### Law P1: Margin Safety

For any action A with raw cost C and price P:

```
P >= C * 1.3  (minimum 30% gross margin)
```

**Rationale**: Sustainable economics before growth.

### Law P2: Model Truthfulness

The model used MUST match the model charged:

```
charged_model(action) == actual_model(action)
```

**Violation**: Ethical breach. User pays for Opus, receives Haiku.

### Law P3: Transparency

All prices MUST be visible before action:

```
display_price(action) THEN confirm(user) THEN execute(action)
```

**No dark patterns**: Never charge without explicit consent.

---

## 3. Action Catalog

### 3.1 LOD Actions

| Action | Model | Tokens (est.) | Raw Cost | Credits | Price Range |
|--------|-------|---------------|----------|---------|-------------|
| `lod.view.3` | CHEAP | 300 | $0.0005 | 10 | $0.01-0.05 |
| `lod.view.4` | STANDARD | 800 | $0.014 | 100 | $0.02-0.05 |
| `lod.view.5` | PREMIUM | 1200 | $0.108 | 400 | $0.10-0.40 |

### 3.2 INHABIT Actions

| Action | Model | Tokens (est.) | Raw Cost | Credits | Price Range |
|--------|-------|---------------|----------|---------|-------------|
| `inhabit.session.10min` | MIXED | 2000 | $0.05 | 100 | $0.02-0.10 |
| `inhabit.force` | STANDARD | 500 | $0.014 | 50 | $0.01-0.025 |
| `inhabit.apologize` | CHEAP | 200 | $0.0003 | 5 | $0.001-0.005 |

### 3.3 Branch Actions

| Action | Model | Storage | Credits | Price Range |
|--------|-------|---------|---------|-------------|
| `branch.create` | N/A | $0.01 | 150 | $0.03-0.15 |
| `branch.switch` | N/A | $0.001 | 10 | $0.002-0.01 |
| `branch.merge` | N/A | $0.005 | 50 | $0.01-0.05 |

---

## 4. Subscription Tiers

### 4.1 TOURIST (Free)

```yaml
tier: TOURIST
price: 0
included:
  lod_0: unlimited
  lod_1: unlimited
features:
  inhabit: false
  branching: false
  towns: 0  # demo only
```

### 4.2 RESIDENT ($9.99/mo)

```yaml
tier: RESIDENT
price: 9.99
included:
  lod_0: unlimited
  lod_1: unlimited
  lod_2: unlimited
  lod_3: 50/month
features:
  inhabit: basic  # no force
  branching: false
  towns: 1
credit_multiplier: 1.0
```

### 4.3 CITIZEN ($29.99/mo)

```yaml
tier: CITIZEN
price: 29.99
included:
  lod_0: unlimited
  lod_1: unlimited
  lod_2: unlimited
  lod_3: unlimited
  lod_4: 20/month
features:
  inhabit: full  # with force
  branching: 3/month
  towns: 5
credit_multiplier: 0.9  # 10% discount
```

### 4.4 FOUNDER ($99.99/mo)

```yaml
tier: FOUNDER
price: 99.99
included:
  lod_0: unlimited
  lod_1: unlimited
  lod_2: unlimited
  lod_3: unlimited
  lod_4: unlimited
  lod_5: 50/month
features:
  inhabit: unlimited
  branching: unlimited
  towns: unlimited
  api_access: true
credit_multiplier: 0.75  # 25% discount
```

---

## 5. Credit Packs

```yaml
packs:
  starter:
    credits: 500
    price: 4.99
    per_credit: 0.00998

  explorer:
    credits: 2500
    price: 19.99
    per_credit: 0.00800

  adventurer:
    credits: 10000
    price: 59.99
    per_credit: 0.00600
```

---

## 6. Consent Framework

### 6.1 Consent Debt

```
ConsentDebt := { value: [0.0, 1.0], forces: Nat, cooldown: Duration }
```

**Laws**:
- `force` increases debt by 0.2
- Debt decays at 0.001/second
- `apologize` action reduces debt by 0.1
- At `debt >= 1.0`: citizen refuses all interaction (rupture)

### 6.2 Force Constraints

```yaml
force_constraints:
  opt_in_required: true
  max_per_session: 3
  cooldown_seconds: 60
  cost_multiplier: 3.0  # 3x normal action
  logged: true
```

---

## 7. Kill-Switch Conditions

```yaml
kill_switches:
  cac_ltv_ratio:
    threshold: 0.30  # CAC > 30% LTV
    action: halt_paid_acquisition

  m1_churn:
    threshold: 0.25  # >25% churn month 1
    action: emergency_retention_review

  conversion_rate:
    threshold: 0.03  # <3% conversion
    action: pause_monetization

  force_rate:
    threshold: 0.30  # >30% sessions have force
    action: ethics_review
```

---

## 8. Metrics Contract

Every billable action MUST emit:

```yaml
action_metric:
  required_fields:
    - action_type: string
    - user_id: string
    - town_id: string
    - citizen_id: string?
    - model: string
    - tokens_in: int
    - tokens_out: int
    - latency_ms: int
    - credits_charged: int
    - timestamp: datetime
  export:
    - otel_span
    - prometheus_counter
```

---

## 9. Paywall Contract

```python
@dataclass(frozen=True)
class PaywallCheck:
    """Input to paywall decision."""
    user_tier: SubscriptionTier
    user_credits: int
    action: Action
    monthly_usage: dict[str, int]


@dataclass(frozen=True)
class PaywallResult:
    """Output of paywall decision."""
    allowed: bool
    reason: str | None
    cost: int  # credits if allowed
    upgrade_options: list[UpgradeOption]


def check_paywall(check: PaywallCheck) -> PaywallResult:
    """
    Pure function implementing paywall logic.

    Laws:
    - If action in included allowance and under limit: allowed, cost=0
    - If action requires credits and user has enough: allowed, cost=action.credits
    - If action requires credits and user lacks: blocked, show upgrade options
    - If action requires feature user doesn't have: blocked, show tier upgrade
    """
    ...
```

---

## 10. Generative Principle

This spec is designed to **generate** the implementation:

| Spec Section | Generates |
|--------------|-----------|
| §3 Action Catalog | `BilledAction` enum + cost table |
| §4 Subscription Tiers | `SubscriptionTier` enum + feature flags |
| §5 Credit Packs | Stripe product configuration |
| §6 Consent Framework | `ConsentState` class |
| §7 Kill-Switches | Alert rules + monitoring |
| §8 Metrics Contract | `ActionMetric` dataclass |
| §9 Paywall Contract | `check_paywall()` function |

**Autopoiesis Score Target**: >70% of monetization code derivable from this spec.

---

*"The spec is the source of truth. Implementation derives from it."*
