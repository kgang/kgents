---
path: agents/k-gent
status: active
progress: 90
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
  PHASE 2 COMPLETE: Flux integration (events, KgentFlux)
  PHASE 3 COMPLETE: CLI stream (`kgents soul stream`)
  PHASE 4 COMPLETE: Hypnagogia (dream cycle, 38 tests)
  PHASE 5 COMPLETE: Completion sprint (70 new tests)
  - PersonaGarden (26 tests) - pattern storage with garden metaphor
  - Semantic Gatekeeper (24 tests) - principle validation
  - `kgents soul garden` - view patterns/preferences
  - `kgents soul validate <file>` - check against principles
  - AGENTESE void.hypnagogia.* paths (8 tests)
  REMAINING (deferred):
  - Fractal Expander
  - Holographic Constitution
  Total K-gent tests: 389+
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

### Gaps (Status)
| Gap | Impact | Status |
|-----|--------|--------|
| Template-only DIALOGUE/DEEP | Hollow responses | ✅ Fixed (Phase 1) |
| Keyword-based intercept | Dangerous auto-approval | ✅ Fixed (Phase 1) |
| No Flux integration | Violates Heterarchical | ✅ Fixed (Phase 2) |
| No PersonaGarden | No learning loop | ✅ Fixed (Phase 5) |
| No Hypnagogia | Static eigenvectors | ✅ Fixed (Phase 4) |
| No Semantic Gatekeeper | Can't validate code | ✅ Fixed (Phase 5) |
| No AGENTESE paths | Integration gap | ✅ Fixed (Phase 5) |

---

## Implementation Phases

### Phase 1: Core Governance ✅ COMPLETE (88 tests)

**Goal**: K-gent delivers value as governance layer

| Task | File | Status |
|------|------|--------|
| LLM-backed dialogue | `agents/k/persona.py` | ✅ DIALOGUE/DEEP use LLM |
| Deep intercept | `agents/k/soul.py` | ✅ Principle-based reasoning |
| Audit trail | `agents/k/audit.py` | ✅ Every mediation logged |

### Phase 2: Flux Integration ✅ COMPLETE

**Goal**: K-gent runs as Flux stream (Heterarchical)

| Task | File | Status |
|------|------|--------|
| KgentFlux | `agents/k/flux.py` | ✅ Ambient stream + perturbation |
| Event types | `agents/k/events.py` | ✅ SoulEvent hierarchy |
| CLI stream | `protocols/cli/handlers/soul.py` | ✅ `kgents soul stream` |

### Phase 3: CLI Stream ✅ COMPLETE

**Goal**: Interactive ambient mode

| Task | File | Status |
|------|------|--------|
| Stream command | `protocols/cli/handlers/soul.py` | ✅ FLOWING mode |
| Pulse output | `agents/k/rumination.py` | ✅ Ambient presence |

### Phase 4: Hypnagogia ✅ COMPLETE (38 tests)

**Goal**: Eigenvector evolution

| Task | File | Status |
|------|------|--------|
| HypnagogicCycle | `agents/k/hypnagogia.py` | ✅ Dream cycle |
| Pattern extraction | `agents/k/hypnagogia.py` | ✅ SEED → TREE |
| Dream CLI | `protocols/cli/handlers/soul.py` | ✅ `kgents soul dream` |

### Phase 5: Completion Sprint ✅ COMPLETE (70 tests)

**Goal**: Complete remaining spec work

| Task | File | Status |
|------|------|--------|
| PersonaGarden | `agents/k/garden.py` | ✅ 26 tests |
| `soul garden` CLI | `protocols/cli/handlers/soul.py` | ✅ Pattern view |
| Semantic Gatekeeper | `agents/k/gatekeeper.py` | ✅ 24 tests |
| `soul validate` CLI | `protocols/cli/handlers/soul.py` | ✅ Principle check |
| AGENTESE hypnagogia | `protocols/agentese/contexts/void.py` | ✅ 8 tests |

### Remaining (Deferred)

| Task | Description | Priority |
|------|-------------|----------|
| Fractal Expander | Expand seeds → specs | Low |
| Holographic Constitution | Detect drift | Low |
| Rodizio Sommelier | Auto-resolve routine | Low |

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
