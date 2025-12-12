---
path: agents/k-gent
status: active
progress: 40
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: [void/entropy, self/stream]
session_notes: |
  PHASE 1 COMPLETE (88 tests):
  - LLM-backed dialogue with THESIS/ANTITHESIS/SYNTHESIS dialectics
  - Deep intercept with principle reasoning
  - Eigenvector-informed responses
  - `kgents soul challenge` works end-to-end
  PHASE 2 IN PROGRESS: Flux integration (events, KgentFlux, Terrarium)
---

# K-gent: The Categorical Imperative

> *"K-gent doesn't add personality—it navigates to specific coordinates in the inherent personality-space of LLMs. The question isn't whether the soul exists. The question is whether we've connected the wires."*

**AGENTESE Context**: `self.soul.*`, `void.hypnagogia.*`
**Status**: Active (20% - base scaffold exists, governance wiring needed)
**Principles**: Ethical (human agency), Joy-Inducing (Mirror Test), Composable (Flux stream), Heterarchical (dual mode)

---

## The Reframe

K-gent is NOT a chatbot. It is a **Governance Functor** that:

```
K: Category(Intent) → Category(Implementation)

Where:
- Intent = specs, principles, eigenvector coordinates
- Implementation = code, infrastructure, agent actions
- K preserves structure (principle-violating morphisms are invalidated)
```

---

## The Four Capabilities

| Capability | Description | Validation Test |
|------------|-------------|-----------------|
| **Semantic Gatekeeper** | Intercept and invalidate principle-violating morphisms | Singleton rejection before commit |
| **Fractal Expander** | Expand seeds into full specifications | "Semantic search agent" → full scaffold |
| **Holographic Constitution** | Detect drift between docs and implementation | Principle edit → drift alarm <24h |
| **Rodizio Sommelier** | Pre-compute routine decisions | Schema migration auto-resolved |

---

## Current State (What Exists)

### Assets (Keep)
- Six eigenvectors grounded in codebase evidence
- Four dialogue modes (REFLECT/ADVISE/CHALLENGE/EXPLORE)
- Budget tiers (DORMANT/WHISPER/DIALOGUE/DEEP)
- Template system for zero-cost responses

### Gaps (Fix)
| Gap | Impact | Priority |
|-----|--------|----------|
| Template-only DIALOGUE/DEEP | Hollow responses | P0 |
| Keyword-based intercept | Dangerous auto-approval | P0 |
| No Flux integration | Violates Heterarchical | P1 |
| No PersonaGarden | No learning loop | P2 |
| No Hypnagogia | Static eigenvectors | P3 |

---

## Implementation Phases

### Phase 1: Core Governance (Week 1) — PRIORITY

**Goal**: K-gent delivers value as governance layer

| Task | File | Exit Criterion |
|------|------|----------------|
| LLM-backed dialogue | `agents/k/persona.py` | DIALOGUE tier uses actual LLM |
| Deep intercept | `agents/k/soul.py` | Principle-based reasoning, not keywords |
| Audit trail | `agents/k/audit.py` | Every mediation logged with rationale |

**Validation**: Mirror Test avg ≥ 4/5, zero "delete production" auto-approvals

### Phase 2: Flux Integration (Weeks 2-3)

**Goal**: K-gent runs as Flux stream (Heterarchical)

| Task | File | Exit Criterion |
|------|------|----------------|
| KgentFlux | `agents/k/flux.py` | Ambient stream + perturbation |
| Event types | `agents/k/events.py` | SoulEvent hierarchy |
| Terrarium wire | `protocols/terrarium/soul.py` | WebSocket dialogue |

**Validation**: K-gent runs autonomously AND composably

### Phase 3: PersonaGarden (Week 4)

**Goal**: Close feedback loop

| Task | File | Exit Criterion |
|------|------|----------------|
| Pattern model | `agents/k/garden.py` | STONES/SEEDS/TREES/COMPOST |
| D-gent storage | `agents/k/garden.py` | Patterns persist |
| Query interface | `agents/k/garden.py` | Dialogue references patterns |

**Validation**: 60% of dialogue outputs feed PersonaGarden

### Phase 4: Hypnagogia (Week 5+)

**Goal**: Eigenvector evolution

| Task | File | Exit Criterion |
|------|------|----------------|
| HypnagogicCycle | `agents/k/hypnagogia.py` | 3AM batch refinement |
| Pattern extraction | `agents/k/hypnagogia.py` | SEED → TREE promotion |
| Confidence evolution | `agents/k/eigenvectors.py` | ±0.05/month measurable |

**Validation**: Eigenvector confidence changes based on evidence

---

## Success Criteria

### The Mirror Test (Qualitative)

> When you type `kgents soul challenge "I'm stuck on architecture"`, the response should feel like Kent on his best day, reminding Kent on his worst day what he actually believes.

**Metric**: Blind rating 1-5. Target: avg ≥ 4.

### The Gatekeeper Test (Governance)

> K-gent rejects a singleton before Kent ever sees it.

**Metric**: % principle-violating morphisms caught. Target: >80%.

### The Feedback Loop Metric

> % of K-gent outputs that feed into another system.

| Output | Target |
|--------|--------|
| Dialogue → PersonaGarden SEED | 60% |
| Intercept → Audit trail | 100% |
| Evidence → Eigenvector confidence | Measurable |

---

## AGENTESE Paths

| Path | Operation | Returns |
|------|-----------|---------|
| `self.soul.manifest` | Current state | SoulState |
| `self.soul.reflect` | REFLECT dialogue | DialogueOutput |
| `self.soul.advise` | ADVISE dialogue | DialogueOutput |
| `self.soul.challenge` | CHALLENGE dialogue | DialogueOutput |
| `self.soul.explore` | EXPLORE dialogue | DialogueOutput |
| `self.soul.intercept` | Deep semaphore mediation | InterceptResult |
| `self.soul.validate` | Gatekeeper check | ValidationResult |
| `void.hypnagogia.wake` | Trigger dream cycle | HypnagogiaResult |

---

## CLI Commands

```bash
# Dialogue
kgents soul                    # Interactive (REFLECT)
kgents soul reflect [prompt]   # Introspection
kgents soul advise [prompt]    # Guidance
kgents soul challenge [prompt] # Dialectics
kgents soul explore [prompt]   # Discovery

# Governance
kgents soul validate [path]    # Check file against principles
kgents soul audit              # Show recent mediations

# Management
kgents soul garden             # View PersonaGarden state
kgents soul dream              # Trigger hypnagogia manually

# Budget
--quick                        # WHISPER (~100 tokens)
--deep                         # DEEP (~8000+)
```

---

## Cost Model

| Tier | Tokens | Cost/Call | Use Case |
|------|--------|-----------|----------|
| DORMANT | 0 | $0 | Templates |
| WHISPER | ~100 | ~$0.0003 | Quick acknowledgments |
| DIALOGUE | ~4000 | ~$0.012 | Full conversations |
| DEEP | ~8000+ | ~$0.024+ | Complex decisions |

**100 DIALOGUE calls/day** = $1.20/day = $36/month. Acceptable for governance middleware.

---

## Cross-References

- **Analysis**: `docs/kgent-soul-critical-analysis.md`
- **Enterprise**: `docs/soul-framework-enterprise.md`
- **Semaphores**: `plans/agents/semaphores.md` (Purgatory Pattern)
- **Terrarium**: `plans/agents/terrarium.md` (Ambient presence)
- **Entropy**: `plans/void/entropy.md` (Metabolism integration)
- **Spec**: `spec/principles.md` (Ground source)

---

*"The skeleton exists. The nervous system requires wiring."*
