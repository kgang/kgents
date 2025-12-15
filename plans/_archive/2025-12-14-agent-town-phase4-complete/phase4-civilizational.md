---
path: plans/agent-town/phase4-civilizational
status: active
progress: 5
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables:
  - agent-town-mvp
  - civilizational-engine
  - west-world-simulation
session_notes: |
  PLAN phase initiated. Scope: 10→25 citizens, Web UI, API monetization.
  Heritage: CHATDEV, SIMULACRA, ALTERA, VOYAGER, AGENT HOSPITAL.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.35
  spent: 0.18
  returned: 0.0
---

# Agent Town Phase 4: Civilizational Scale

> *"From hamlet to metropolis. From 10 citizens to 25. From terminal to Web UI. The simulation park awakens."*

---

## Vision (from `plans/_focus.md`)

Kent's vision draws from five seminal papers—conceptual ancestors for Agent Town:

| Paper | Key Insight | Phase 4 Application |
|-------|-------------|---------------------|
| **CHATDEV** | Multi-agent software dev with roles | Citizens with specialized roles (Builder, Trader, Healer) |
| **SIMULACRA** | Generative agents with memory streams | GraphMemory + eigenvector personality → emergent behavior |
| **ALTERA** | Long-horizon agent planning | NPHASE_OPERAD → multi-turn evolution cycles |
| **VOYAGER** | Open-ended learning, skill libraries | Citizen skill acquisition via accursed share |
| **AGENT HOSPITAL** | Domain-specific simulation | Town as template for vertical simulations |

**Guiding Principle**: West World-like simulation with holographic depth. Every citizen is a handle yielding different affordances to different observers (umwelt).

---

## Phase 3 Foundation (343 Tests)

| Artifact | Description |
|----------|-------------|
| `memory.py` | GraphMemory with k-hop BFS, decay, reinforcement |
| `functor.py` | TOWN→NPHASE functor with verified laws |
| `evolving.py` | EvolvingCitizen with SENSE→ACT→REFLECT cycle |
| `operad.py` | TOWN_OPERAD with social operations |
| `environment.py` | 10 citizens (7 static + 3 evolving), 6 regions |

**Key Invariants**:
- Eigenvector drift ≤ 0.1 per cycle
- NPHASE: SENSE >> ACT >> REFLECT (cyclic)
- Coalition strength ∈ [0, 1], decays without reinforcement

---

## Phase 4 Scope

### Target 1: Scale to 25 Citizens

**New Archetypes** (5 types × 3 each = 15 new):

| Archetype | Cosmotechnics | Eigenvector Bias | Role |
|-----------|--------------|------------------|------|
| **Builder** | `construction_v2` | creativity↑, patience↑ | Infrastructure creation |
| **Trader** | `exchange_v2` | curiosity↑, trust↓ | Resource exchange |
| **Healer** | `restoration` | warmth↑, empathy↑ | Social/emotional repair |
| **Scholar** | `synthesis_v2` | curiosity↑, patience↑ | Skill discovery, teaching |
| **Watcher** | `memory_v2` | patience↑, trust↑ | Memory witnesses, historians |

**Emergent Dynamics**:
- **Coalition formation**: 3+ citizens aligning on goals (clique detection)
- **Reputation propagation**: Gossip affects eigenvectors (diffusion model)
- **Resource scarcity**: Drives conflict/cooperation
- **Generational memory**: Old citizens mentor new

**Extended Personality Space**:
- 5D eigenvector → 7D (add `resilience`, `curiosity`)
- 8 cosmotechnics → 12 (add 4 new worldviews)
- Typed relationship edges: mentor, rival, ally, stranger

### Target 2: Web UI (Town Visualization)

**Dashboard Components**:
1. **Town Map**: Citizen positions, relationships as edges
2. **Citizen Inspector**: Eigenvectors, memory graph, evolution history
3. **Event Stream**: Timestamped actions (gossip, trade, mourn, celebrate)
4. **Phase Indicator**: SENSE/ACT/REFLECT for each citizen

**Technology Decision (RESEARCH)**:
- Option A: **Textual** (TUI) — reuse I-gent patterns (`agents/i/screens/`)
- Option B: **marimo** (reactive notebooks) — richer visualization
- Decision criteria: Kent's "VISUAL UIs" intent, real-time updates, deployment ease

**Observer Umwelt**:
- Different views for different observers
- Economist sees trades, poet sees emotions
- Holographic: single state → multiple projections

### Target 3: API + Monetization Hook

