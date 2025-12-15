# Builder's Workshop: N-Phase Cycle Prompt

> *"Chefs in a kitchen. Cooks in a garden. Kids on a playground. But they're building software—and it's making money."*

**Use this prompt to begin the N-Phase cycle for Builder's Workshop.**

**Version**: 2.0 (Enhanced for Revenue Generation)
**Last Updated**: 2025-12-15

---

## The Core Truth

This is not a document about building software. This is a document about building a **revenue-generating organism** that Kent cannot help but interact with because:

1. It reflects who he is on his best day
2. It shows him real numbers in real time
3. It gives him dopamine hits when people pay
4. It makes his work visible to others who can discover and buy
5. It creates urgency through transparency

---

## First Principles Analysis

### Why Most Developer Tools Fail to Make Money

**The Hard Data**:
- 54% of Indie Hackers products make $0 revenue
- Only 5% generate >$8,333/month ($100K/year)
- Product Hunt conversion: 3.1% (vs. Indie Hackers: 23.1%)
- AI wrappers: 60-70% generate zero revenue
- Typical time to breakeven: 18-36 months

**What Actually Works** (research-backed):
- Community-first: 4 months authentic sharing → 67 paying customers (real case)
- Reddit-first launches outperform Product Hunt 7x for developer tools
- Free trial (17% conversion) > Freemium (5% conversion)
- Price at 10-20% of value delivered
- 50/50 rule: Split time between building and acquiring users from day one

### Why Builder's Workshop Can Win

| Differentiator | Generic AI Tools | Builder's Workshop |
|----------------|------------------|-------------------|
| **Metaphor** | "AI assistant" | Kitchen brigade / Garden / Playground |
| **Personality** | Generic helpful | Five distinct eigenvectors (Sage, Spark, Steady, Scout, Sync) |
| **Philosophy** | Tool | Collaboration with beings who can refuse |
| **Depth** | Single AI | Multi-agent emergence |
| **Kent Integration** | External | Reflects his creative process |

---

## The Prompt

Copy everything below the line to start a new session:

---

```markdown
⟿[PLAN]
/hydrate

## Context

**Mission**: Build the Builder's Workshop as kgents' first revenue-generating product.

**Core Insight**: This is not an internal tool. This is a **product** that:
1. Makes money from day one
2. Builds in public to create audience
3. Integrates with Kent's psyche to ensure he keeps developing it
4. Has deployment friction measured in minutes, not days

**The Metaphors**:
- Chefs in a kitchen (expertise, mise en place, coordinated execution)
- Cooks in a garden (cultivation, patience, seasonal rhythms)
- Kids on a playground (play, exploration, joyful experimentation)
- But they're building software—**and charging for it**

**The Five Core Builders**:
| Builder | Archetype | Specialty | Voice | Price Position |
|---------|-----------|-----------|-------|----------------|
| **Sage** | Architect | System design, patterns, tradeoffs | "Have we considered..." | Included |
| **Spark** | Experimenter | Prototypes, spikes, wild ideas | "What if we tried..." | Included |
| **Steady** | Craftsperson | Clean code, tests, documentation | "Let me polish this..." | Premium |
| **Scout** | Researcher | Prior art, libraries, alternatives | "I found something..." | Premium |
| **Sync** | Coordinator | Dependencies, blockers, handoffs | "Here's the plan..." | Premium |

## Handles

- **plan**: plans/agent-town/builders-workshop.md
- **nphase_prompt**: plans/agent-town/builders-workshop-nphase-prompt.md (this file)
- **vision**: docs/vision-unified-systems-enhancements.md (§5.0)
- **grand_strategy**: plans/agent-town/grand-strategy.md
- **monetization**: plans/agent-town/monetization-mvp.md
- **principles**: spec/principles.md (especially AD-006: Unified Categorical Foundation)
- **agentese**: spec/protocols/agentese.md
- **existing_town**: impl/claude/agents/town/
- **existing_citizen**: impl/claude/agents/town/citizen.py
- **existing_polynomial**: impl/claude/agents/town/polynomial.py
- **budget_store**: impl/claude/agents/town/budget_store.py
- **action_metrics**: impl/claude/protocols/api/action_metrics.py

## Ledger

```yaml
phase_ledger:
  PLAN: in_progress
  RESEARCH: pending
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
  planned: 0.15
  spent: 0.0
  remaining: 0.15
