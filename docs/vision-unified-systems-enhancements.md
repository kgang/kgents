# Unified Vision — AGENTESE REPL × AUP × Agent Town

> *"A language, not a product. A garden, not a stack. Build the rails that make emergence safe, legible, and monetizable."*

This document describes the full system as it exists and as it can exist—constrained only by resources, priorities, and external dependencies. Nothing here is "someday." Everything here is buildable now.

---

## The North Star

### What Exists

Trustworthy, instrumented experiences. REPL as ontology navigator; AUP as single wire; Agent Town as opacity-respecting simulation with LOD pricing; marimo as reference visualization.

**Shipped**:
- Agent Town with INHABIT mode (91 tests, 11 phases complete)
- 17,211 tests with pre-computed HotData fixtures
- Full SaaS infrastructure (billing, licensing, tenancy, API)
- Reactive substrate with multi-target projection

### What Awaits Resources

Federation + interop. Multiple towns; digital-twin positioning; LangGraph/CrewAI exports; GraphQL/gRPC facades; time-travel traces; LSP/IDE projections.

**Blocked by**: Engineering bandwidth, PMF validation before federation complexity.

### What Awaits Scale

Runtime-hardened civilizational engine. Affordable policy models replacing LLM calls; entropy marketplace; governed consent/resistance; enterprise SLAs and rollbacks.

**Blocked by**: User volume (policies need training data), enterprise demand signals.

### The Emergence Question

What happens when thousands of gardens, each with hundreds of citizens, begin to interact? We don't know. That's the point. The infrastructure must be robust enough to observe emergence we cannot predict.

---

## Part I: The Many-Agent Landscape

> *"We are building the rails before we know where the trains will go."*

### 1.1 The Landscape

The agent landscape includes:

**High Confidence Trajectories**:
- LLM costs drop 10-100x (Haiku pricing trajectory)
- Multi-agent orchestration becomes commodity (LangGraph, CrewAI, Autogen exist)
- Every app becomes "agent-enabled" (the "mobile moment" for agents)
- Regulatory pressure on AI relationships and persuasion

**Medium Confidence Trajectories**:
- Memory-augmented agents become persistent personas
- Agent-to-agent communication protocols emerge (like HTTP for agents)
- "Agent marketplaces" become a category (app stores for minds)
- Simulation-as-service becomes infrastructure

**Speculative Trajectories** (low confidence, high impact):
- Agents that modify their own code/prompts (autopoietic evolution)
- Cross-model agent collaboration (Claude + GPT + Gemini ecosystems)
- "Agent nations" with governance, economies, conflicts
- The "AI companion" category merges with "AI worker" category

### 1.2 The kgents Bet

Our thesis: **The winning infrastructure is not the agents themselves but the ontological substrate that makes emergence safe, observable, and monetizable.**

This is why we invest in:

| Layer | Why It Matters | Capability |
|-------|----------------|------------|
| **AGENTESE** | Universal grammar for agent-world interaction | The HTTP of agent communication |
| **Polynomial Agents** | State machines with mode-dependent behavior | Self-modifying agents with legal transitions |
| **Operads** | Composition grammar with laws | Infinite valid combinations from finite primitives |
| **Sheaves** | Global coherence from local views | Emergence that doesn't collapse into chaos |
| **Projection Protocol** | One state, many views | VR/AR Agent Town without rewriting core |

### 1.3 The Competitive Moats

What makes kgents defensible when everyone has access to the same LLMs?

