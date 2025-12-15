---
path: plans/agent-town/unified-v2
status: active
progress: 0
priority: 10.0
importance: crown_jewel
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town-launch
  - revenue/first-dollar
supersedes:
  - plans/agent-town/grand-strategy.md
  - plans/agent-town/monetization-mvp.md
  - plans/agent-town/phase8-inhabit.md
  - plans/agent-town/phase9-web-ui.md
session_notes: |
  UNIFIED V2: Synthesizes plan-review.md critical feedback.
  Key corrections: unit economics, safety/consent, instrumentation-first,
  LOD5 artifact guarantee, CAC/retention assumptions, Haiku-default routing.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched
  QA: touched
  TEST: touched
  MEASURE: touched
  REFLECT: touched
  EDUCATE: pending
entropy:
  planned: 0.15
  spent: 0.05
  remaining: 0.10
---

# Agent Town Unified Plan v2: Economics-Grounded, Ethics-First

> *"Margin before magic. Safety before speed. Instrument before monetize."*

---

## 0. Critical Corrections Applied

| Original Flaw | Correction | Principle Alignment |
|---------------|------------|---------------------|
| LOD4 @ 50 credits = $0.005-0.01, but Sonnet costs ~$0.014 | LOD4 @ 100 credits = $0.02-0.05 (margin-safe) | Tasteful: sustainable economics |
| LOD5 @ 200 credits = $0.05-0.20, but Opus costs ~$0.108 | LOD5 @ 400 credits = $0.10-0.40 (margin-safe) | Curated: premium is premium |
| "Force resistance" ethically unconstrained | Consent debt meter + opt-in + expensive + logged | Ethical: augment, don't override |
| No instrumentation before monetization | Phase 5.1: Metrics Spine prerequisite | Generative: measure before optimize |
| LOD5 "opacity" = paying for nothing | Artifact guarantee: vignette or tension reveal | Joy-Inducing: mystery has value |
| No CAC/retention assumptions | Kill-switch: if CAC > 30% LTV, halt | Tasteful: no vanity metrics |
| Branching for all tiers | Branching = Citizen+ only (state is expensive) | Composable: cost follows complexity |
| $120M market figure unverified | Mark as **unverified**; cite RevenueCat for trends | Ethical: transparency |

---

## 1. Unit Economics Reality (Claude Pricing 2024-10)

### Model Costs (per 1M tokens)

| Model | Input | Output | Typical Call (in+out) | Margin Target |
|-------|-------|--------|----------------------|---------------|
| Haiku | $0.25 | $1.25 | ~$0.0005 (300 tok) | 80%+ |
| Sonnet | $3.00 | $15.00 | ~$0.014 (800 tok) | 60%+ |
| Opus | $15.00 | $75.00 | ~$0.108 (1200 tok) | 40%+ |

### Revised Credit Costs (Margin-Safe)

| Action | Model | Raw Cost | Credits | Price Range | Gross Margin |
|--------|-------|----------|---------|-------------|--------------|
| LOD 3 | Haiku | $0.0005 | 10 | $0.01-0.05 | 95-99% |
| LOD 4 | Sonnet | $0.014 | **100** | $0.02-0.05 | 30-70% |
| LOD 5 | Opus | $0.108 | **400** | $0.10-0.40 | 0-73% |
| Branch | State | $0.01 | 150 | $0.03-0.15 | 66-93% |
| INHABIT (10 min) | Mixed | $0.05 | 100 | $0.02-0.10 | -60-50% |
| Force | Sonnet | $0.014 | 50 | $0.01-0.025 | 28-78% |

**Key insight**: INHABIT sessions can be **loss-leaders** to drive engagement, but must have caps.

### Credit Packs (Revised)

| Pack | Credits | Price | $/Credit | Break-even Actions |
|------|---------|-------|----------|-------------------|
| Starter | 500 | $4.99 | $0.010 | 50 LOD3 or 5 LOD4 |
| Explorer | 2,500 | $19.99 | $0.008 | 250 LOD3 or 25 LOD4 |
| Adventurer | 10,000 | $59.99 | $0.006 | 1000 LOD3 or 100 LOD4 |

---

## 2. Safety & Consent Framework

### The Consent Debt Meter

```python
@dataclass
class ConsentState:
    """Tracks relationship between user and inhabited citizen."""

    debt: float = 0.0  # 0.0 = harmony, 1.0 = rupture
    forces: int = 0    # Total forced actions
    cooldown: float = 0.0  # Time since last force

    def can_force(self) -> bool:
        """Force requires debt < 0.8 and cooldown elapsed."""
        return self.debt < 0.8 and self.cooldown <= 0.0

    def apply_force(self, severity: float = 0.2) -> None:
        """Force increases debt, resets cooldown."""
        self.debt = min(1.0, self.debt + severity)
        self.forces += 1
        self.cooldown = 60.0  # 60 seconds between forces

    def cool_down(self, elapsed: float) -> None:
        """Debt decays over time (harmony restoration)."""
        self.cooldown = max(0.0, self.cooldown - elapsed)
        self.debt = max(0.0, self.debt - elapsed * 0.001)  # Slow decay

    def at_rupture(self) -> bool:
        """Citizen refuses all interaction until debt clears."""
        return self.debt >= 1.0
```