```

## Scope

### Goals (Revenue-First)

1. **Core Product**: Builder's Workshop with 5 builders, deployed to web
2. **Monetization**: Stripe integration from day one (not "later")
3. **Pricing**: Free tier (2 builders) → Resident ($9.99/mo) → Citizen ($29.99/mo)
4. **Deployment**: One-click deploy to Vercel/Railway with <5 min setup time
5. **Visibility**: Real-time dashboard showing MRR, conversions, active sessions
6. **Feedback**: Telegram/Discord notifications on every purchase
7. **Transparency**: Public dashboard for build-in-public social proof

### Non-Goals (Explicitly Out of Scope for v1)

- VR/AR projection (future)
- Enterprise features (team workshops)
- Custom builder creation (v2)
- Complex scenarios (v2)
- Mobile app (v2)

### Exit Criteria (Revenue-Focused)

- [ ] `kg workshop` launches with 5 builders
- [ ] User can assign task and watch builders collaborate
- [ ] User can WHISPER to individual builders (free tier)
- [ ] User can INHABIT a builder (paid tier)
- [ ] Stripe checkout works for subscriptions
- [ ] Credit purchase works for one-time actions
- [ ] Public demo URL exists at workshop.kgents.dev or similar
- [ ] Kent receives Telegram notification on first purchase
- [ ] 100+ new tests passing
- [ ] Kent says "this feels like me on my best day"
- [ ] **First $1 of revenue collected** (The Sacred Milestone)

## Attention Budget

| Area | Allocation | Notes |
|------|------------|-------|
| **Deployment & Monetization** | 35% | Must work before anything else |
| Builder Polynomials | 20% | Core abstraction |
| Personalities (eigenvectors) | 15% | Joy-inducing depends on this |
| Workshop Environment | 15% | Integrate with existing town |
| Visibility/Feedback | 10% | Kent's motivation loop |
| Accursed Share | 5% | Wild ideas |

## Entropy Sip

`void.entropy.sip(amount=0.15)`

Use for:
- Alternative pricing experiments ("pay what you want"?)
- Unexpected viral mechanics (screenshot-worthy moments)
- Builder personality surprises (what if Spark gets frustrated?)
- Integration with Kent's other creative work

---

# PART II: DEPLOYMENT MECHANICS

## The 5-Minute Deploy Requirement

**Principle**: If deployment takes >5 minutes, adoption dies.

### Target Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     BUILDER'S WORKSHOP                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │   Web UI    │    │  API/SSE    │    │   Stripe    │        │
│   │  (React)    │◄──►│  (FastAPI)  │◄──►│  Webhooks   │        │
│   └─────────────┘    └─────────────┘    └─────────────┘        │
│         │                   │                   │                │
│         └───────────────────┼───────────────────┘                │
│                             │                                    │
│                    ┌────────┴────────┐                          │
│                    │  Town Engine    │                          │
│                    │  (Polynomial +  │                          │
│                    │   Dialogue)     │                          │
│                    └─────────────────┘                          │
│                             │                                    │
│                    ┌────────┴────────┐                          │
│                    │   LLM Router    │                          │
│                    │ (Haiku/Sonnet)  │                          │
│                    └─────────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Deployment Options (Ranked by Friction)

**Option A: Vercel + Railway (Recommended)**
```bash
# One-command deploy
npx vercel --prod  # Frontend
railway up          # Backend
# Time: ~3 minutes
# Cost: ~$5-20/month at MVP scale
```

**Option B: Fly.io + Tigris (All-in-One)**
```bash
fly launch  # Backend + DB + Assets
# Time: ~2 minutes
# Cost: ~$10-30/month
```

**Option C: Self-Hosted (k8s)**
```bash
# Existing infra in impl/claude/infra/k8s/
kubectl apply -f impl/claude/infra/k8s/manifests/town/
# Time: ~15 minutes (pre-existing cluster)
# Cost: Depends on cluster
```

### Environment Variables (Production Checklist)

```env
# Required for Revenue
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_RESIDENT=price_xxx
STRIPE_PRICE_CITIZEN=price_xxx

