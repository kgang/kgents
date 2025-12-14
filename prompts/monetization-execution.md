# Monetization Grand Initiative: Execution Prompt

> *"This is the prompt. Run it. Ship revenue."*

**Source Plan**: `plans/monetization/grand-initiative-monetization.md`
**Phase**: IMPLEMENT (all SENSE phases complete)
**Parallel Agents**: 4 tracks

---

## Pre-Execution Checklist

```bash
# Verify ground state
/hydrate

# Confirm tests pass
cd impl/claude && uv run pytest -q && uv run mypy .

# Expected: 13,345+ tests, 0 mypy errors
```

---

## Track Assignments

### Track A: License Infrastructure
**Agent 1 Focus**: Build the gating layer

```markdown
/hydrate
# Track A: License Infrastructure

## Context
- Plan: plans/monetization/grand-initiative-monetization.md
- Phase: IMPLEMENT
- Entropy: void.entropy.sip(0.07)

## Mission
Create license tier infrastructure that gates Pro features.

## Files to Create
impl/claude/protocols/licensing/
├── __init__.py
├── tiers.py        # LicenseTier enum, tier configs
├── gate.py         # @requires_tier decorator
├── features.py     # FeatureFlag enum + registry
└── _tests/
    ├── __init__.py
    ├── test_tiers.py
    ├── test_gate.py
    └── test_features.py

## Implementation Specs

### tiers.py
```python
from enum import Enum, auto
from dataclasses import dataclass
from typing import FrozenSet

class LicenseTier(Enum):
    """License tiers with ascending privileges."""
    FREE = auto()
    PRO = auto()
    TEAMS = auto()
    ENTERPRISE = auto()

    def __ge__(self, other: "LicenseTier") -> bool:
        return self.value >= other.value

@dataclass(frozen=True)
class TierConfig:
    """Configuration for a license tier."""
    tier: LicenseTier
    price_monthly: int  # cents
    features: FrozenSet[str]
    api_calls_per_day: int
    support_level: str

TIER_CONFIGS: dict[LicenseTier, TierConfig] = {
    LicenseTier.FREE: TierConfig(
        tier=LicenseTier.FREE,
        price_monthly=0,
        features=frozenset({"soul_reflect", "status", "parse_basic"}),
        api_calls_per_day=100,
        support_level="community",
    ),
    LicenseTier.PRO: TierConfig(
        tier=LicenseTier.PRO,
        price_monthly=1900,  # $19
        features=frozenset({
            "soul_reflect", "soul_advise", "soul_challenge", "soul_explore",
            "soul_vibe", "soul_drift", "soul_tense",
            "whatif", "shadow", "dialectic", "parse_all",
            "approve", "budget_dashboard",
        }),
        api_calls_per_day=10000,
        support_level="email",
    ),
    # ... TEAMS and ENTERPRISE configs
}
```

### gate.py
```python
from functools import wraps
from typing import Callable, TypeVar, ParamSpec
from impl.claude.protocols.licensing.tiers import LicenseTier

P = ParamSpec("P")
T = TypeVar("T")

class LicenseError(Exception):
    """Raised when feature requires higher tier."""
    def __init__(self, feature: str, required: LicenseTier, current: LicenseTier):
        self.feature = feature
        self.required = required
        self.current = current
        super().__init__(
            f"Feature '{feature}' requires {required.name} tier. "
            f"Current tier: {current.name}. Upgrade at https://kgents.io/pricing"
        )