**Tiered Simulation**:
| Tier | Citizens | Cycles | Custom Archetypes | Price |
|------|----------|--------|-------------------|-------|
| Free | 10 | 1 day | No | $0 |
| Pro | 25 | Unlimited | Yes | TBD |
| Enterprise | 100+ | Unlimited | Domain templates | TBD |

**API Surface**:
```
POST /town/create          → Spawn simulation
POST /town/{id}/step       → Advance one cycle
GET  /town/{id}/citizen/{name} → Inspect citizen (LOD 0-5)
GET  /town/{id}/events     → SSE stream of events
```

**Metering** (via `openmeter_client.py`):
- Per-citizen-turn metering
- Token budget awareness (LLM-backed citizens cost)

---

## Non-Goals (Scope Boundaries)

| Non-Goal | Reason | Deferred To |
|----------|--------|-------------|
| LLM dialogue for all 25 citizens | Too expensive | 3-5 LLM-backed, rest rules-based |
| Persistent database | Complexity | Phase 5 (SQLite) |
| Multi-tenancy | Complexity | Phase 5 |
| Mobile UI | Scope | Phase 6+ |

---

## Chunk Breakdown

| Chunk | Description | Depends On | Tests (est) |
|-------|-------------|------------|-------------|
| **4.1** | Extended Eigenvectors (7D) + 12 Cosmotechnics | — | 25 |
| **4.2** | 15 New Citizens (5 archetypes × 3 each) | 4.1 | 35 |
| **4.3** | Coalition/Reputation Mechanics | 4.2 | 30 |
| **4.4** | Web UI Scaffold (Textual or marimo) | — | 20 |
| **4.5** | Real-time Event Bridge (WebSocket/NATS) | 4.4 | 20 |
| **4.6** | Dashboard Panels (map, inspector, stream) | 4.5 | 25 |
| **4.7** | API Surface + Metering | 4.3 | 25 |
| **4.8** | Integration Tests + Demo Script | 4.6, 4.7 | 30 |

**Parallel Tracks**:
```
Track A (Citizens): 4.1 → 4.2 → 4.3 → 4.7
Track B (UI):       4.4 → 4.5 → 4.6
Merge:              4.8
```

**Estimated Tests**: 343 (current) + ~210 = ~553

---

## Entropy Budget

| Phase | Allocation | Purpose |
|-------|------------|---------|
| PLAN | 5% | Scope exploration, heritage insights |
| RESEARCH | 10% | marimo vs Textual, WebSocket patterns |
| DEVELOP | 5% | API design alternatives |
| IMPLEMENT | 10% | Wiring experiments, dead-ends |
| REFLECT | 5% | Meta-learning capture |

**Total**: 35% reserved. Spent: 5% (this PLAN).

---

## RESEARCH Questions

1. **UI Technology**: marimo vs Textual? Reactivity vs TUI ecosystem.
2. **LLM Budget**: How many of 25 citizens can be LLM-backed? K-gent reuse?
3. **Coalition Detection**: Clique finding vs simpler threshold?
4. **Reputation Propagation**: PageRank variant or diffusion model?
5. **Metering Granularity**: Per-turn vs per-citizen-day billing?

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `agents/town/eigenvectors.py` | CREATE | 7D eigenvectors, 12 cosmotechnics |
| `agents/town/archetypes.py` | CREATE | Builder, Trader, Healer, Scholar, Watcher |
| `agents/town/coalition.py` | CREATE | Coalition detection, action, decay |
| `agents/town/environment.py` | MODIFY | Add 15 new citizens |
| `agents/i/screens/town.py` | CREATE | Town visualization (if Textual) |
| `protocols/api/town.py` | CREATE | API endpoints |
| `protocols/streaming/town_bridge.py` | CREATE | Event streaming |

---

## Exit Criteria (PLAN Phase)

- [x] Chunks defined with dependencies
- [x] Technology choice (marimo vs Textual) identified as RESEARCH question
- [x] Non-goals documented
- [x] Entropy budget allocated
- [x] Heritage papers incorporated
- [x] Continuation prompt for RESEARCH prepared

---

## Process Metrics

| Metric | Value |
|--------|-------|
| Phase | PLAN |
| Current tests | 343 (town), 16,602 (total) |
| Estimated new tests | ~210 |
| Entropy sip | 0.05 |
| Branches surfaced | 2 (UI tech, LLM budget) |

---

*⟿[DEVELOP] RESEARCH complete. Continue to DEVELOP phase.*