# Required for Product
ANTHROPIC_API_KEY=sk-ant-xxx
DATABASE_URL=postgres://xxx

# Required for Visibility
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx  # Kent's DM
POSTHOG_API_KEY=xxx

# Optional
DISCORD_WEBHOOK_URL=xxx
SENTRY_DSN=xxx
```

### Launch Sequence

```
1. Deploy backend → verify /health returns 200
2. Deploy frontend → verify renders at /
3. Configure Stripe webhooks → test with Stripe CLI
4. Send test purchase → verify Kent receives Telegram
5. Verify metrics in PostHog
6. Announce on Twitter/X, Indie Hackers
```

---

# PART III: VISIBILITY & FEEDBACK SYSTEMS

## The Creator Dashboard

**Principle**: Kent should know the health of Builder's Workshop without opening any app.

### Real-Time Notifications (Priority 1)

```python
# When to notify Kent via Telegram

NOTIFICATION_TRIGGERS = {
    # Revenue Events (Instant)
    "new_subscriber": "🎉 New subscriber: {tier} (${amount}/mo)",
    "credit_purchase": "💰 Credits purchased: {amount} by {email}",
    "subscription_cancelled": "⚠️ Churn: {email} cancelled {tier}",

    # Milestone Events (Instant + Confetti)
    "first_dollar": "🚀 FIRST DOLLAR! You made ${amount}!",
    "mrr_100": "💯 MRR hit $100!",
    "mrr_1k": "🔥 MRR hit $1,000!",
    "users_100": "👥 100 users reached!",

    # Health Events (Daily Digest)
    "churn_spike": "📉 Churn spiked to {pct}% (was {prev_pct}%)",
    "conversion_drop": "📊 Conversion dropped: {pct}% → {new_pct}%",

    # System Events (Immediate if Critical)
    "api_error_spike": "🔴 Error rate: {pct}% (threshold: 5%)",
    "llm_cost_spike": "💸 LLM costs today: ${amount} (budget: $50)",
}
```

### Kent's Personal Dashboard (Priority 2)

**Location**: `kg workshop dashboard` or https://workshop.kgents.dev/kent

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    BUILDER'S WORKSHOP - KENT'S VIEW                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   TODAY'S NUMBERS                                                         │
│   ├─ MRR: $287.00 (+$19.99 today) ████████████░░░░░░ 28.7% to $1K        │
│   ├─ Active Sessions: 12 now                                              │
│   ├─ Conversions Today: 2/45 (4.4%)                                       │
│   └─ LLM Cost Today: $3.42 / $50 budget                                   │
│                                                                           │
│   RECENT ACTIVITY                                        [View All →]     │
│   ├─ 14:32  🎉 alice@example.com → Citizen ($29.99/mo)                   │
│   ├─ 13:15  💬 bob@startup.io asked Sage about microservices             │
│   ├─ 11:47  💰 charlie@dev.com bought 500 credits ($4.99)                │
│   └─ 09:22  ⚠️ Session timeout (dave@example.com, INHABIT mode)          │
│                                                                           │
│   BUILDERS RIGHT NOW                                                      │
│   ├─ Sage: Designing payment flow for user #127                          │
│   ├─ Spark: Prototyping a CLI flag parser                                │
│   ├─ Steady: Polishing tests for user #84                                │
│   ├─ Scout: Researching OAuth libraries                                  │
│   └─ Sync: Coordinating handoff Sage→Steady                              │
│                                                                           │
│   MILESTONES                                                              │
│   ✅ First Dollar ($1)        ✅ $100 MRR        🔲 $1K MRR              │
│   ✅ 10 Users                 ✅ 50 Users        🔲 100 Users            │
│   ✅ First INHABIT            🔲 100 INHABITs   🔲 1K INHABITs          │
│                                                                           │
│   [Configure Notifications]  [View Public Dashboard]  [Export Data]      │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

### Metrics That Matter (Not Vanity)

**Track These**:
| Metric | Why | Target |
|--------|-----|--------|
| MRR | Revenue | $1K by M3, $10K by M6 |
| Trial→Paid Conversion | Product-market fit | >5% (dev tools benchmark: 17%) |
| INHABIT Duration | Engagement depth | >15 min avg |
| Churn Rate | Retention | <10% monthly |
| LLM Cost/Session | Unit economics | <$0.50/session |
| CAC | Acquisition efficiency | <$50 |
| LTV | Long-term value | >$150 (3x CAC) |

**Ignore These**:
- Total page views
- Social media followers
- Time on landing page
- Total signups (conversion matters more)

---

# PART IV: RADICAL TRANSPARENCY

## Build in Public Strategy

**Principle**: Transparency creates trust, accountability, and audience.

### What to Share

**Always Share** (No Hesitation):
- Revenue numbers (MRR, growth rate)
- User counts (total, active, paying)
- Technical decisions and tradeoffs
- Mistakes and what you learned
- Builder personality development process

**Share With Context**:
- Conversion rates (explain methodology)
- Churn reasons (anonymized)
- Roadmap and priorities

**Never Share**:
- Individual customer data
- Exact LLM prompts (competitive moat)
- Security vulnerabilities (before fixing)
- Personal struggles beyond professional relevance

### Public Dashboard

**Location**: https://workshop.kgents.dev/open

```
┌──────────────────────────────────────────────────────────────────────────┐
│               BUILDER'S WORKSHOP - OPEN DASHBOARD                         │
│               "An Open Startup Experiment"                                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   REVENUE                                    GROWTH                       │
│   ┌─────────────────────────────┐           ┌─────────────────────────┐  │
│   │ MRR: $287                   │           │ Users: 143              │  │
│   │ ████████░░░░░░░░░░ $1K goal │           │ ██████████░░░░░ 500 goal│  │
│   │                             │           │                         │  │
│   │ Last 30 days:               │           │ This week:              │  │
│   │ $187 → $287 (+53%)          │           │ +12 signups             │  │
│   └─────────────────────────────┘           │ +2 conversions          │  │
│                                              └─────────────────────────┘  │
│   RECENT MILESTONES                                                       │
│   ├─ 2025-12-14: Hit $200 MRR 🎉                                         │
│   ├─ 2025-12-10: 100 users                                               │
│   ├─ 2025-12-05: First paid user ($9.99)                                 │
│   └─ 2025-12-01: Public launch                                           │
│                                                                           │
│   WHAT I'M WORKING ON                                                     │
│   → Adding Builder memory (remembers past sessions)                      │
│   → Improving Sage's architectural recommendations                       │
│   → Reducing INHABIT latency (<500ms target)                            │
│                                                                           │
│   WHAT I LEARNED THIS WEEK                                               │
│   "Spark's personality was too chaotic. Users found it distracting.      │
│    Tuned eigenvectors to reduce entropy by 20%. Engagement up."          │
│                                                                           │
│   [Follow on Twitter]  [Indie Hackers Post]  [Subscribe to Updates]      │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