def requires_tier(tier: LicenseTier) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to gate features by license tier."""
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Get current user tier from context
            ctx = _extract_context(args, kwargs)
            current_tier = ctx.license_tier if ctx else LicenseTier.FREE

            if current_tier < tier:
                raise LicenseError(func.__name__, tier, current_tier)

            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## Exit Criteria
- [ ] LicenseTier enum with comparison operators
- [ ] TierConfig for FREE, PRO, TEAMS, ENTERPRISE
- [ ] @requires_tier decorator working
- [ ] FeatureFlag registry with 20+ features
- [ ] 30+ tests passing
- [ ] mypy strict passing

## Continuation
ledger.IMPLEMENT=touched → next=QA
```

---

### Track B: Stripe Integration
**Agent 2 Focus**: Payment infrastructure

```markdown
/hydrate
# Track B: Stripe Integration

## Context
- Plan: plans/monetization/grand-initiative-monetization.md
- Phase: IMPLEMENT
- Entropy: void.entropy.sip(0.07)

## Mission
Integrate Stripe for subscription billing.

## Files to Create
impl/claude/protocols/billing/
├── __init__.py
├── stripe_client.py    # Stripe SDK wrapper
├── webhooks.py         # Webhook handlers
├── customers.py        # Customer management
├── subscriptions.py    # Subscription lifecycle
└── _tests/
    ├── __init__.py
    ├── test_webhooks.py
    ├── test_customers.py
    └── test_subscriptions.py

## Implementation Specs

### stripe_client.py
```python
import os
import stripe
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class StripeConfig:
    """Stripe configuration."""
    api_key: str
    webhook_secret: str
    price_ids: dict[str, str]  # tier -> stripe price ID

def get_stripe_config() -> StripeConfig:
    """Load Stripe config from environment."""
    return StripeConfig(
        api_key=os.environ.get("STRIPE_API_KEY", ""),
        webhook_secret=os.environ.get("STRIPE_WEBHOOK_SECRET", ""),
        price_ids={
            "pro_monthly": os.environ.get("STRIPE_PRICE_PRO_MONTHLY", ""),
            "pro_yearly": os.environ.get("STRIPE_PRICE_PRO_YEARLY", ""),
            "teams_monthly": os.environ.get("STRIPE_PRICE_TEAMS_MONTHLY", ""),
        },
    )

async def create_checkout_session(
    user_id: str,
    tier: str,
    success_url: str,
    cancel_url: str,
) -> str:
    """Create Stripe checkout session, return URL."""
    config = get_stripe_config()
    stripe.api_key = config.api_key

    session = stripe.checkout.Session.create(
        customer_email=_get_user_email(user_id),
        line_items=[{"price": config.price_ids[tier], "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"user_id": user_id, "tier": tier},
    )
    return session.url
```

### webhooks.py
```python
from fastapi import Request, HTTPException
import stripe
from impl.claude.protocols.licensing.tiers import LicenseTier

async def handle_webhook(request: Request) -> dict:
    """Process Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, get_stripe_config().webhook_secret
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")

    if event["type"] == "checkout.session.completed":
        await _handle_checkout_completed(event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        await _handle_subscription_cancelled(event["data"]["object"])
    elif event["type"] == "invoice.payment_failed":
        await _handle_payment_failed(event["data"]["object"])

    return {"status": "ok"}

async def _handle_checkout_completed(session: dict) -> None:
    """Upgrade user to purchased tier."""
    user_id = session["metadata"]["user_id"]
    tier = session["metadata"]["tier"]
    await upgrade_user_tier(user_id, LicenseTier[tier.upper()])
```

## Exit Criteria
- [ ] Stripe SDK wrapped with config
- [ ] Checkout session creation
- [ ] Webhook handlers for 4+ events
- [ ] Customer portal link generation
- [ ] Mocked tests (no live Stripe calls)
- [ ] 25+ tests passing

## Continuation
ledger.IMPLEMENT=touched → next=QA
```

---

### Track C: Soul API Service
**Agent 3 Focus**: FastAPI service for Soul-as-a-Service

```markdown
/hydrate
# Track C: Soul API Service

## Context
- Plan: plans/monetization/grand-initiative-monetization.md
- Phase: IMPLEMENT
- Entropy: void.entropy.sip(0.07)

## Mission
Create FastAPI service exposing K-gent Soul as API.

## Files to Create
impl/claude/protocols/api/
├── __init__.py
├── app.py              # FastAPI app
├── soul.py             # Soul endpoints
├── auth.py             # API key authentication
├── metering.py         # Usage tracking
├── models.py           # Request/response models
└── _tests/
    ├── __init__.py
    ├── test_app.py
    ├── test_soul.py
    ├── test_auth.py
    └── test_metering.py

## Implementation Specs

### app.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from impl.claude.protocols.api.soul import router as soul_router
from impl.claude.protocols.api.metering import MeteringMiddleware

app = FastAPI(
    title="kgents Soul API",
    description="Soul-as-a-Service: Personality-governed AI decisions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MeteringMiddleware)

app.include_router(soul_router, prefix="/v1/soul", tags=["soul"])

@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "version": "1.0.0"}
```

### soul.py
```python
from fastapi import APIRouter, Depends, HTTPException
from impl.claude.agents.k.soul import KgentSoul
from impl.claude.protocols.api.auth import get_api_key, ApiKeyData
from impl.claude.protocols.api.models import (
    GovernanceRequest, GovernanceResponse,
    DialogueRequest, DialogueResponse,
)

router = APIRouter()

@router.post("/governance", response_model=GovernanceResponse)
async def governance_check(
    request: GovernanceRequest,
    api_key: ApiKeyData = Depends(get_api_key),
) -> GovernanceResponse:
    """Check if action aligns with soul governance."""
    soul = await KgentSoul.from_api_key(api_key.key)

    result = await soul.deep_intercept(
        action=request.action,
        context=request.context,
        budget=request.budget,
    )

    return GovernanceResponse(
        approved=result.approved,
        reasoning=result.reasoning,
        alternatives=result.alternatives if not result.approved else [],
        confidence=result.confidence,
        tokens_used=result.tokens_used,
    )

@router.post("/dialogue", response_model=DialogueResponse)
async def dialogue(
    request: DialogueRequest,
    api_key: ApiKeyData = Depends(get_api_key),
) -> DialogueResponse:
    """Have a dialogue with the soul."""
    soul = await KgentSoul.from_api_key(api_key.key)

    mode = request.mode or "reflect"
    method = getattr(soul, mode)
    result = await method(request.prompt, budget=request.budget)

    return DialogueResponse(
        response=result.response,
        mode=mode,
        eigenvectors=result.eigenvectors.to_dict(),
        tokens_used=result.tokens_used,
    )
```

### auth.py
```python
from fastapi import Header, HTTPException
from dataclasses import dataclass
from impl.claude.protocols.licensing.tiers import LicenseTier

@dataclass
class ApiKeyData:
    key: str
    user_id: str
    tier: LicenseTier
    rate_limit: int

async def get_api_key(
    x_api_key: str = Header(..., alias="X-API-Key")
) -> ApiKeyData:
    """Validate API key and return user data."""
    if not x_api_key.startswith("kg_"):
        raise HTTPException(401, "Invalid API key format")

    # Look up key in database
    key_data = await lookup_api_key(x_api_key)
    if not key_data:
        raise HTTPException(401, "Invalid API key")

    return key_data
```

### metering.py
```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from datetime import datetime
from dataclasses import dataclass

@dataclass
class UsageRecord:
    api_key: str
    endpoint: str
    tokens_in: int
    tokens_out: int
    latency_ms: float
    timestamp: datetime

class MeteringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = datetime.utcnow()
        response = await call_next(request)
        latency = (datetime.utcnow() - start).total_seconds() * 1000

        # Extract API key and record usage
        api_key = request.headers.get("X-API-Key", "anonymous")
        await record_usage(UsageRecord(
            api_key=api_key,
            endpoint=request.url.path,
            tokens_in=int(request.headers.get("X-Tokens-In", 0)),
            tokens_out=int(response.headers.get("X-Tokens-Out", 0)),
            latency_ms=latency,
            timestamp=start,
        ))

        return response
```

## Exit Criteria
- [ ] FastAPI app running on localhost:8000
- [ ] /v1/soul/governance endpoint working
- [ ] /v1/soul/dialogue endpoint working
- [ ] API key authentication
- [ ] Usage metering middleware
- [ ] OpenAPI docs at /docs
- [ ] 40+ tests passing

## Continuation
ledger.IMPLEMENT=touched → next=QA
```

---

### Track D: Pro Crown Jewels
**Agent 4 Focus**: Gate and ship top 5 Crown Jewels

```markdown
/hydrate
# Track D: Pro Crown Jewels

## Context
- Plan: plans/monetization/grand-initiative-monetization.md
- Phase: IMPLEMENT
- Entropy: void.entropy.sip(0.07)

## Mission
Implement and gate the 5 highest-priority Crown Jewels.

## Crown Jewels to Implement

### CJ-1: `kg soul vibe` (Pro)
```python
# impl/claude/protocols/cli/handlers/soul.py

from impl.claude.protocols.licensing.gate import requires_tier
from impl.claude.protocols.licensing.tiers import LicenseTier

@handler("soul", "vibe")
@requires_tier(LicenseTier.PRO)
async def handle_soul_vibe(ctx: Context) -> None:
    """One-liner soul state from eigenvectors."""
    soul = await KgentSoul.from_context(ctx)
    eigens = await soul.get_eigenvectors()

    vibe_parts = []
    if eigens.joy > 0.7:
        vibe_parts.append("Playful")
    if eigens.categorical > 0.8:
        vibe_parts.append("Abstract")
    if eigens.aesthetic < 0.3:
        vibe_parts.append("Minimal")
    if eigens.ethical > 0.8:
        vibe_parts.append("Principled")

    vibe = ", ".join(vibe_parts) or "Neutral"
    ctx.console.print(f"[bold magenta]{vibe}[/bold magenta]")
```

### CJ-2: `kg whatif` (Pro)
```python
# impl/claude/protocols/cli/handlers/whatif.py

@handler("whatif")
@requires_tier(LicenseTier.PRO)
async def handle_whatif(ctx: Context, prompt: str, n: int = 3) -> None:
    """Show N alternative approaches to any problem."""
    uncertain = UncertainAgent()
    alternatives = await uncertain.generate_alternatives(prompt, n=n)

    for i, alt in enumerate(alternatives, 1):
        ctx.console.print(f"[bold]{i}. {alt.title}[/bold]")
        ctx.console.print(f"   {alt.description}")
        ctx.console.print(f"   Reality: {alt.reality_type} | Confidence: {alt.confidence:.0%}")
        ctx.console.print()
```

### CJ-3: `kg shadow` (Pro)
```python
# impl/claude/protocols/cli/handlers/shadow.py

@handler("shadow")
@requires_tier(LicenseTier.PRO)
async def handle_shadow(ctx: Context, target: str = "self") -> None:
    """Surface shadow content using H-jung."""
    jung = HgentJung()
    analysis = await jung.analyze_shadow(target)

    ctx.console.print("[bold]Shadow Analysis[/bold]")
    ctx.console.print(f"Persona claims: {analysis.persona}")
    ctx.console.print(f"Shadow reveals: {analysis.shadow}")
    ctx.console.print(f"Integration path: {analysis.integration}")
```

### CJ-4: `kg dialectic` (Pro)
```python
# impl/claude/protocols/cli/handlers/dialectic.py

@handler("dialectic")
@requires_tier(LicenseTier.PRO)
async def handle_dialectic(ctx: Context, thesis: str, antithesis: str) -> None:
    """Synthesize two concepts using H-hegel."""
    hegel = HgentHegel()
    synthesis = await hegel.synthesize(thesis, antithesis)

    ctx.console.print(f"[blue]Thesis:[/blue] {thesis}")
    ctx.console.print(f"[red]Antithesis:[/red] {antithesis}")
    ctx.console.print(f"[green]Synthesis:[/green] {synthesis.result}")
    ctx.console.print(f"Preserved: {synthesis.aufheben.preserved}")
    ctx.console.print(f"Negated: {synthesis.aufheben.negated}")
    ctx.console.print(f"Elevated: {synthesis.aufheben.elevated}")
```

### CJ-5: `kg approve` (Pro)
```python
# impl/claude/protocols/cli/handlers/approve.py

@handler("approve")
@requires_tier(LicenseTier.PRO)
async def handle_approve(ctx: Context, action: str) -> None:
    """Would Kent approve this action?"""
    soul = await KgentSoul.from_context(ctx)
    judge = JudgeAgent()

    values = await soul.get_eigenvectors()
    verdict = await judge.evaluate(action, principles=values)

    if verdict.approved:
        ctx.console.print("[green]WOULD APPROVE[/green]")
    else:
        ctx.console.print("[red]WOULD NOT APPROVE[/red]")
        for violation in verdict.violations:
            ctx.console.print(f"  Conflicts with: {violation}")
        if verdict.alternative:
            ctx.console.print(f"  Suggestion: {verdict.alternative}")
```

## Exit Criteria
- [ ] `kg soul vibe` working (Pro gated)
- [ ] `kg whatif` working (Pro gated)
- [ ] `kg shadow` working (Pro gated)
- [ ] `kg dialectic` working (Pro gated)
- [ ] `kg approve` working (Pro gated)
- [ ] Free users see upgrade prompt
- [ ] 50+ tests for commands

## Continuation
ledger.IMPLEMENT=touched → next=QA
```

---

## Parallel Execution Command

```bash
# Launch all 4 tracks simultaneously
# (Use separate terminal sessions or background processes)

# Terminal 1: Track A
claude -p "$(cat prompts/monetization-execution.md | grep -A200 'Track A:')"

# Terminal 2: Track B
claude -p "$(cat prompts/monetization-execution.md | grep -A200 'Track B:')"

# Terminal 3: Track C
claude -p "$(cat prompts/monetization-execution.md | grep -A200 'Track C:')"

# Terminal 4: Track D
claude -p "$(cat prompts/monetization-execution.md | grep -A200 'Track D:')"
```

---

## QA Phase (After IMPLEMENT)

```markdown
/hydrate
# QA ← IMPLEMENT

## Checklist
- [ ] All new code passes mypy strict
- [ ] All tests passing (target: 100+ new tests)
- [ ] Ruff formatting clean
- [ ] No hardcoded secrets
- [ ] Error messages include upgrade URLs
- [ ] API endpoints documented in OpenAPI
- [ ] License gate decorator tested

## Commands
```bash
cd impl/claude
uv run mypy protocols/licensing protocols/billing protocols/api
uv run ruff check protocols/licensing protocols/billing protocols/api
uv run pytest protocols/licensing protocols/billing protocols/api -v
```

## Exit
ledger.QA=touched → next=TEST
```

---

## TEST Phase

```markdown
/hydrate
# TEST ← QA

## Test Types Required
1. **Unit Tests**: Each function in isolation
2. **Integration Tests**: Stripe webhook → tier upgrade → feature unlock
3. **Property Tests**: License tier comparison properties
4. **E2E Tests**: Full checkout flow (mocked Stripe)

## Test Commands
```bash
# Unit tests
uv run pytest -m "unit" protocols/

# Integration tests
uv run pytest -m "integration" protocols/

# Property tests
uv run pytest -m "property" protocols/

# E2E tests
uv run pytest -m "e2e" protocols/
```

## Exit
ledger.TEST=touched → next=EDUCATE
```

---

## EDUCATE Phase

```markdown
/hydrate
# EDUCATE ← TEST

## Documentation Required
1. **API Reference**: `/docs` endpoint complete
2. **Upgrade Guide**: How to go from Free → Pro
3. **Integration Guide**: How to use Soul API
4. **Pricing Page Copy**: For landing page

## Files to Create
docs/
├── api-reference.md
├── upgrade-guide.md
├── integration-guide.md
└── pricing-copy.md

## Exit
ledger.EDUCATE=touched → next=MEASURE
```

---

## MEASURE Phase

```markdown
/hydrate
# MEASURE ← EDUCATE

## Metrics to Track
1. **Revenue**: MRR, ARR, conversion rates
2. **Usage**: API calls/day, tokens consumed
3. **Quality**: Error rates, p95 latency
4. **Engagement**: Commands/user/day

## Implementation
- Stripe dashboard for revenue
- Custom metrics dashboard for usage
- OTEL for quality metrics
- CLI telemetry for engagement

## Exit
ledger.MEASURE=touched → next=REFLECT
```

---

## REFLECT Phase

```markdown
/hydrate
# REFLECT ← MEASURE

## Questions to Answer
1. Which revenue stream converted fastest?
2. What features do users actually use?
3. What's blocking enterprise adoption?
4. What learnings go into meta.md?

## Outputs
- Epilogue: plans/_epilogues/2025-XX-XX-monetization-phase1.md
- Meta learnings: plans/meta.md (append)
- Next cycle seeds: plans/monetization/phase2.md

## Exit
ledger.REFLECT=touched → RE-METABOLIZE to Phase 2
```

---

## Success Criteria Summary

| Phase | Exit Criteria | Status |
|-------|--------------|--------|
| PLAN | Scope defined, 3+ revenue streams | DONE |
| RESEARCH | Market validated, 6 web searches | DONE |
| DEVELOP | Primitives designed, specs written | DONE |
| STRATEGIZE | Sequencing complete, risks identified | DONE |
| CROSS-SYNERGIZE | Compositions mapped | DONE |
| IMPLEMENT | 4 tracks complete, 200+ new tests | PENDING |
| QA | All quality gates pass | PENDING |
| TEST | Unit + Integration + E2E passing | PENDING |
| EDUCATE | Documentation complete | PENDING |
| MEASURE | Metrics framework live | PENDING |
| REFLECT | Learnings captured | PENDING |

---

*"The prompt is the plan. The plan is the execution. Ship it."*
