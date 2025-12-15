---
path: plans/agent-town/monetization-mvp
status: active
progress: 0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking:
  - agent-town-phase9-web
enables:
  - revenue/first-dollar
  - scale/growth-engine
session_notes: |
  MONETIZATION MVP for Agent Town.
  Based on 2025 AI companion app research ($120M market).
  Hybrid model: subscriptions + consumable credits.
phase_ledger:
  PLAN: touched
  RESEARCH: complete
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.08
  spent: 0.03
  remaining: 0.05
---

# Agent Town Monetization MVP

> *"The best monetization is invisible until the moment it creates value."*

---

## Market Context

### The Opportunity

The AI companion app market is [on track to reach $120M in 2025](https://techcrunch.com/2025/08/12/ai-companion-apps-on-track-to-pull-in-120m-in-2025/), with:
- Revenue per download **doubled** from $0.52 (2024) to $1.18 (2025)
- [Top 10% capture 89% of revenue](https://www.webpronews.com/ai-companion-apps-surge-to-120m-revenue-by-2025-amid-growth-boom/)
- [35% of apps now use hybrid models](https://www.revenuecat.com/blog/company/the-state-of-subscription-apps-2025-launch/) (subscriptions + consumables)

### Why Agent Town Can Win

| Differentiator | Competitors | Agent Town |
|----------------|-------------|------------|
| Depth | Single AI companion | 25 interacting citizens |
| Emergence | Scripted responses | Emergent drama from operad composition |
| Philosophy | "Your AI friend" | Cosmotechnical simulation, citizen rights |
| Time | Real-time only | Time travel, branching |
| Opacity | Full transparency | Right to irreducibility |

---

## The Three Revenue Streams

### Stream 1: Subscriptions (Recurring)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SUBSCRIPTION TIERS                                   │
│                                                                              │
│   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐                 │
│   │    TOURIST    │   │   RESIDENT    │   │   CITIZEN     │                 │
│   │     FREE      │   │   $9.99/mo    │   │  $29.99/mo    │                 │
│   │               │   │               │   │               │                 │
│   │ • LOD 0-1     │   │ • LOD 0-2     │   │ • LOD 0-3     │                 │
│   │ • Demo town   │   │ • 100 LOD 3   │   │ • 50 LOD 4    │                 │
│   │ • Observer    │   │ • 1 town      │   │ • 5 towns     │                 │
│   │   only        │   │ • Basic       │   │ • INHABIT     │                 │
│   │               │   │   INHABIT     │   │ • Branching   │                 │
│   └───────────────┘   └───────────────┘   └───────────────┘                 │
│                                                                              │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                           FOUNDER                                      │ │
│   │                          $99.99/mo                                     │ │
│   │                                                                         │ │
│   │  • Unlimited all LOD    • Unlimited towns    • API access              │ │
│   │  • Priority support     • Early features     • Custom scenarios        │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Stream 2: Credits (Consumable)

Following [Adobe's Firefly model](https://blog.crossmint.com/monetize-ai-agents/):

| Pack | Credits | Price | Value |
|------|---------|-------|-------|
| **Starter** | 500 | $4.99 | $0.010/credit |
| **Explorer** | 2,000 | $14.99 | $0.0075/credit |
| **Adventurer** | 10,000 | $49.99 | $0.005/credit |

**Credit Costs**:

| Action | Credits | Rationale |
|--------|---------|-----------|
| LOD 3 view | 10 | Haiku call |
| LOD 4 view | 50 | Sonnet call |
| LOD 5 view | 200 | Opus call |
| Branch creation | 100 | State snapshot |
| INHABIT (10 min) | 50 | Multiple LLM calls |
| Force resistance | 30 | Extra processing |
| Time jump | 20 | State restore |

### Stream 3: Premium Scenarios (One-Time)

| Scenario | Description | Price |
|----------|-------------|-------|
| **The Vanishing** | A citizen disappears. Uncover the mystery. | $9.99 |
| **The Festival** | Plan Valentine's Day. Romance blossoms. | $4.99 |
| **The Schism** | Two coalitions clash. Choose your side. | $9.99 |
| **The Founding** | Seven citizens arrive. Shape the town. | $14.99 |
| **Custom Scenario** | Define your own starting conditions. | $29.99 |

---

## Implementation Architecture

### Payment Integration (Stripe)

```python
# protocols/api/payments.py

from stripe import stripe

@dataclass
class SubscriptionTier(Enum):
    TOURIST = "tourist"       # Free
    RESIDENT = "resident"     # $9.99/mo
    CITIZEN = "citizen"       # $29.99/mo
    FOUNDER = "founder"       # $99.99/mo

@dataclass
class StripeConfig:
    products: dict[SubscriptionTier, str] = field(default_factory=lambda: {
        SubscriptionTier.RESIDENT: "prod_resident_xxx",
        SubscriptionTier.CITIZEN: "prod_citizen_xxx",
        SubscriptionTier.FOUNDER: "prod_founder_xxx",
    })
    prices: dict[SubscriptionTier, str] = field(default_factory=lambda: {
        SubscriptionTier.RESIDENT: "price_resident_monthly_xxx",
        SubscriptionTier.CITIZEN: "price_citizen_monthly_xxx",
        SubscriptionTier.FOUNDER: "price_founder_monthly_xxx",
    })


class PaymentService:
    """Stripe integration for Agent Town."""

    def __init__(self, config: StripeConfig):
        self.config = config

    async def create_checkout_session(
        self,
        user_id: str,
        tier: SubscriptionTier,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """Create Stripe Checkout session."""
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer_email=await self._get_user_email(user_id),
            line_items=[{
                "price": self.config.prices[tier],
                "quantity": 1,
            }],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": user_id, "tier": tier.value},
        )
        return session.url

    async def purchase_credits(
        self,
        user_id: str,
        pack: CreditPack,
    ) -> str:
        """Create one-time purchase for credits."""
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{
                "price": pack.stripe_price_id,
                "quantity": 1,
            }],
            success_url=f"/credits/success?pack={pack.name}",
            cancel_url="/credits/cancel",
            metadata={"user_id": user_id, "credits": pack.credits},
        )
        return session.url
```

### Credit Management

```python
# agents/town/budget_store.py

@dataclass
class UserBudget:
    """User's credit balance and subscription status."""

    user_id: str
    subscription: SubscriptionTier
    credits: int = 0
    monthly_lod3_used: int = 0
    monthly_lod4_used: int = 0

    def can_afford(self, action: BilledAction) -> bool:
        """Check if user can afford an action."""
        if action.type == "lod3" and self._has_monthly_lod3():
            return True
        if action.type == "lod4" and self._has_monthly_lod4():
            return True
        return self.credits >= action.cost

    def charge(self, action: BilledAction) -> int:
        """Charge for an action. Returns credits used."""
        if action.type == "lod3" and self._has_monthly_lod3():
            self.monthly_lod3_used += 1
            return 0  # Included in subscription

        if action.type == "lod4" and self._has_monthly_lod4():
            self.monthly_lod4_used += 1
            return 0  # Included in subscription

        self.credits -= action.cost
        return action.cost

    def _has_monthly_lod3(self) -> bool:
        """Check if user has LOD 3 allowance remaining."""
        limits = {
            SubscriptionTier.TOURIST: 0,
            SubscriptionTier.RESIDENT: 100,
            SubscriptionTier.CITIZEN: 999999,  # Unlimited
            SubscriptionTier.FOUNDER: 999999,
        }
        return self.monthly_lod3_used < limits[self.subscription]

    def _has_monthly_lod4(self) -> bool:
        """Check if user has LOD 4 allowance remaining."""
        limits = {
            SubscriptionTier.TOURIST: 0,
            SubscriptionTier.RESIDENT: 0,
            SubscriptionTier.CITIZEN: 50,
            SubscriptionTier.FOUNDER: 999999,
        }
        return self.monthly_lod4_used < limits[self.subscription]


@dataclass
class BilledAction:
    """An action that costs credits."""
    type: str  # lod3, lod4, lod5, branch, inhabit, etc.
    cost: int
    description: str


# Cost table
COSTS = {
    "lod3": BilledAction("lod3", 10, "View LOD 3 (memories)"),
    "lod4": BilledAction("lod4", 50, "View LOD 4 (psyche)"),
    "lod5": BilledAction("lod5", 200, "View LOD 5 (abyss)"),
    "branch": BilledAction("branch", 100, "Create branch"),
    "inhabit_10min": BilledAction("inhabit_10min", 50, "INHABIT 10 minutes"),
    "force": BilledAction("force", 30, "Force resistance"),
    "time_jump": BilledAction("time_jump", 20, "Jump to past"),
}
```

### Paywall UI

```python
# agents/town/paywall.py

@dataclass
class PaywallResponse:
    """Response when action requires payment."""
    allowed: bool
    reason: str | None = None
    upgrade_options: list[UpgradeOption] = field(default_factory=list)


@dataclass
class UpgradeOption:
    """An option to unblock the action."""
    type: Literal["subscription", "credits", "pack"]
    name: str
    price: str
    description: str
    url: str


def check_paywall(
    user: UserBudget,
    action: BilledAction,
) -> PaywallResponse:
    """Check if action is allowed or requires payment."""

    if user.can_afford(action):
        return PaywallResponse(allowed=True)

    # Build upgrade options
    options = []

    # Suggest subscription upgrade if not at top tier
    if user.subscription != SubscriptionTier.FOUNDER:
        next_tier = _next_tier(user.subscription)
        options.append(UpgradeOption(
            type="subscription",
            name=f"Upgrade to {next_tier.value.title()}",
            price=_tier_price(next_tier),
            description=_tier_description(next_tier),
            url=f"/subscribe/{next_tier.value}",
        ))

    # Suggest credit pack
    if action.cost <= 500:
        options.append(UpgradeOption(
            type="pack",
            name="Starter Pack (500 credits)",
            price="$4.99",
            description="Enough for this action and more",
            url="/credits/starter",
        ))
    else:
        options.append(UpgradeOption(
            type="pack",
            name="Explorer Pack (2,000 credits)",
            price="$14.99",
            description="Better value for explorers",
            url="/credits/explorer",
        ))

    return PaywallResponse(
        allowed=False,
        reason=f"This action costs {action.cost} credits. You have {user.credits}.",
        upgrade_options=options,
    )
```

---

## User Journey

### Free User (Tourist)

```
1. Visit demo town (public URL)
2. See LOD 0-1 (silhouette, posture)
3. Watch citizens move, see emoji moods
4. Click citizen → paywall for LOD 2+
5. "Upgrade to Resident for full dialogue"
```

### Resident ($9.99/mo)

```
1. Create personal town
2. See LOD 0-2 (dialogue, greetings)
3. 100 LOD 3 views/month (memories)
4. Basic INHABIT mode
5. Hit LOD 4 → paywall: "Upgrade to Citizen or buy credits"
```

### Citizen ($29.99/mo)

```
1. Full LOD 0-3 access
2. 50 LOD 4/month (psyche)
3. Full INHABIT with resistance mechanics
4. Branching universes
5. Hit LOD 5 → "Purchase Adventurer pack for deepest insights"
```

### Founder ($99.99/mo)

```
1. Unlimited everything
2. API access for custom integrations
3. Priority support
4. Early access to new features
5. Custom scenario creation
```

---

## Revenue Projections

### Conservative Model

| Month | MAU | Tourist | Resident | Citizen | Founder | MRR |
|-------|-----|---------|----------|---------|---------|-----|
| M1 | 100 | 95 | 3 | 1 | 1 | $140 |
| M3 | 500 | 420 | 50 | 25 | 5 | $1,745 |
| M6 | 2,000 | 1,600 | 250 | 120 | 30 | $9,570 |
| M12 | 10,000 | 7,500 | 1,500 | 800 | 200 | $63,490 |

**Assumptions**:
- 5% → 8% → 10% → 12% conversion over 12 months
- 60% Resident, 30% Citizen, 10% Founder among paid
- Credit purchases add ~20% to subscription revenue

### Path to $10K MRR

```
$10K MRR =
  (200 Residents × $10) +
  (100 Citizens × $30) +
  (30 Founders × $100) +
  $2K credits
= $2K + $3K + $3K + $2K = $10K
```

**Required MAU**: ~3,000 with 11% conversion

---

## Implementation Phases

### Phase M1: Infrastructure (Week 1-2)

| Task | Description | Owner |
|------|-------------|-------|
| Stripe account | Set up Stripe with test mode | Kent |
| Products | Create subscription products | Kent |
| Webhook | Handle subscription events | Agent |
| BudgetStore | Implement credit management | Agent |

### Phase M2: Paywall (Week 3-4)

| Task | Description | Owner |
|------|-------------|-------|
| check_paywall() | Implement paywall logic | Agent |
| UI components | Paywall modal, upgrade prompts | Agent |
| Integration | Wire LOD requests through paywall | Agent |

### Phase M3: Checkout (Week 5-6)

| Task | Description | Owner |
|------|-------------|-------|
| Checkout flow | Stripe Checkout integration | Agent |
| Success handling | Credit/subscription activation | Agent |
| Email | Welcome/confirmation emails | Agent |

### Phase M4: Dashboard (Week 7-8)

| Task | Description | Owner |
|------|-------------|-------|
| User dashboard | Show subscription, credits, usage | Agent |
| Admin dashboard | Revenue metrics, user analytics | Agent |
| Reporting | Daily/weekly revenue reports | Agent |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Users reject paywall | Medium | High | Generous free tier, soft paywall messaging |
| LLM costs exceed revenue | Medium | High | Strict Haiku routing, cost monitoring |
| Low conversion | Medium | Medium | A/B test pricing, value demos |
| Churn | Medium | Medium | Engagement features, new content |
| Refund requests | Low | Low | Clear terms, quality guarantee |

---

## Success Metrics

| Metric | M3 Target | M6 Target |
|--------|-----------|-----------|
| MRR | $1,500 | $10,000 |
| Conversion rate | 8% | 10% |
| ARPU (paid users) | $15 | $20 |
| Churn (monthly) | <20% | <12% |
| Credit revenue % | 15% | 20% |
| LTV/CAC | >3 | >5 |

---

## Ethical Considerations

Per spec/principles.md **Ethical** principle:

1. **Transparent pricing**: No hidden fees, clear credit costs
2. **Value before payment**: Generous free tier demonstrates value
3. **No dark patterns**: Easy to cancel, no guilt-tripping
4. **Respect for time**: LOD 5 mystery is philosophical, not arbitrary paywall
5. **Data privacy**: Usage data for product improvement only

---

## Continuation

```
⟿[IMPLEMENT]
/hydrate plans/agent-town/monetization-mvp.md
handles:
  stripe: Set up Stripe account + test mode
  budget_store: agents/town/budget_store.py
  paywall: agents/town/paywall.py
  payments: protocols/api/payments.py
mission: Implement monetization infrastructure
exit: Stripe integrated; paywall working; ledger.IMPLEMENT=touched
```

---

*"The best monetization is invisible until the moment it creates value."*