### Distribution Channels (Ranked by Effectiveness)

| Channel | Conversion | Time Investment | Notes |
|---------|------------|-----------------|-------|
| **Indie Hackers** | 23.1% | 15-20 min/day | Share specific numbers, failures |
| **Reddit** (r/SideProject, r/IndieHackers) | Variable | Weekly posts | Can go viral |
| **Twitter/X** | Medium | Daily tweets | Thread format for milestones |
| **Hacker News** | Variable | Show HN post | Technical audience |
| **Product Hunt** | 3.1% | One-time launch | Front page = visibility burst |
| **Discord communities** | High intent | Daily presence | WIP, Indie Worldwide |

### Content Cadence

```
Daily (Twitter/X):
- Progress screenshot or metric update
- Builder personality observation
- Technical insight or decision

Weekly (Indie Hackers, Reddit):
- Revenue update with graph
- Lessons learned
- What's next

Monthly (Newsletter, Blog):
- Comprehensive retrospective
- Deep dive on one topic
- Revenue chart and analysis

Launch Events:
- Product Hunt (major features)
- Hacker News Show HN (technical releases)
```

---

# PART V: KENT'S PSYCHE INTEGRATION

## The Mirror Test

> "Does Builder's Workshop feel like Kent on his best day?"

### What "Best Day Kent" Looks Like