### Force Mechanic (Ethical Guardrails)

| Guardrail | Implementation |
|-----------|----------------|
| **Opt-in** | User must enable "Advanced INHABIT" in settings |
| **Expensive** | 50 credits (3x normal action) |
| **Logged** | All forces recorded with timestamp, action, citizen |
| **Limited** | Max 3 forces per session, 60s cooldown between |
| **Consequences** | Debt accumulates, citizen may refuse all interaction |
| **Reversible** | Debt decays over time; apologize action accelerates decay |

### INHABIT Session Caps

| Tier | Session Cap | Daily Cap | Force Limit |
|------|-------------|-----------|-------------|
| Citizen | 15 min | 60 min | 3/session |
| Founder | 30 min | Unlimited | 5/session |

---

## 3. LOD 5: Artifact Guarantee

**Problem**: "Opacity" sounds like paying for nothing.

**Solution**: LOD 5 always delivers a **concrete artifact** that embodies the mystery:

| Artifact Type | Example |
|---------------|---------|
| **Vignette** | "Clara stood at the well's edge. The water reflected something that wasn't her face. She remembers a choice made before the town existed—a debt unpaid to someone who may never return." |
| **Tension Reveal** | "HIDDEN: Clara and Eve share a secret about the founding. Neither will speak of it. This tension influences Clara's resistance to questions about the past." |
| **Dream Fragment** | "Last night, Clara dreamed of keys. Seven keys for seven doors, but only six doors exist in the town. The seventh door is her own making." |
| **Relational Graph** | Visual showing hidden connections—Clara's secret alliance with Eve, her unspoken debt to Alice, her fear of David's questions. |

**The Opacity Principle preserved**: The artifact deepens mystery, doesn't resolve it. You learn *that* something is hidden, not *what* it is.

---

## 4. Instrumentation Spine (Phase 5.1)

**Prerequisite for monetization**: Without metrics, we can't validate business hypotheses.

### Required Metrics

| Metric | Collection Point | Purpose |
|--------|------------------|---------|
| `action.cost.tokens` | Every LLM call | Unit economics validation |
| `action.cost.credits` | Every billable action | Revenue tracking |
| `action.latency.p50/p95` | Every LLM call | SLO enforcement |
| `user.session.duration` | Session start/end | Engagement measurement |
| `user.conversion.step` | Paywall interactions | Funnel analysis |
| `user.churn.signal` | 7-day inactivity | Retention early warning |
| `lod.unlock.depth` | LOD upgrade clicks | Willingness to pay |
| `inhabit.force.count` | Force actions | Ethics monitoring |
| `inhabit.consent.debt` | Session end | Relationship health |

### Implementation Contract

```python
# protocols/api/metrics.py

@dataclass
class ActionMetric:
    """Every billable action emits this."""

    action_type: str  # lod3, lod4, lod5, branch, inhabit, force
    user_id: str
    town_id: str
    citizen_id: str | None
    tokens_in: int
    tokens_out: int
    model: str  # haiku, sonnet, opus
    latency_ms: int
    credits_charged: int
    timestamp: datetime

    def to_otel_span(self) -> dict:
        """Export as OpenTelemetry span attributes."""
        return {
            "action.type": self.action_type,
            "action.model": self.model,
            "action.tokens.in": self.tokens_in,
            "action.tokens.out": self.tokens_out,
            "action.latency_ms": self.latency_ms,
            "action.credits": self.credits_charged,
        }


def instrument_action(action: BilledAction) -> Callable:
    """Decorator to instrument any billable action."""
    def decorator(fn: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            start = time.monotonic()
            result = await fn(*args, **kwargs)
            latency = (time.monotonic() - start) * 1000

            emit_metric(ActionMetric(
                action_type=action.type,
                latency_ms=int(latency),
                tokens_in=result.tokens_in,
                tokens_out=result.tokens_out,
                # ... other fields
            ))

            return result
        return wrapper
    return decorator
```

---

## 5. CAC/Retention Assumptions + Kill-Switch

### Baseline Assumptions (from RevenueCat 2025)

| Metric | Conservative | Moderate | Aggressive |
|--------|--------------|----------|------------|
| Paid conversion | 5% | 8% | 12% |
| Monthly churn | 20% | 15% | 10% |
| ARPU (paid) | $15 | $22 | $30 |
| CAC | $10 | $15 | $25 |
| LTV | $75 | $147 | $300 |
| LTV/CAC | 7.5 | 9.8 | 12.0 |

### Kill-Switch Conditions