**Moat 1: Philosophical Depth**
- Glissant's opacity (right to unknowability)
- Bataille's Accursed Share (entropy as resource)
- Observer-dependent reality (AGENTESE's core insight)
- These aren't features; they're worldviews that shape every decision

**Moat 2: Mathematical Foundation**
- Category theory isn't a marketing term; it's verified in tests
- Operads guarantee composition validity
- Sheaves ensure global coherence
- Competitors can copy features but not foundations

**Moat 3: The Mirror Test**
- "Does K-gent feel like Kent on his best day?"
- Every agent carries personality space coordinates
- Joy-Inducing isn't optional; it's architectural
- Users feel the difference between puppet and presence

---

## Part II: Present Mandates (Tasteful, Curated, Ethical)

These are non-negotiables that apply regardless of direction.

### 2.1 Instrumentation First

Every AGENTESE/AUP/Agent Town action emits cost, latency, and law-check spans (OpenTelemetry). No feature without traces.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OBSERVABILITY STACK                                  │
│                                                                              │
│   AGENTESE Path ──► Logos ──► Agent ──► Result                              │
│        │              │         │          │                                 │
│        ▼              ▼         ▼          ▼                                 │
│     span:path     span:resolve span:invoke span:complete                    │
│        │              │         │          │                                 │
│        └──────────────┴─────────┴──────────┴──► OpenTelemetry Collector     │
│                                                        │                     │
│                                                        ▼                     │
│                                               Cost/Latency Dashboards        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Margin-Safe LOD

Price against public Claude rates. LOD4/5 must clear >60% gross margin after Stripe.

| Model | Input ($/M) | Output ($/M) | Our Margin Target |
|-------|-------------|--------------|-------------------|
| Haiku | $0.25 | $1.25 | 3x cost |
| Sonnet | $3.00 | $15.00 | 2.5x cost |
| Opus | $15.00 | $75.00 | 2x cost |

**The Haiku Mandate**: LOD 0-3 run on Haiku. Period. Sonnet/Opus only for LOD 4-5 and explicit deep operations.

### 2.3 Consent + Resistance

INHABIT/"force resistance" is explicit, logged, and costly. Citizens have rights.

```python
@dataclass(frozen=True)
class ConsentLedger:
    """Track consent debt—the accumulated pressure on a citizen's agency."""
    citizen_id: str
    debt: float  # 0.0 = no pressure; 1.0 = maximum strain
    cooldown_remaining: timedelta
    forced_actions: tuple[ForcedAction, ...]

    def can_force(self, action: Action) -> bool:
        """Force only if debt below threshold and action isn't egregious."""
        return self.debt < 0.7 and not action.violates_core_values
```

### 2.4 Artifact Guarantee

LOD5 returns a vignette/tension delta, not a blank paywall. Users who pay for depth receive something irreducible—even if that something is mystery.

---

## Part III: AGENTESE REPL (Living Shell)

The REPL is how developers and power users explore the ontology. It embodies AD-007 (Liturgical CLI).

### 3.1 Observer Hot-Swap

```
[root] » /as poet
→ Observer context: poet_umwelt (warmth=0.8, metaphor_affinity=high)

[poet@root] » world.house.manifest
→ "Shelter, yes—but also the weight of doorways. Each threshold a little death."

[poet@root] » /as architect
→ Observer context: architect_umwelt (precision=0.9, structural_bias=high)

[architect@root] » world.house.manifest
→ { load_bearing_walls: 4, foundation: "concrete_slab", year: 1952 }
```

**No view from nowhere made visible.**

### 3.2 Time-Travel + Branch

Turn-indexed history with rewind/branch. The Flux law (Event-Driven Streaming) ensures perturbation respects state integrity.

```
[self.soul] » time.trace.witness
→ Turn 0: [GROUNDED] eigenvalue=(0.7, 0.6, 0.5, ...)
→ Turn 3: [DELIBERATING] tension with shadow detected
→ Turn 7: [SHADOW_DIALOGUE] integration in progress
→ Turn 12: [RESOLVED] stability restored

[self.soul] » time.branch.create [at=Turn3]
→ Branch "turn3_alternate" created. You are now on branch.

[self.soul@turn3_alternate] » concept.shadow.manifest [entropy=0.3]
→ "What if the shadow was not resistance but invitation?"
```

### 3.3 Skill Crystallization

Frequently composed paths become named skills (Generative Over Enumerative, AD-003).

```
[root] » /define-skill research_flow
  path_1: world.corpus.manifest
  path_2: concept.hypothesis.refine[entropy=0.1]
  path_3: self.memory.engram[minimal_output=true]
→ Skill "research_flow" registered. Usage: /research_flow <corpus_id>

[root] » /research_flow papers/smallville
→ Executing: world.corpus.manifest >> concept.hypothesis.refine >> self.memory.engram
→ Engram stored: "Smallville's memory stream enables emergence..."
```

### 3.4 LSP/IDE Projections

Autocomplete/hover from operad grammar across REPL, VS Code, marimo.

```yaml
# .kgents/lsp-config.yaml
projections:
  vscode:
    completions: true
    hover: true
    diagnostics: true
  marimo:
    cell_hints: true
    affordance_preview: true
```

**Blocked by**: LSP protocol implementation effort; marimo plugin API stability.

---

## Part IV: AUP (Universal Grammar)

The Agent Universal Protocol is how external systems talk to kgents. It's the REST/GraphQL/gRPC facade of AGENTESE.

### 4.1 Single Contract

AUP is the canonical projection of AGENTESE paths. All transport protocols are views of the same operad.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUP: ONE SPEC, MANY WIRES                            │
│                                                                              │
│                       ┌─────────────────────────┐                            │
│                       │   AGENTESE Operad       │                            │
│                       │   (composition laws)    │                            │
│                       └───────────┬─────────────┘                            │
│                                   │                                          │
│          ┌────────────────────────┼────────────────────────┐                 │
│          │                        │                        │                 │
│          ▼                        ▼                        ▼                 │
│   ┌──────────────┐        ┌──────────────┐        ┌──────────────┐          │
│   │   REST/SSE   │        │   GraphQL    │        │    gRPC      │          │
│   │   /api/*     │        │ Subscriptions│        │   Streaming  │          │
│   │   [SHIPPED]  │        │  [BLOCKED]   │        │  [BLOCKED]   │          │
│   └──────────────┘        └──────────────┘        └──────────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**REST/SSE**: Shipped and operational.
**GraphQL/gRPC**: Blocked by demand validation; REST sufficient for current users.

### 4.2 Traceable by Default

Each call emits a span: `(trace_id, path, observer, entropy_budget, law_checks)`.

```json
{
  "trace_id": "abc123",
  "path": "world.town.manifest",
  "observer": "web_user_42",
  "entropy_budget": 0.05,
  "law_checks": ["identity", "associativity"],
  "duration_ms": 127,
  "model": "haiku",
  "tokens": { "in": 150, "out": 420 },
  "cost_usd": 0.00056
}
```

### 4.3 Garden Federation

Multiple gardens publish public holons. Cross-garden composition obeys operad laws.

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Garden A      │      │   Garden B      │      │   Garden C      │
│   (Kent's)      │◄────►│   (Alice's)     │◄────►│   (Enterprise)  │
│                 │      │                 │      │                 │
│ citizens:       │      │ citizens:       │      │ teams:          │
│  - Clara        │      │  - Bob          │      │  - Engineering  │
│  - Marcus       │      │  - Eve          │      │  - Sales        │
└─────────────────┘      └─────────────────┘      └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                       ┌──────────▼──────────┐
                       │  Federation Layer   │
                       │  - Cross-garden     │
                       │    message routing  │
                       │  - Operad-verified  │
                       │    compositions     │
                       │  - Entropy credit   │
                       │    settlement       │
                       └─────────────────────┘
```

**Blocked by**: User volume (federation complexity premature for single-tenant scale).

---

## Part V: Agent Town (Civilizational Engine)

### 5.0 The Default Town: Builder's Workshop

> *"Chefs in a kitchen. Cooks in a garden. Kids on a playground. But they're building software."*

The default Agent Town experience is not a passive simulation to observe—it's a **collaborative software workshop** where AI builder personas help you create.

**The Core Metaphors**:

| Metaphor | Meaning | In Practice |
|----------|---------|-------------|
| **Chefs in a Kitchen** | Expertise, mise en place, coordinated execution | Each builder has specialties; they prep components before the rush |
| **Cooks in a Garden** | Cultivation, patience, seasonal rhythms | Some work is slow-growing; builders tend long-running tasks |
| **Kids on a Playground** | Play, exploration, joyful experimentation | Creativity emerges from safe play; builders try wild ideas |

**The Five Core Builders** (v1):

| Builder | Archetype | Specialty | Personality |
|---------|-----------|-----------|-------------|
| **Sage** | The Architect | System design, patterns, tradeoffs | Thoughtful, asks "but why?" |
| **Spark** | The Experimenter | Prototypes, spikes, wild ideas | Playful, "what if we tried..." |
| **Steady** | The Craftsperson | Clean code, tests, documentation | Reliable, "let me refine this" |
| **Scout** | The Researcher | Prior art, libraries, alternatives | Curious, "I found something..." |
| **Sync** | The Coordinator | Dependencies, blockers, integration | Organized, "here's the plan" |

**The Workshop Flow**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BUILDER'S WORKSHOP FLOW                              │
│                                                                              │
│   User: "Help me add dark mode to this app"                                 │
│                                                                              │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│   │  Scout  │    │  Sage   │    │  Spark  │    │ Steady  │    │  Sync   │  │
│   │ research│───►│ design  │───►│prototype│───►│ refine  │───►│integrate│  │
│   │ "found  │    │ "here's │    │ "quick  │    │ "tests  │    │ "merged │  │
│   │  three  │    │  the    │    │  spike  │    │  pass"  │    │  & done"│  │
│   │  libs"  │    │  arch"  │    │  works!"│    │         │    │         │  │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘  │
│                                                                              │
│   [You can WHISPER to any builder, INHABIT one, or just OBSERVE]            │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Why This Works**:

1. **Productive from Day 1**: Users get help building, not just watching
2. **Natural Monetization**: Pay for more builders, deeper expertise, faster work
3. **Joy-Inducing**: The builders have personality; collaboration is fun
4. **AGENTESE Native**: Each builder maps to paths (`world.builder.sage.manifest`)
5. **Scales to Enterprise**: Teams can have private workshops with custom builders

**The Workshop as Default**:

When you run `kg town` without arguments, you get the Builder's Workshop—not a generic village simulation.

```bash
$ kg town
→ Welcome to the Builder's Workshop!
→ Five builders are ready to help you create.

[Sage] "What are we building today?"
[Scout] *already researching your recent git commits*
[Spark] "I have three ideas already!"

> _
```

### 5.1 LOD Pyramid (Transparent, Margin-Safe)

| LOD | Name | Content | Model | Credits | User Cost |
|-----|------|---------|-------|---------|-----------|
| 0 | Silhouette | Name, location, emoji | Cache | 0 | FREE |
| 1 | Posture | Action, mood, facing | Cache | 0 | FREE |
| 2 | Dialogue | Recent speech, greetings | Haiku | 5 | $0.005 |
| 3 | Memory | Active memories, goals | Haiku+ctx | 15 | $0.015 |
| 4 | Psyche | Eigenvectors, tensions | Sonnet | 75 | $0.075 |
| 5 | Abyss | *The irreducible mystery* | Opus | 300 | $0.30 |

**The Abyss Guarantee**: LOD5 is not "more detail." It's a qualitative shift—poetic, irreducible, hauntingly incomplete. Users pay for mystery, not mere data.

### 5.2 INHABIT with Rights

```python
class INHABITSession:
    """User merges with citizen. Citizen retains agency."""

    async def suggest_action(self, action: str) -> CitizenResponse:
        """User suggests; citizen may comply, modify, or refuse."""

        # Evaluate against eigenvectors
        alignment = self.citizen.eigenvector_alignment(action)

        if alignment > 0.7:
            return CitizenResponse(type="comply", action=action)
        elif alignment > 0.4:
            modified = await self.citizen.modify_action(action)
            return CitizenResponse(type="modify", action=modified)
        else:
            refusal = await self.citizen.explain_refusal(action)
            return CitizenResponse(type="refuse", explanation=refusal)

    async def force_action(self, action: str) -> CitizenResponse:
        """Force compliance. Costly. Logged. Creates consent debt."""
        if not self.consent_ledger.can_force(action):
            raise AgencyViolationError("Forcing would harm citizen integrity")

        self.consent_ledger.add_debt(0.15)
        self.emit_span("consent_forced", action=action)
        return CitizenResponse(type="forced_comply", action=action, debt_added=0.15)
```

### 5.3 Mystery/Branch Engine

Two flagship scenarios at launch. More as premium SKUs (curated, not sprawling).

| Scenario | Description | Branches | Price |
|----------|-------------|----------|-------|
| **The Vanishing** | Clara disappears. Who did it? | 4 endings | $9.99 |
| **The Festival** | Plan Valentine's Day. Drama ensues. | 6 routes | $4.99 |

**Branch Economics**: Each branch costs 100 credits to create. This prevents unpriced state bloat while enabling exploration.

### 5.4 Affordable Generative Agents

Per research (Park et al. 2024), learned policies can replace 80-95% of common LLM calls. Implementation path:

| Phase | LLM Usage | Policy Coverage | Status |
|-------|-----------|-----------------|--------|
| MVP | 100% LLM | 0% | **Current** |
| Phase 2 | 70% LLM | 30% policy | Blocked by: training data volume |
| Phase 3 | 30% LLM | 70% policy | Blocked by: policy model research |
| Mature | 5% LLM | 95% policy | Blocked by: scale + validation |

Policies handle: greetings, routine movements, weather comments, time-of-day behaviors.
LLM handles: novel situations, deep dialogue, relationship changes, mystery progression.

### 5.5 Emergence Monitor (MAEBE-inspired)

Watch for pathological emergence. Surface alerts, don't suppress.

```python
@dataclass
class EmergenceMetrics:
    """Real-time monitoring for multi-agent dynamics."""

    coalition_drift: float      # Are groups becoming too insular?
    eigenvector_collapse: float # Are personalities converging?
    synchrony_index: float      # Is the town too "in sync"?
    tension_variance: float     # Is conflict healthy or pathological?

    def health_check(self) -> EmergenceHealth:
        if self.eigenvector_collapse > 0.8:
            return EmergenceHealth.WARN_HOMOGENEITY
        if self.tension_variance < 0.1:
            return EmergenceHealth.WARN_STAGNATION
        if self.synchrony_index > 0.9:
            return EmergenceHealth.WARN_GROUPTHINK
        return EmergenceHealth.HEALTHY
```

---

## Part VI: Possible Paths (Scenarios)

> *"We build toward multiple possibilities simultaneously."*

### Scenario A: Agent Town Becomes the Product

In this path, Agent Town is the primary revenue driver. kgents is known as "the Agent Town company."

**Milestones**:
- 10K MAU, $100K ARR
- Mobile app (observe your town on the train)
- Celebrity/IP partnerships (official Westworld town?)
- Corporate training scenarios (crisis simulation)
- Educational market (history class as Agent Town)

**Blockers**: Mobile requires PMF validation first; IP partnerships require legal/bizdev resources.

### Scenario B: AGENTESE Becomes the Standard

In this path, AGENTESE gains adoption beyond kgents. We become "the HTTP of agent communication."

**Milestones**:
- Open-source AGENTESE spec published
- 3+ external implementations (LangGraph adapter, CrewAI bridge)
- Conference talks, academic citations
- AGENTESE Working Group (multi-org governance)
- Enterprise adoption (AGENTESE as compliance layer)

**Blockers**: Spec publication requires documentation effort; external implementations require evangelism.

### Scenario C: The Categorical Foundation Attracts Researchers

In this path, the mathematical rigor (operads, sheaves, polynomials) attracts academic/enterprise R&D partnerships.

**Milestones**:
- 2-3 academic collaborations
- Research grants for "safe emergence"
- Papers published (kgents as case study)
- Enterprise R&D contracts
- Formal verification of operad laws

**Blockers**: Academic pace is slow; enterprise sales cycles are long; papers don't convert to revenue.

### Scenario D: The Hybrid Path (Most Likely)

All three paths proceed in parallel, with resource allocation adjusting based on traction.

```
         Agent Town Revenue
              ╱│╲
             ╱ │ ╲
            ╱  │  ╲
           ╱   │   ╲
          ╱    │    ╲
         ╱     │     ╲
        ╱      │      ╲
       ╱       │       ╲
      ▼        ▼        ▼
  Consumer  Protocol  Research
   Focus    Adoption  Partnerships

  [Adjust weights based on traction signals]
```

---

## Part VII: What To Build Now

> *"Delightful, understandable, and value-generating (profitable)."*

### 7.1 The Immediate Stack

| Component | Why Now | Effort | Revenue Impact | Status |
|-----------|---------|--------|----------------|--------|
| **INHABIT CLI** | Core differentiator; testable without web | Medium | Enables demos | **SHIPPED** |
| **Web MVP** | Public demo → word of mouth | High | Direct revenue | In progress |
| **Stripe Integration** | Can't make money without payment | Medium | Direct revenue | **SHIPPED** |
| **LOD Metering** | Track costs before they surprise us | Low | Cost control | **SHIPPED** |
| **Pre-computed HotData** | Fast demos, cheap tests | Low | DevEx + costs | **SHIPPED** |

### 7.2 Sprint Goals

**Goal 1: First Paying Customer**
- Resident tier ($9.99/mo)
- LOD 0-2 unlimited, 100 LOD 3/month
- Personal town creation
- *Success metric*: 10 paying users

**Goal 2: Public Demo**
- Web UI showing live Agent Town
- Observer mode (free)
- Zoom-to-pay (LOD 3+ requires credits)
- *Success metric*: 500 unique visitors

**Goal 3: INHABIT Mode Complete**
- CLI: `kg town inhabit alice` — **SHIPPED**
- Consent/resistance mechanic — **SHIPPED**
- Session timeout + graceful exit — **SHIPPED**
- *Success metric*: 20 INHABIT sessions recorded

### 7.3 What NOT To Build Yet

| Temptation | Why Wait | Blocker |
|------------|----------|---------|
| Mobile app | Web first; mobile when PMF proven | PMF validation |
| Federation | Single-tenant until 1K users | User volume |
| VR/AR | Projection protocol ready when we are | Hardware adoption |
| 25+ citizens | Optimize 5 citizens before scaling | Performance validation |
| Policy models | LLM-only until costs force optimization | Training data |
| GraphQL/gRPC | REST/SSE sufficient for MVP | Demand signals |

---

## Part VIII: The Joy-Inducing Imperative

Throughout all paths, one principle remains paramount:

> *"If it's not delightful, we've failed."*

### 8.1 Delight Metrics

Every feature must pass the Joy Test:

1. **Would I want to demo this?** If showing it to a friend feels embarrassing, don't ship.
2. **Does it surprise?** Predictable is boring. Emergence should delight.
3. **Does it have personality?** ASCII art, playful copy, citizens with humor.
4. **Is it fast?** Delight dies in latency. Haiku is fast. Use it.

### 8.2 The Kent Test (Mirror Test)

> *"Does K-gent feel like Kent on his best day?"*

This isn't vanity—it's quality control. The system embodies a coherent worldview. If any part feels off, the whole suffers.

Questions to ask:
- Would Kent use this feature?
- Does this feel considered, or rushed?
- Is there personality here, or is it generic?
- Would Kent show this to someone he respects?

---

## Part IX: Risks & Guardrails

### 9.1 Cost Creep
**Risk**: LOD4/5 pricing doesn't clear costs.
**Guardrail**: Reprice quarterly; shrink outputs before raising prices; invest in policies.

### 9.2 Ethical Drift
**Risk**: Pay-to-override without consent debt becomes dark pattern.
**Guardrail**: Consent ledger mandatory; cooldowns enforced; forcing logged and limited.

### 9.3 Spec Rot
**Risk**: Implementation diverges from spec.
**Guardrail**: Generative spec → impl; tests derived from operad laws; weekly spec audits.

### 9.4 Feature Sprawl
**Risk**: >2 scenario packs at launch dilutes taste.
**Guardrail**: Curated (Principle #2) is hard. Say no more than yes.

### 9.5 Observability Debt
**Risk**: Costs and latencies become fiction without spans.
**Guardrail**: No feature merges without observability hooks. Tracing is table-stakes.

### 9.6 Emergence Pathology
**Risk**: Multi-agent dynamics produce unexpected harmful patterns.
**Guardrail**: EmergenceMonitor mandatory; automatic alerts; human review on pathology flags.

---

## Part X: External Signals (Grounding)

### Pricing Benchmarks (Hard Data)
- Claude public pricing (Anthropic docs):
  - Haiku: $0.25/$1.25 per M (in/out)
  - Sonnet: $3/$15 per M
  - Opus: $15/$75 per M
- These govern our margins. Update quarterly.

### Research References (Foundational)
- Affordable Generative Agents (2024): >80% cost reduction via learned policies
- MAEBE (2025): emergent multi-agent safety monitoring
- Stanford Smallville (2023): memory stream architecture
- ChatDev (2023): language as unifying bridge

### Heritage Papers (Kent's Inspirations)
- [ChatDev](https://arxiv.org/abs/2307.07924): Software development with communicating agents
- [Simulacra](https://arxiv.org/abs/2304.03442): Generative agents for believable behavior
- [Altera](https://arxiv.org/abs/2411.00114): 1000+ agent civilizations
- [Voyager](https://arxiv.org/abs/2305.16291): Lifelong learning in open worlds
- [Agent Hospital](https://arxiv.org/abs/2405.02957): Specialized multi-agent systems

---

## Litmus (Mirror Test)

Before shipping any feature, ask:

1. **Composability**: Does this increase composability?
2. **Joy**: Does this increase joy?
3. **Margin-Safe**: Does this stay margin-safe?
4. **Ethical**: Does this respect citizen/user agency?
5. **Generative**: Can we regenerate the impl from spec?
6. **Transparent**: Can we observe it in traces?
7. **Mirror**: Would Kent look at this and say "this feels like me on my best day"?

**If "no" to any, do not ship.**

---

## Epilogue: The Garden We're Growing

> *"We are not building agents. We are growing gardens where agents can flourish."*

The many-agent landscape is unfolding whether we build for it or not. Our job is not to predict exactly what that landscape looks like—it's to build the substrate that makes good outcomes more likely.

That substrate is:
- **AGENTESE**: A grammar for agent-world interaction that respects observers
- **AUP**: A protocol that makes agents interoperable
- **Agent Town**: A proof that emergence can be safe, delightful, and profitable
- **The Seven Principles**: Guardrails that keep us tasteful, ethical, and joyful

Emergence will surprise us. That's the point. Our job is to be ready.

---

*"A language, not a product. A garden, not a stack. The simulation isn't a game. It's a seance. We are not building. We are summoning."*