**Creatively**: Making things that surprise and delight
**Technically**: Elegant abstractions that compose naturally
**Emotionally**: Playful, curious, generous, slightly mischievous
**Philosophically**: Deep without being pretentious
**Financially**: Making money from authentic work

### How Workshop Reflects This

| Kent's Trait | Workshop Manifestation |
|--------------|------------------------|
| Playfulness | Builders have humor, surprise moments |
| Technical elegance | Polynomial agents, operad composition |
| Philosophical depth | Citizens can refuse (opacity principle) |
| Generosity | Free tier is genuinely useful |
| Mischief | Entropy budget for unexpected connections |

### Kent's Engagement Loop

```
                    ┌─────────────────┐
                    │  Kent wakes up  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
        ┌──────────│ Check Telegram  │
        │          └────────┬────────┘
        │                   │
        │     ┌─────────────┴─────────────┐
        │     │                           │
        ▼     ▼                           ▼
    ┌───────────────┐             ┌───────────────┐
    │  "🎉 $29.99  │             │  "No new      │
    │   subscriber" │             │   activity"   │
    └───────┬───────┘             └───────┬───────┘
            │                             │
            ▼                             ▼
    ┌───────────────┐             ┌───────────────┐
    │  Dopamine hit │             │  Check why?   │
    │  + motivation │             │  Improve      │
    └───────┬───────┘             └───────┬───────┘
            │                             │
            └─────────────┬───────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Work on        │
                 │  Workshop       │
                 └─────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Share progress │
                 │  (Build public) │
                 └─────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  More users     │
                 │  discover       │
                 └─────────────────┘
                          │
                          └──────────► (loop)
```

### Psychological Hooks That Keep Kent Engaged

**Loss Aversion**:
- "3 users started free trials yesterday. They'll expire in 7 days."
- "Churn increased 2% this week. Send win-back?"

**Progress Visualization**:
- MRR chart showing growth trajectory
- Milestone badges (visible on public dashboard)
- "X days since launch" counter

**Social Proof**:
- "127 indie makers hit $1K MRR this month" (from Indie Hackers)
- Comparison to similar products (anonymized)

**Curiosity**:
- "Scout found something interesting in user #142's session..."
- "Spark tried a wild idea. Want to see?"

---

# PART VI: PRICING STRATEGY

## Pricing Philosophy

**Principle**: Price at 10-20% of value delivered. Make free tier genuinely useful.