| Condition | Threshold | Action |
|-----------|-----------|--------|
| CAC > 30% LTV | $22.50 (conservative) | Halt paid acquisition |
| Churn > 25% M1 | 25% | Emergency retention analysis |
| Conversion < 3% | 3% | Pause monetization, focus on engagement |
| LOD unlock rate < 5% | 5% | Revisit paywall UX |
| Force rate > 30% of sessions | 30% | Ethics review, adjust mechanics |

---

## 6. Haiku-First Routing

**Principle**: Use the cheapest model that satisfies the task.

| Request Type | Default Model | Upgrade Trigger |
|--------------|---------------|-----------------|
| Background NPC thoughts | Haiku | Never |
| Active NPC dialogue | Haiku | User requests LOD 4+ |
| LOD 3 (memories) | Haiku | Never |
| LOD 4 (psyche) | Sonnet | User explicit |
| LOD 5 (abyss) | Opus | User explicit + credits |
| INHABIT (basic) | Haiku | Alignment check |
| INHABIT (complex) | Sonnet | Resistance negotiation |
| Force override | Sonnet | Always |

### Routing Logic

```python
def select_model(
    request_type: str,
    user_tier: SubscriptionTier,
    explicit_upgrade: bool = False,
) -> str:
    """Select cheapest adequate model."""

    # LOD 4-5 always require explicit upgrade
    if request_type in ["lod4", "lod5"]:
        if not explicit_upgrade:
            raise PaywallError(f"{request_type} requires explicit unlock")
        return "sonnet" if request_type == "lod4" else "opus"

    # Everything else defaults to Haiku
    return "haiku"
```

---

## 7. Subscription Tiers (Revised)

| Tier | Price | LOD Access | INHABIT | Branching | Towns |
|------|-------|------------|---------|-----------|-------|
| **Tourist** | FREE | 0-1 | None | None | Demo only |
| **Resident** | $9.99/mo | 0-2, 50 LOD3 | Basic (no force) | None | 1 |
| **Citizen** | $29.99/mo | 0-3, 20 LOD4 | Full (with force) | 3/month | 5 |
| **Founder** | $99.99/mo | Unlimited | Unlimited | Unlimited | Unlimited + API |

**Key change**: Branching moved to Citizen+ only due to state storage costs.

---

## 8. Parallel N-Phase Tracks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGENT TOWN PARALLEL TRACKS                                │
│                                                                              │
│   Track A: INHABIT Mode (Safety-First)                                       │
│   ├─ PLAN: Consent framework, session caps                                   │
│   ├─ IMPLEMENT: Portal + consent debt + force mechanics                      │
│   └─ Exit: INHABIT working with ethical guardrails                          │
│                                                                              │
│   Track B: Instrumentation Spine                                             │
│   ├─ PLAN: Metrics contract, OTEL integration                               │
│   ├─ IMPLEMENT: ActionMetric, decorators, dashboards                        │
│   └─ Exit: Every action emits metrics                                       │
│                                                                              │
│   Track C: Monetization Infrastructure                                       │
│   ├─ PLAN: Unit economics, Stripe setup                                     │
│   ├─ IMPLEMENT: BudgetStore, paywall, checkout                              │
│   └─ Exit: Can charge for LOD 3-5, subscriptions work                       │
│                                                                              │
│   Track D: Web UI MVP                                                        │
│   ├─ DEPENDS: A, B, C                                                       │
│   ├─ IMPLEMENT: Mesa, Citizen Panel, INHABIT browser                        │
│   └─ Exit: Public demo, payment working                                     │
│                                                                              │
│   Track E: Premium Scenarios (Flagship Only)                                │
│   ├─ PLAN: "The Vanishing" + "The Founding" only                            │
│   ├─ IMPLEMENT: Scenario loader, preset citizen configs                     │
│   └─ Exit: 2 purchasable scenarios                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Exit Criteria (Crown Jewel Launch)

| Criterion | Verification |
|-----------|--------------|
| Unit economics validated | Metrics show LOD margins > 30% |
| Safety framework active | Consent debt working, force logged |
| Kill-switch in place | Automated alerts for CAC/churn thresholds |
| 900+ tests passing | pytest with coverage |
| Demo town public | URL accessible, LOD 0-1 visible |
| Payment working | Can subscribe, buy credits, unlock LOD |
| 2 scenarios available | "The Vanishing" + "The Founding" |
| Kent says "amazing" | The Mirror Test |

---

## 10. Non-Goals (Explicit Pruning)

| Feature | Reason | When to Revisit |
|---------|--------|-----------------|
| 25 citizens | Scale complexity | After $10K MRR |
| Mobile native app | Resource constraint | After web proven |
| Custom scenario builder | Scope creep | After flagships sell |
| VR/AR support | Premature | After 2026 |
| Phase 12 mystery packs (all 5) | Feature sprawl | After 2 prove out |

---

## Continuation Seeds

See next file: `plans/agent-town/master-prompts-v2.md` for N-phase kickoff prompts.

---

*"Margin before magic. Safety before speed. Instrument before monetize."*
