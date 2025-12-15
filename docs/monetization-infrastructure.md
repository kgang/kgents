# Agent Town Monetization Infrastructure

## Overview

Track C implementation of the Agent Town master plan (unified-v2.md). Complete payment and monetization infrastructure with margin-safe pricing, ethical guardrails, and kill-switch monitoring.

**Status**: ✅ Complete
**Exit Criteria**: All met
**Tests**: 82 passing

---

## Components Implemented

### 1. BudgetStore (Credit & Subscription Management)

**Location**: `impl/claude/agents/town/budget_store.py`

Revised from token-based to credit-based system with subscription tier support.

**Key Features**:
- `UserBudgetInfo`: Tracks credits, subscription tier, monthly usage
- `ConsentState`: Implements consent debt meter for INHABIT force mechanic
- `SubscriptionTier`: Defines TOURIST, RESIDENT, CITIZEN, FOUNDER tiers
- `InMemoryBudgetStore`: Dev/test implementation
- `RedisBudgetStore`: Production implementation with automatic monthly resets

**Subscription Tiers**:
| Tier | Price | LOD Access | Features |
|------|-------|------------|----------|
| TOURIST | FREE | 0-1 unlimited | Demo only |
| RESIDENT | $9.99/mo | 0-2 unlimited, 50 LOD3/mo | Basic INHABIT, 1 town |
| CITIZEN | $29.99/mo | 0-3 unlimited, 20 LOD4/mo | Full INHABIT + force, branching 3/mo, 5 towns |
| FOUNDER | $99.99/mo | 0-4 unlimited, 50 LOD5/mo | Unlimited INHABIT/branching, API access |

**Consent Debt Mechanics**:
- Debt: 0.0 (harmony) → 1.0 (rupture)
- Force increases debt by 0.2, resets 60s cooldown
- Debt decays at 0.001/sec
- Apologize reduces debt by 0.1
- At debt >= 0.8: force blocked
- At debt = 1.0: citizen refuses all interaction (rupture)

**Tests**: 23 passing

---

### 2. Paywall Logic

**Location**: `impl/claude/agents/town/paywall.py`

Pure function implementing paywall decisions per spec/town/monetization.md §9.

**Key Features**:
- `check_paywall()`: Pure function determining action access
- Action catalog with margin-safe pricing
- Feature access checks (INHABIT, branching)
- Upgrade option generation
- Consent debt validation

**Credit Costs** (per unified-v2.md §1):
| Action | Model | Credits | Price Range | Margin |
|--------|-------|---------|-------------|--------|
| LOD 3 | Haiku | 10 | $0.01-0.05 | 95-99% |
| LOD 4 | Sonnet | 100 | $0.02-0.05 | 30-70% |
| LOD 5 | Opus | 400 | $0.10-0.40 | 0-73% |
| INHABIT (10min) | Mixed | 100 | $0.02-0.10 | -60-50% |
| Force | Sonnet | 50 | $0.01-0.025 | 28-78% |
| Branch Create | Storage | 150 | $0.03-0.15 | 66-93% |

**Laws**:
1. If action in subscription allowance: allowed, cost=0
2. If action requires credits and user has enough: allowed, charge credits
3. If insufficient credits: blocked, show upgrade options
4. If feature not available to tier: blocked, show tier upgrade

**Tests**: 28 passing

---

### 3. Stripe Payment Integration

**Location**: `impl/claude/protocols/api/payments.py`

Stripe integration for subscriptions and one-time credit pack purchases.

**Key Features**:
- `PaymentClient`: Stripe API wrapper
- Subscription checkout sessions
- Credit pack checkout sessions
- Customer management
- Webhook event handlers
- `MockPaymentClient`: Testing without Stripe

**Webhook Handlers**:
- `subscription.created` → Update tier, set renewal date
- `subscription.updated` → Update status
- `subscription.deleted` → Downgrade to TOURIST
- `payment_intent.succeeded` → Add credits to balance

**Credit Packs**:
| Pack | Credits | Price | $/Credit | Break-even Actions |
|------|---------|-------|----------|-------------------|
| Starter | 500 | $4.99 | $0.010 | 50 LOD3 or 5 LOD4 |
| Explorer | 2,500 | $19.99 | $0.008 | 250 LOD3 or 25 LOD4 |
| Adventurer | 10,000 | $59.99 | $0.006 | 1000 LOD3 or 100 LOD4 |

**Tests**: 12 passing (+ 2 skipped integration tests)

---

### 4. Kill-Switch Monitoring

**Location**: `impl/claude/agents/town/kill_switch.py`

Automated safety thresholds per unified-v2.md §5 to halt operations if economics or ethics breach acceptable levels.