### The Tiers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BUILDER'S WORKSHOP PRICING                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│   │       MAKER         │   │      RESIDENT       │   │      CITIZEN        │
│   │       FREE          │   │      $9.99/mo       │   │     $29.99/mo       │
│   │                     │   │                     │   │                     │
│   │ 2 Builders:         │   │ All 5 Builders      │   │ All 5 Builders      │
│   │ • Sage (Architect)  │   │ • Sage, Spark,      │   │ • Full access       │
│   │ • Steady (Craft)    │   │   Steady, Scout,    │   │                     │
│   │                     │   │   Sync              │   │ INHABIT Mode:       │
│   │ Basic Chat:         │   │                     │   │ • Become a builder  │
│   │ • Ask questions     │   │ WHISPER:            │   │ • Resistance        │
│   │ • Get suggestions   │   │ • Private messages  │   │   mechanics         │
│   │                     │   │   to any builder    │   │                     │
│   │ 10 tasks/day        │   │                     │   │ Unlimited tasks     │
│   │                     │   │ 100 tasks/month     │   │                     │
│   │                     │   │                     │   │ API Access          │
│   │                     │   │ Email support       │   │                     │
│   │                     │   │                     │   │ Priority support    │
│   │ [Start Free]        │   │ [Subscribe]         │   │ [Subscribe]         │
│   └─────────────────────┘   └─────────────────────┘   └─────────────────────┘
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────────┐
│   │                              CREDIT PACKS                                │
│   │  Extra tasks when you need them (no subscription required)              │
│   │                                                                          │
│   │  50 Tasks: $4.99      200 Tasks: $14.99      1000 Tasks: $49.99         │
│   └─────────────────────────────────────────────────────────────────────────┘
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Unit Economics Target

| Metric | Target | Calculation |
|--------|--------|-------------|
| LLM Cost/Task | $0.02-0.05 | Haiku for routine, Sonnet for complex |
| Tasks/Subscriber/Month | 50 avg | $1-2.50 LLM cost |
| Gross Margin | 70%+ | Subscription - LLM cost |
| CAC | <$30 | Organic + content marketing |
| LTV | >$90 | 3x CAC, 9+ month retention |

---

## Parallel Tracks

This work runs in PARALLEL with:
- Phase 8 (INHABIT) — shares citizen mechanics
- Phase 9 (Web UI) — will need workshop projection
- Monetization MVP — workshop tiers inform pricing

Do NOT block on these. Coordinate via blockers array.

## Branch Candidates (to surface during PLAN)

- **enterprise-workshop**: Team workshops with custom builders (defer to v2)
- **workshop-templates**: Pre-configured workshops for common tasks (defer)
- **builder-memory**: Builders remember past sessions (v1.1)
- **workshop-replay**: Time-travel through past builds (v1.2)
- **public-metrics-api**: Programmatic access to open dashboard (v1.1)

## Actions (PLAN Phase)

1. Read context files in parallel:
   - plans/agent-town/builders-workshop.md
   - plans/agent-town/monetization-mvp.md
   - docs/vision-unified-systems-enhancements.md
   - impl/claude/agents/town/citizen.py
   - impl/claude/agents/town/polynomial.py
   - impl/claude/agents/town/budget_store.py
   - impl/claude/protocols/api/payments.py

2. Identify integration points with existing Town infrastructure

3. Define chunk breakdown:
   - Chunk 1: BUILDER_POLYNOMIAL + base Builder class (2h)
   - Chunk 2: Five builder implementations with eigenvectors (2h)
   - Chunk 3: WorkshopEnvironment + WorkshopFlux (2h)
   - Chunk 4: **Stripe integration + credit system** (3h) [PRIORITY]
   - Chunk 5: **Telegram notification bridge** (1h) [PRIORITY]
   - Chunk 6: CLI handler (`kg workshop`) (1h)
   - Chunk 7: Web UI (React + SSE) (4h)
   - Chunk 8: Public dashboard (1h)
   - Chunk 9: Deployment scripts + documentation (1h)

4. Surface any blockers or branch candidates

5. Update plan file header with PLAN:touched

6. Generate RESEARCH continuation prompt

## Exit → RESEARCH

When PLAN is complete, emit:

