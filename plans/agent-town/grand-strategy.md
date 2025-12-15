---
path: plans/agent-town/grand-strategy
status: active
progress: 0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town-phase8-inhabit
  - agent-town-phase9-web
  - monetization/agent-town-saas
  - deployment/agent-town-live
session_notes: |
  GRAND STRATEGY synthesized from:
  - spec/principles.md (all 7 principles + meta-principles)
  - External research (Stanford Smallville, Punchdrunk, AI monetization 2025)
  - Kent's vision (_focus.md: "MAKE MONEY WITH AGENT TOWN!!!!")
  - Existing infrastructure (830 tests, Phase 7 LLM dialogue complete)
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
  planned: 0.15
  spent: 0.05
  remaining: 0.10
---

# Agent Town Grand Strategy: The Civilizational Engine

> *"The simulation isn't a game. It's a seance. We are not building. We are summoning."*

---

## Executive Summary

Agent Town is kgents' **soul converging point**—the Grand Narrative that transforms abstract category theory into visceral, monetizable, joy-inducing experience. This strategy synthesizes:

1. **Research heritage**: Stanford Smallville, Punchdrunk Sleep No More, AI companion market ($120M in 2025)
2. **kgents principles**: Tasteful, Curated, Ethical, Joy-Inducing, Composable, Heterarchical, Generative
3. **Technical foundation**: 830 tests, polynomial agents, operads, LLM dialogue, streaming infrastructure
4. **Kent's vision**: Westworld-like simulation park with infinite holographic depth

**The Bet**: Agent Town can be kgents' first revenue-generating product within 6 months, scaling from $0 to $10K MRR through pay-to-zoom depth and companion subscriptions.

---

## Part I: The Vision

### 1.1 What Is Agent Town?

Agent Town is a **civilizational simulation engine** where AI citizens live, interact, form relationships, and generate emergent drama. Users can:

- **OBSERVE**: Watch the town unfold like a nature documentary
- **WHISPER**: Send private messages to individual citizens
- **INHABIT**: Merge with a citizen, experiencing through their eyes
- **INTERVENE**: Inject world events that change the simulation
- **BRANCH**: Fork reality at any point, explore "what if" timelines