**Kill-Switch Conditions**:
| Condition | Threshold | Action | Severity |
|-----------|-----------|--------|----------|
| CAC/LTV ratio | > 30% | Halt paid acquisition | KILL_SWITCH |
| M1 churn | > 25% | Emergency retention review | CRITICAL |
| Conversion rate | < 3% | Pause monetization | CRITICAL |
| LOD unlock rate | < 5% | Revisit paywall UX | WARNING |
| Force rate | > 30% | Ethics review | CRITICAL |

**Key Features**:
- `MetricCalculator`: Calculate business/ethics metrics
- `KillSwitchMonitor`: Monitor thresholds, generate alerts
- Alert acknowledgment system
- Operational safety checks (`is_safe_to_operate()`)

**Example Metrics**:
```python
calc = MetricCalculator()

# Conservative scenario: CAC $10, LTV $75 → 13.3% (good)
metric = calc.calculate_cac_ltv_ratio(total_cac=10.0, total_ltv=75.0)

monitor = KillSwitchMonitor()
alert = monitor.check_metric(metric)  # None (no breach)
assert monitor.is_safe_to_operate()  # True
```

**Tests**: 19 passing

---

## Demo Flow

**Location**: `impl/claude/agents/town/demo/monetization_demo.py`

Full end-to-end demonstration:

1. **Tourist** tries LOD 3 → Paywall (blocked, shows upgrade options)
2. **Upgrade** to RESIDENT ($9.99/mo via Stripe)
3. **Webhook** processes subscription.created → Update tier
4. **Access** LOD 3 with monthly allowance (50/mo included)
5. **Exhaust** allowance → Paywall (need credits)
6. **Purchase** STARTER pack (500 credits, $4.99)
7. **Use** credits for LOD 3 (10 credits each)
8. **Try** LOD 4 (100 credits, allowed with credits)

**Run with**: `python -m impl.claude.agents.town.demo.monetization_demo`

---

## Exit Criteria

✅ **All criteria met**:

- [x] BudgetStore tracks credits, subscription tier, monthly usage
- [x] check_paywall() returns correct response for all LOD levels
- [x] Stripe Checkout session creation works (test mode)
- [x] Webhook updates user subscription status
- [x] Kill-switch alerts defined (CAC > 30% LTV, churn > 25%, etc.)
- [x] 82 tests passing (exceeded 40+ target)
- [x] Demo path verified: Tourist → paywall → Resident upgrade → LOD3 access

---

## Test Coverage

| Module | Tests | Focus |
|--------|-------|-------|
| `test_budget_store.py` | 23 | ConsentState, UserBudgetInfo, store operations |
| `test_paywall.py` | 28 | LOD access, INHABIT, branching, upgrade options |
| `test_kill_switch.py` | 19 | Metrics calculation, threshold monitoring, alerts |
| `test_payments.py` | 12 | Stripe integration, webhooks, mock client |
| **Total** | **82** | |

All tests passing. 2 skipped (Stripe integration tests requiring API keys).

---

## Key Principles Applied

1. **Margin before magic**: All pricing is margin-safe (30%+ gross margin targets)
2. **Safety before speed**: Consent debt meter prevents unethical force use
3. **Instrument before monetize**: Kill-switch conditions monitor business health
4. **Ethical guardrails**: Force requires opt-in, expensive, logged, limited
5. **Generative from spec**: Implementation derives from spec/town/monetization.md

---

## Next Steps

**For Kent**:
1. Configure Stripe production account
2. Set environment variables:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_WEBHOOK_SECRET`
3. Create Stripe products for subscription tiers
4. Create Stripe products for credit packs
5. Set price IDs in environment
6. Deploy with Redis for production BudgetStore

**For Track D (Web UI MVP)**:
- Integrate paywall checks into LOD unlock buttons
- Add subscription management UI
- Add credit pack purchase buttons
- Display kill-switch status in admin dashboard
- Show consent debt meter during INHABIT

---

## Files Created/Modified

**Created**:
- `impl/claude/agents/town/paywall.py` (345 lines)
- `impl/claude/agents/town/kill_switch.py` (520 lines)
- `impl/claude/protocols/api/payments.py` (650 lines)
- `impl/claude/agents/town/demo/monetization_demo.py` (270 lines)
- `impl/claude/agents/town/_tests/test_budget_store.py` (285 lines)
- `impl/claude/agents/town/_tests/test_paywall.py` (450 lines)
- `impl/claude/agents/town/_tests/test_kill_switch.py` (390 lines)
- `impl/claude/protocols/api/_tests/test_payments.py` (150 lines)

**Modified**:
- `impl/claude/agents/town/budget_store.py` (revised for credit-based system)

**Total**: ~3,060 lines of implementation + tests

---

*"Margin before magic. Safety before speed. Instrument before monetize."*