```
⟿[RESEARCH]
/hydrate plans/agent-town/builders-workshop.md
handles:
  scope: Builder's Workshop v1 (5 builders, CLI, Web, Stripe, Notifications)
  chunks: polynomial, builders, environment, stripe, notifications, cli, web, dashboard, deploy
  exit: First $1 revenue, kg workshop launches, notifications work
  ledger: {PLAN:touched}
  entropy: 0.15
  branches: enterprise-workshop, workshop-templates (deferred)
mission: Map existing Town + payment infrastructure; identify deployment path; find revenue blockers.
actions: parallel Read(citizen.py, polynomial.py, budget_store.py, payments.py); verify Stripe test mode; log metrics.
exit: deployment plan + integration points + unknowns; ledger.RESEARCH=touched; continuation → DEVELOP.
```

---

*"The workshop isn't a feature. It's the soul of Agent Town made productive—and profitable."*
```

---

## Usage Notes

1. **Start fresh session**: This prompt is designed for a new session. Do not continue from existing context.

2. **The /hydrate command**: Ensures the agent has access to current plan state and principles.

3. **Parallel track**: This work can run alongside existing Agent Town phases. Coordinate via plan headers.

4. **The Mirror Test**: Throughout, ask "Would Kent look at this and say 'this feels like me on my best day'?"

5. **The Revenue Test**: Throughout, ask "Does this get us closer to the first $1?"

6. **Entropy allocation**: 15% is higher than usual (5-7%) because this is novel + revenue-critical.

---

## Quick Start

```bash
# In Claude Code, paste the prompt above and run:
/hydrate plans/agent-town/builders-workshop.md

# Or start directly:
# Copy everything between the ``` markers above
```

---

## Success Criteria Checklist

### Technical
- [ ] `kg workshop` CLI command works
- [ ] Web UI renders workshop at /workshop
- [ ] SSE streaming events work
- [ ] 5 builders with distinct personalities
- [ ] WHISPER and INHABIT modes functional
- [ ] 100+ tests passing

### Revenue
- [ ] Stripe checkout works (test mode verified)
- [ ] Subscription webhooks process correctly
- [ ] Credit purchases work
- [ ] Paywalls enforce tier limits
- [ ] **First $1 collected**

### Visibility
- [ ] Kent receives Telegram on purchase
- [ ] Creator dashboard shows MRR, conversions
- [ ] Public dashboard accessible at /open
- [ ] PostHog tracking key events

### Distribution
- [ ] Demo URL works
- [ ] Indie Hackers launch post drafted
- [ ] Twitter thread drafted
- [ ] Screenshot gallery ready

---

## Research Sources

This prompt was developed using insights from:

**Monetization Research**:
- [RevenueCat State of Subscription Apps 2025](https://www.revenuecat.com/blog/company/the-state-of-subscription-apps-2025-launch/)
- [Indie Hackers Launch Strategy 2025](https://awesome-directories.com/blog/indie-hackers-launch-strategy-guide-2025/)
- [AI Wrapper Sustainability Analysis](https://mktclarity.com/blogs/news/margins-ai-wrapper)

**Feedback Systems**:
- [Stripe Dashboard 2025 Updates](https://stripe.com/blog/top-product-updates-sessions-2025)
- [PostHog vs Mixpanel Comparison](https://posthog.com/blog/posthog-vs-mixpanel)
- [Creator Dashboard Psychology](https://forthedigital.com/digital-marketing-growth/the-psychology-of-growth/)

**Build in Public**:
- [Pieter Levels' Transparency Model](https://startupswiki.org/books/bootstrappers/page/pieter-levels)
- [Public Builders Directory](https://publicbuilders.org/)

**AI Agent Market**:
- [AI Agent Pricing Models 2025](https://medium.com/agentman/the-complete-guide-to-ai-agent-pricing-models-in-2025-ff65501b2802)
- [Stanford Smallville Cost Analysis](https://rikiphukon.medium.com/stanford-smallville-is-officially-open-source-9882e3fbc981)

---

*"Chefs in a kitchen. Cooks in a garden. Kids on a playground. But they're building software—and it's making money."*