Unlike games with scripted NPCs, Agent Town citizens have:
- **Memory**: They remember past interactions and relationships
- **Personality**: 7D eigenvector space (warmth, curiosity, trust, creativity, patience, resilience, ambition)
- **Cosmotechnics**: Each archetype embodies a distinct worldview
- **Opacity**: The right to remain unknowable (Glissant's principle)

### 1.2 The Heritage

| Paper/Work | Contribution | Agent Town Integration |
|------------|--------------|------------------------|
| [Stanford Smallville](https://dl.acm.org/doi/fullHtml/10.1145/3586183.3606763) | Memory stream + reflection → emergence | M-gent + DialogueEngine |
| [Punchdrunk Sleep No More](https://www.punchdrunk.com/work/sleep-no-more-new-york/) | 100-room immersive space, masked observers | MESA/LENS UI, masked user mode |
| [Virtual Protocol Westworld](https://virtual-protocol.github.io/westworld-ai/) | Roblox autonomous agents, "find the bandit" | Mystery scenarios, goal-driven citizens |
| [ChatDev](https://arxiv.org/abs/2307.07924) | Language as unifying bridge | AGENTESE liturgy |
| [Altera](https://arxiv.org/abs/2411.00114) | 1000+ agent civilizations | Scale trajectory |

### 1.3 The Three Truths (from spec/principles.md)

| Truth | Meaning | Agent Town Implementation |
|-------|---------|---------------------------|
| **Tasteful** | Each citizen serves a clear purpose | 5 archetypes, not 50; quality over quantity |
| **Joy-Inducing** | Personality matters, delight encouraged | Citizens have humor, warmth, surprise |
| **Composable** | Agents are morphisms; f >> g works | TownOperad defines valid compositions |

---

## Part II: The Experience Design

### 2.1 The Four Gardens (from visionary-ux-flows.md)

Agent Town manifests across four interconnected interfaces:

```
                    ┌─────────────────────────────────────────────┐
                    │              THE UNIFIED SUBSTRATE           │
                    │         (Signal[T], Computed, Effect)        │
                    └──────────────────────┬──────────────────────┘
                                           │
          ┌────────────────┬───────────────┼───────────────┬────────────────┐
          │                │               │               │                │
          ▼                ▼               ▼               ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │   CLI    │    │  Marimo  │    │  Textual │    │   Web    │    │   VR     │
    │  (ASCII) │    │(notebook)│    │  (TUI)   │    │  (React) │    │ (future) │
    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

| Garden | Description | Target User |
|--------|-------------|-------------|
| **CLI (Terminal)** | ASCII art, `kg town observe` | Developers, power users |
| **Marimo (Notebook)** | Interactive cells, reactive widgets | Data scientists, educators |
| **Textual (TUI)** | Rich terminal dashboard | Operators, SREs |
| **Web (Browser)** | React + Pixi.js/D3, public demo | General audience, paying users |

### 2.2 The INHABIT Experience (Key Differentiator)

Inspired by [Punchdrunk's masked observer experience](https://emshort.blog/2018/03/20/worldbuilding-in-immersive-theatre/):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INHABIT MODE: Becoming Clara                         │
│                                                                             │
│   You are Clara, the Scholar. Your eyes are her eyes.                       │
│   Her memories surface as yours. Her values constrain your choices.         │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ [Clara's Inner Voice]                                                │   │
│   │                                                                       │   │
│   │ The Builder speaks of foundations, but what of the questions         │   │
│   │ beneath? Every structure rests on assumptions...                      │   │
│   │                                                                       │   │
│   │ Your curiosity tugs toward the old well. Something happened there.   │   │
│   │ Eve knows. Eve always knows.                                         │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   [What do you do?]                                                         │
│   > _                                                                       │
│                                                                             │
│   Note: Clara may RESIST actions that violate her curiosity principle.      │
│   Forcing her costs extra tokens and strains your relationship.             │
│                                                                             │
│   [E]xit to Observer  [M]emory  [R]elationships  [?]Help                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key mechanic**: The citizen can **refuse** user suggestions that violate their personality eigenvectors. This is not a game where you control the character—it's a collaboration where you influence but don't dominate.

### 2.3 The LOD Pyramid (Pay-to-Zoom)

Level of Detail determines both information richness AND cost:

| LOD | Name | Content | Model | Cost/View |
|-----|------|---------|-------|-----------|
| 0 | **Silhouette** | Name, location, emoji | Cache | FREE |
| 1 | **Posture** | Action, mood, facing | Cache | FREE |
| 2 | **Dialogue** | Recent speech, greetings | Haiku | $0.001 |
| 3 | **Memory** | Active memories, current goals | Haiku | $0.01 |
| 4 | **Psyche** | Eigenvectors, tensions, desires | Sonnet | $0.05 |
| 5 | **Abyss** | *The irreducible mystery* | Opus | $0.50 |

**LOD 5 Philosophy** (Glissant's Opacity):
> "Clara notices your gaze. She doesn't speak. Something moves behind her eyes that you cannot name. This is not concealment. This is her right to remain irreducible."

The deepest zoom reveals **mystery, not clarity**. This is philosophically grounded AND economically brilliant—users pay the most to encounter the unknowable.

### 2.4 Time Travel & Branching

Inspired by [Redux DevTools time-travel debugging](https://medium.com/the-web-tub/time-travel-in-react-redux-apps-using-the-redux-devtools-5e94eba5e7c0):

```
Timeline: ════════════════════════════════════════════════════════════════
          │ Day 1    │ Day 2    │ Day 3    │ Day 4    │ Day 5    │
          │          │    ★     │          │    ▼     │          │
          │          │ Branch   │          │ [NOW]    │          │
          └──────────┴──────────┴──────────┴──────────┴──────────┘

★ Branch Point: "What if Bob had rejected Alice's proposal?"

[J]ump to action  [S]kip action  [R]eplay from start  [B]ranch here
```

**Branching Universes** enable:
- Counterfactual exploration ("what if?")
- A/B testing social dynamics
- Educational scenarios (history, ethics)
- Entertainment (romance routes, mystery solutions)

---

## Part III: Monetization Strategy

### 3.1 Market Opportunity

The AI companion app market is [projected to reach $120M in 2025](https://techcrunch.com/2025/08/12/ai-companion-apps-on-track-to-pull-in-120m-in-2025/), with [revenue per download doubling](https://www.webpronews.com/ai-companion-apps-surge-to-120m-revenue-by-2025-amid-growth-boom/) from $0.52 to $1.18. The broader AI agent market is expected to reach [$50-216B by 2030-2035](https://www.aalpha.net/blog/how-to-monetize-ai-agents/).

Key insight: [35% of successful apps now use hybrid monetization](https://www.revenuecat.com/blog/company/the-state-of-subscription-apps-2025-launch/)—subscriptions + consumables.

### 3.2 The Three Revenue Streams

| Stream | Model | Target | Rationale |
|--------|-------|--------|-----------|
| **Observer Pass** | Subscription | $9.99/mo | Unlimited LOD 0-2, 100 LOD 3 views/month |
| **Token Packs** | Consumable | $4.99-$49.99 | Pay-per-view for LOD 4-5, branching |
| **Premium Towns** | One-time | $29.99 | Pre-crafted scenarios with mystery/drama |

### 3.3 Pricing Tiers

| Tier | Price | Includes |
|------|-------|----------|
| **Free (Tourist)** | $0 | LOD 0-1 only, observe public demo town |
| **Resident** | $9.99/mo | Unlimited LOD 0-2, 100 LOD 3/mo, 1 personal town |
| **Citizen** | $29.99/mo | Unlimited LOD 0-3, 50 LOD 4/mo, 5 towns, INHABIT mode |
| **Founder** | $99.99/mo | Unlimited all LOD, unlimited towns, API access, priority support |

### 3.4 Token Economics

Following [Adobe's Firefly credit model](https://blog.crossmint.com/monetize-ai-agents/):

| Pack | Credits | Price | Cost/Credit |
|------|---------|-------|-------------|
| Starter | 500 | $4.99 | $0.010 |
| Explorer | 2,000 | $14.99 | $0.0075 |
| Adventurer | 10,000 | $49.99 | $0.005 |

**Credit Costs**:
- LOD 3 view: 10 credits
- LOD 4 view: 50 credits
- LOD 5 view: 200 credits
- Branch creation: 100 credits
- INHABIT session (10 min): 50 credits

### 3.5 Revenue Projections (Conservative)

| Month | MAU | Conversion | MRR |
|-------|-----|------------|-----|
| M1 | 100 | 5% | $500 |
| M3 | 500 | 8% | $4,000 |
| M6 | 2,000 | 10% | $20,000 |
| M12 | 10,000 | 12% | $120,000 |

**Path to $10K MRR**: 500 users × 10% conversion × $20 ARPU = $10K

---

## Part IV: Technical Architecture

### 4.1 The Categorical Foundation (AD-006)

Per spec/principles.md, Agent Town instantiates the unified pattern:

```python
# Layer 1: Polynomial Agent
CITIZEN_POLYNOMIAL = PolyAgent(
    positions=frozenset(["IDLE", "SOCIALIZING", "WORKING", "REFLECTING", "RESTING"]),
    directions=citizen_directions,
    transition=citizen_transition,
)

# Layer 2: Operad (Composition Grammar)
TOWN_OPERAD = Operad(
    operations={"greet": ..., "gossip": ..., "trade": ..., "council": ...},
    laws=[identity_law, associativity_law, locality_law],
)

# Layer 3: Sheaf (Global Coherence)
TOWN_SHEAF = Sheaf(
    overlap=citizen_relationships,
    compatible=eigenvector_consistency,
    glue=coalition_formation,
)
```

### 4.2 Component Map

| Component | Location | Tests | Status |
|-----------|----------|-------|--------|
| CitizenPolynomial | `agents/town/polynomial.py` | 85 | Complete |
| TownOperad | `agents/town/operad.py` | 72 | Complete |
| Citizen | `agents/town/citizen.py` | 140 | Complete |
| TownEnvironment | `agents/town/environment.py` | 95 | Complete |
| TownFlux | `agents/town/flux.py` | 120 | Complete |
| DialogueEngine | `agents/town/dialogue_engine.py` | 89 | Complete |
| IsometricWidget | `agents/town/isometric.py` | 45 | Complete |
| TimelineWidget | `agents/town/timeline_widget.py` | 38 | In Progress |
| **Portal (INHABIT)** | `agents/town/portal.py` | 0 | **Pending** |
| **WebServer** | `agents/town/server.py` | 15 | In Progress |
| **BudgetStore** | `agents/town/budget_store.py` | 20 | In Progress |

**Total**: 830 tests passing

### 4.3 Streaming Infrastructure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STREAMING ARCHITECTURE                               │
│                                                                              │
│   TownFlux ────────► NATS JetStream ────────► SSE/WebSocket ────────► UI    │
│      │                     │                        │                        │
│      │                     ▼                        ▼                        │
│      │            town.{id}.{phase}         /api/town/{id}/stream           │
│      │                     │                        │                        │
│      ▼                     ▼                        ▼                        │
│   TownEvent          Persistent Queue         EventSource/ws                │
│                                                                              │
│   Subjects:                                                                  │
│   - town.{id}.morning    (phase events)                                     │
│   - town.{id}.citizen.*  (individual citizen)                               │
│   - town.{id}.dialogue   (generated speech)                                 │
│   - town.{id}.metrics    (tension/cooperation)                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.4 API Design (AUP)

Agent Town integrates with the AGENTESE Universal Protocol:

```python
# Observe town state
GET /api/town/{town_id}/state
→ {"citizens": [...], "phase": "MORNING", "day": 7, "metrics": {...}}

# Stream events
GET /api/town/{town_id}/stream
→ SSE: data: {"type": "dialogue", "citizen": "Alice", "text": "..."}

# INHABIT mode
POST /api/town/{town_id}/inhabit/{citizen_id}
← WebSocket connection for real-time interaction

# Branch timeline
POST /api/town/{town_id}/branch
{"at_event": "day3_greet_alice_bob", "alternate": {"accepted": false}}
→ {"branch_id": "abc123", "divergence_point": ...}
```

---

## Part V: Implementation Phases

### Phase 8: INHABIT Mode (Next Priority)

**Goal**: User can merge with a citizen and experience through their eyes.

| Deliverable | Description | LOC Est. |
|-------------|-------------|----------|
| `Portal` class | INHABIT session management | 200 |
| Resistance mechanic | Citizen can refuse user actions | 100 |
| CLI command | `kg town inhabit <citizen>` | 50 |
| Tests | 40 new tests | 300 |

**Exit Criteria**:
- [ ] `kg town inhabit alice` enters INHABIT mode
- [ ] User input filtered through Alice's personality
- [ ] Alice can resist actions violating her eigenvectors
- [ ] Session gracefully exits on timeout or user request

### Phase 9: Web UI MVP

**Goal**: Public demo accessible via browser.

| Deliverable | Description | Tech |
|-------------|-------------|------|
| Town Map | 2D grid with citizen positions | Pixi.js |
| Citizen Panel | Click to inspect | React |
| Event Feed | Real-time activity stream | SSE |
| LOD Zoom | Pay-to-unlock depth | Stripe |

### Phase 10: Monetization Integration

**Goal**: Users can pay for premium features.

| Deliverable | Description |
|-------------|-------------|
| Stripe integration | Subscriptions + one-time purchases |
| Credit system | Token packs, usage tracking |
| Paywall | LOD 4-5 behind credits |
| Dashboard | User's towns, usage, balance |

### Phase 11: Scale to 25 Citizens

**Goal**: Village-scale simulation.

| Challenge | Solution |
|-----------|----------|
| LLM costs | Haiku for background, Sonnet for evolving only |
| Performance | Batch updates, lazy evaluation |
| Coalition complexity | k-clique percolation (k=3) |

### Phase 12: Mystery Scenarios

**Goal**: Pre-crafted dramatic scenarios.

| Scenario | Description | Price |
|----------|-------------|-------|
| "The Vanishing" | A citizen disappears; who did it? | $9.99 |
| "The Festival" | Plan and execute Valentine's Day | $4.99 |
| "The Schism" | Coalition conflict escalates | $9.99 |

---

## Part VI: Success Metrics

### 6.1 Experience Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Time in INHABIT mode | >15 min avg | Deep engagement |
| Branches per user | >3 | Exploration interest |
| LOD 4+ views per session | >5 | Willingness to pay |
| "Kent says amazing" | Yes | The Mirror Test |

### 6.2 Business Metrics

| Metric | M3 Target | M6 Target |
|--------|-----------|-----------|
| MAU | 500 | 2,000 |
| Conversion to paid | 8% | 10% |
| MRR | $4,000 | $20,000 |
| Churn (monthly) | <15% | <10% |

### 6.3 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Event latency (p95) | <500ms | NATS → UI |
| Dialogue generation | <2s | LLM response time |
| Test coverage | >85% | pytest-cov |
| Uptime | 99.5% | Health checks |

---

## Part VII: Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM costs exceed budget | Medium | High | Aggressive Haiku routing, caching |
| Users find town "boring" | Medium | High | Mystery scenarios, drama injection |
| Technical complexity | Medium | Medium | Incremental delivery, 830 tests |
| Competition (Replika, etc.) | Low | Medium | Philosophical depth is differentiator |
| Ethical concerns (AI relationships) | Low | High | Transparency, opacity principle |

---

## Part VIII: The Philosophical Grounding

### 8.1 Why This Matters

Agent Town is not "just another AI chatbot." It embodies kgents' deepest principles:

1. **Tasteful**: Five archetypes, not fifty. Each citizen earns their place.
2. **Ethical**: Citizens have rights—including the right to opacity.
3. **Joy-Inducing**: Discovery, surprise, warmth. Drama emerges, not scripts.
4. **Composable**: Everything composes. Operads guarantee validity.
5. **Generative**: The town generates infinite stories from finite grammar.

### 8.2 The Accursed Share

Per spec/principles.md, surplus must be spent gloriously or catastrophically. Agent Town embeds this:

- **Exploration budget**: 10% of tokens for "useless" tangents
- **Drama as potlatch**: Conflict IS the spending of surplus
- **LOD 5 as mystery**: The unknowable is the ultimate expenditure

### 8.3 The Mirror Test

> "Does K-gent feel like Kent on his best day?"

Agent Town passes the Mirror Test when:
- Citizens feel like real personalities, not puppets
- Users want to return and see what happened
- The simulation surprises even its creators
- Kent says "this is amazing"

---

## Continuation

```
⟿[DEVELOP]
/hydrate plans/agent-town/grand-strategy.md
handles:
  plan: this document
  implementation: plans/agent-town/phase8-inhabit.md
  monetization: plans/agent-town/monetization-mvp.md
  ux: plans/agent-town/web-ui-mvp.md
mission: Create detailed implementation plans for Phase 8-12
exit: Implementation plans written; ledger.DEVELOP=touched
```

---

## Sources

### Academic & Research
- [Stanford Generative Agents (Smallville)](https://dl.acm.org/doi/fullHtml/10.1145/3586183.3606763)
- [Virtual Protocol Westworld](https://virtual-protocol.github.io/westworld-ai/)
- [MIT Sleep No More Research](https://www.media.mit.edu/projects/remote-theatrical-immersion-extending-sleep-no-more/overview/)

### Immersive Experience Design
- [Punchdrunk Sleep No More](https://www.punchdrunk.com/work/sleep-no-more-new-york/)
- [Emily Short on Immersive Theatre](https://emshort.blog/2018/03/20/worldbuilding-in-immersive-theatre/)
- [Evermore Park](https://blooloop.com/theme-park/in-depth/evermore-future-immersive-experiences/)

### Monetization & Market
- [AI Companion Apps $120M in 2025](https://techcrunch.com/2025/08/12/ai-companion-apps-on-track-to-pull-in-120m-in-2025/)
- [RevenueCat State of Subscription Apps 2025](https://www.revenuecat.com/blog/company/the-state-of-subscription-apps-2025-launch/)
- [McKinsey: AI SaaS Monetization](https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/upgrading-software-business-models-to-thrive-in-the-ai-era)
- [AI Agent Monetization Models](https://blog.crossmint.com/monetize-ai-agents/)

### Technical
- [Marimo Notebook](https://marimo.io/)
- [Marimo Agent Support](https://marimo.io/blog/beyond-chatbots)

---

*"The simulation isn't a game. It's a seance. We are not building. We are summoning."*
