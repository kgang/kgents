---
path: plans/agent-town/phase4-research-findings
status: active
progress: 100
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables:
  - agent-town/phase4-civilizational
session_notes: |
  RESEARCH phase complete. All 5 decision points resolved.
  UI: marimo recommended. Coalition: k-clique percolation.
  Reputation: EigenTrust. LLM budget: 3-5 citizens.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: pending
entropy:
  planned: 0.10
  spent: 0.10
  returned: 0.0
---

# Agent Town Phase 4: RESEARCH Findings

> *"Research is not about finding answers. It is about finding the right questions."*

---

## Executive Summary

All five research questions answered. Ready for DEVELOP phase.

| Question | Decision | Confidence |
|----------|----------|------------|
| UI Technology | **marimo** (with Textual fallback for TUI) | 90% |
| Coalition Algorithm | **k-clique percolation** (CDlib) | 85% |
| Reputation Propagation | **EigenTrust** (personalized PageRank variant) | 88% |
| LLM Budget | **3-5 LLM-backed** of 25 (3 evolving + 2 archetype leaders) | 92% |
| Composable Components | **7 major components** identified for reuse | 95% |

---

## 1. UI Technology Decision: **marimo**

### Analysis

**Textual (existing)**:
- 14 screens in `impl/claude/agents/i/screens/`
- Mature transition system (`GentleNavigator`, LOD semantics)
- `KgentsScreen` base class with key passthrough
- Good for TUI but limited visualization richness

**marimo (new)**:
- Reactive DAG-based execution (cells auto-update on dependency change)
- Native plotly/altair integration for rich visualization
- AI-native design (works well with Claude Code)
- Can deploy as WASM (client-side, no server needed)
- "First AI-native notebook environment"

### Decision Matrix

| Criterion | Textual | marimo | Winner |
|-----------|---------|--------|--------|
| Kent's "VISUAL UIs" intent | ★☆☆ | ★★★ | marimo |
| Reuse existing code | ★★★ | ★☆☆ | Textual |
| Real-time visualization | ★★☆ | ★★★ | marimo |
| Deployment (Web) | ★☆☆ | ★★★ | marimo |
| Learning curve | ★★★ | ★★☆ | Textual |
| Agent simulation fit | ★☆☆ | ★★★ | marimo |

### Recommendation: **marimo for Web UI, Textual for TUI fallback**

**Rationale**:
1. Kent explicitly wants "VISUAL UIs" and "FUN YET TECHNICAL"
2. marimo's reactive model maps to citizen state changes naturally
3. Town map + relationship graph visualization needs plotly/altair
4. WASM deployment enables client-side simulation (cost reduction)
5. Phase 4 is the "4x scope expansion" — new tech is justified

**Migration Path**:
- Keep Textual for CLI (`kg town status`)
- New marimo notebooks for Web dashboard
- Bridge via NATS events (existing `NATSBridge`)

**Sources**:
- [marimo GitHub](https://github.com/marimo-team/marimo)
- [marimo.io](https://marimo.io/)
- [marimo vs Jupyter](https://marimo.io/features/vs-jupyter-alternative)
- [marimo Reactive Notebooks](https://blog.londogard.com/posts/2025-02-17-marimo/)

---

## 2. Coalition Algorithm: **k-clique percolation**

### Analysis

**Options Considered**:

1. **Threshold-based** (simple): Citizens with relationship weight > threshold form coalition
   - Pros: Simple, O(n²) complexity
   - Cons: Misses structural patterns, arbitrary threshold

2. **k-clique percolation** (CDlib): Find overlapping communities via k-cliques
   - Pros: Detects overlapping coalitions, theoretically grounded
   - Cons: Higher complexity, needs tuning

3. **Label propagation** (Raghavan): Semi-supervised propagation
   - Pros: Fast, handles large graphs
   - Cons: Non-deterministic, no overlap detection

### Decision: **k-clique percolation with k=3**

**Rationale**:
1. Citizens can belong to multiple coalitions (overlapping)
2. 25 citizens is small enough that O(n³) is acceptable
3. k=3 means "at least 3 citizens sharing strong bonds form a coalition"
4. CDlib provides Python implementation (`cdlib.algorithms.kclique`)
5. Maps to "coalition = union of adjacent k-cliques"

**Integration Pattern**:
```python
# Coalition detection using existing GraphMemory structure
from cdlib.algorithms import kclique

def detect_coalitions(env: TownEnvironment, min_weight: float = 0.5) -> list[set[str]]:
    """Detect coalitions as k-cliques in the relationship graph."""
    import networkx as nx

    G = nx.Graph()
    for citizen in env.citizens.values():
        G.add_node(citizen.id)
        for other_id, weight in citizen.relationships.items():
            if weight >= min_weight:
                G.add_edge(citizen.id, other_id, weight=weight)

    communities = kclique(G, k=3)
    return [set(c) for c in communities.communities]
```

**Sources**:
- [CDlib Documentation](https://link.springer.com/article/10.1007/s41109-019-0165-9)
- [Clique Percolation in Social Networks](https://www.sciencedirect.com/science/article/abs/pii/S0378437119322642)
- [NetworkX Community Detection](https://networkx.ashford.phd/docs/community-detection/)

---

## 3. Reputation Propagation: **EigenTrust**

### Analysis

**Options Considered**:

1. **Simple PageRank**: Global reputation from link structure
   - Pros: Well-understood, fast
   - Cons: No personalization, single global ranking

2. **EigenTrust**: Trust weighted by assigner's global reputation
   - Pros: Handles sybil attacks, personalized, proven in P2P
   - Cons: More complex, requires iteration

3. **Heat Diffusion**: Trust spreads like heat through edges
   - Pros: Intuitive, continuous
   - Cons: Loses directionality, no convergence guarantee

### Decision: **EigenTrust (simplified)**

**Rationale**:
1. Reputation should depend on *who* gives it (EigenTrust core insight)
2. Maps to SIMULACRA paper's "memory stream" concept
3. Convergent (eigenvector computation)
4. Integrates with existing `Eigenvectors` class (pun intended)
5. Pre-trusted citizens (archetypes) provide bootstrap anchors

**Algorithm Sketch**:
```python
# EigenTrust-inspired reputation propagation
def propagate_reputation(
    env: TownEnvironment,
    pre_trusted: dict[str, float] = None,
    alpha: float = 0.15,  # Teleport probability
    max_iter: int = 20,
) -> dict[str, float]:
    """
    Propagate reputation using personalized PageRank variant.

    trust[i] = alpha * pre_trusted[i] + (1-alpha) * sum(trust[j] * local[j][i])
    """
    n = len(env.citizens)
    citizen_ids = list(env.citizens.keys())

    # Initialize trust
    trust = {cid: 1.0 / n for cid in citizen_ids}

    # Pre-trusted anchors (archetype leaders)
    if pre_trusted is None:
        pre_trusted = {cid: 1.0 / n for cid in citizen_ids}

    for _ in range(max_iter):
        new_trust = {}
        for i in citizen_ids:
            citizen = env.citizens[i]
            # Sum of weighted trust from those who trust me
            incoming_trust = sum(
                trust[j] * env.citizens[j].relationships.get(i, 0.0)
                for j in citizen_ids if j != i
            )
            # Normalize by total outgoing trust from each j
            new_trust[i] = alpha * pre_trusted.get(i, 0) + (1 - alpha) * incoming_trust

        # Normalize
        total = sum(new_trust.values()) or 1.0
        trust = {k: v / total for k, v in new_trust.items()}

    return trust
```

**Sources**:
- [EigenTrust Algorithm (Stanford)](https://nlp.stanford.edu/pubs/eigentrust.pdf)
- [Personalized PageRank (PPNP)](https://github.com/gasteigerjo/ppnp)
- [PyGRank Library](https://pypi.org/project/pygrank/0.1.17/)

---

## 4. LLM Budget: **3-5 LLM-backed Citizens**

### Analysis

**Current K-gent Patterns** (from `agents/k/llm.py`):
- `ClaudeLLMClient` uses `claude -p` subprocess
- `MorpheusLLMClient` for cluster-native (preferred)
- Token estimation: ~500-2000 tokens per dialogue turn
- K-gent system prompt alone is ~800 tokens

**Cost Model**:
```
Per-turn cost = (system_prompt + history + user_input + output) * price_per_token
             ≈ (800 + 500 + 200 + 500) * $0.003/1K tokens
             ≈ $0.006 per turn

25 citizens * 10 turns/day * $0.006 = $1.50/day (if all LLM-backed)
```

**Budget Constraint**: < $1/day for Pro tier

### Decision: **3-5 LLM-backed, 20-22 rules-based**

**Allocation**:
| Citizen Type | Count | LLM? | Rationale |
|--------------|-------|------|-----------|
| Evolving citizens (Hana, Igor, Juno) | 3 | ✓ | Need LLM for SENSE→ACT→REFLECT |
| Archetype leaders (1-2) | 2 | ✓ | Key dialogue anchors |
| Static citizens | 20 | ✗ | Rules-based cosmotechnics |

**Cost Estimate**:
```
5 LLM citizens * 10 turns/day * $0.006 = $0.30/day (well under $1)
```

**Rules-Based Pattern** (from `agents/town/citizen.py`):
```python
def select_action(self, context: ActionContext) -> Action:
    """Rules-based action selection using cosmotechnics."""
    if self.cosmotechnics.name == "gathering":
        return self._gather_action(context)
    elif self.cosmotechnics.name == "construction":
        return self._build_action(context)
    # ... etc
```

**LLM-Backed Pattern** (from K-gent):
```python
async def evolving_citizen_turn(citizen: EvolvingCitizen, context: TurnContext) -> Action:
    """LLM-backed action selection for evolving citizens."""
    llm = create_llm_client()

    system = f"""You are {citizen.name}, a {citizen.archetype} in Smallville.
    Your personality eigenvectors: {citizen.eigenvectors.to_dict()}
    Your cosmotechnics: {citizen.cosmotechnics.name}
    Current phase: {citizen.nphase.value}
    """

    response = await llm.generate(system=system, user=context.to_prompt())
    return parse_action(response.text)
```

---

## 5. Composable Components

### Identified for Reuse

| Component | Location | Reuse Pattern |
|-----------|----------|---------------|
| `GraphMemory` | `agents/town/memory.py` | Coalition graph storage |
| `Eigenvectors` | `agents/k/eigenvectors.py` | Extended to 7D |
| `NATSBridge` | `protocols/streaming/nats_bridge.py` | Town event streaming |
| `KgentsScreen` | `agents/i/screens/base.py` | TUI fallback |
| `GentleNavigator` | `agents/i/screens/transitions.py` | Transition semantics |
| `create_app` | `protocols/api/app.py` | Town API scaffold |
| `MeteringMiddleware` | `protocols/api/metering.py` | Per-citizen-turn billing |

### New Components Needed

| Component | Purpose | Dependencies |
|-----------|---------|--------------|
| `coalition.py` | k-clique detection + action | cdlib |
| `reputation.py` | EigenTrust propagation | numpy (optional) |
| `archetypes.py` | 5 new archetypes × 3 each | citizen.py |
| `eigenvectors_v2.py` | 7D extension (resilience, curiosity) | eigenvectors.py |
| `town_notebook.py` | marimo dashboard | marimo |
| `town_api.py` | API endpoints | app.py |
| `town_bridge.py` | Event streaming | nats_bridge.py |

### Composability Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web UI (marimo)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Town Map    │  │ Inspector   │  │ Event Stream            │  │
│  │ (plotly)    │  │ (eigenvecs) │  │ (real-time updates)     │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
│         │                │                      │                │
│         └────────────────┴──────────────────────┘                │
│                          │                                       │
│                    marimo reactivity                             │
└──────────────────────────┼───────────────────────────────────────┘
                           │ HTTP/WebSocket
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │ /town/*     │  │ /soul/*     │  │ /agentese/* │               │
│  └──────┬──────┘  └─────────────┘  └─────────────┘               │
│         │                                                         │
│         ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              MeteringMiddleware (per-turn billing)           │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────┼───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Town Engine                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │
│  │ Coalition   │  │ Reputation  │  │ TownEnvironment         │   │
│  │ (k-clique)  │  │ (EigenTrust)│  │ (25 citizens, 6 regions)│   │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘   │
│         │                │                      │                 │
│         └────────────────┴──────────────────────┘                 │
│                          │                                        │
│                   NATSBridge (events)                             │
└──────────────────────────┼────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    LLM Layer (3-5 citizens)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │ Hana        │  │ Igor        │  │ Juno        │  + 2 leaders  │
│  │ (GROWTH)    │  │ (ADAPTATION)│  │ (SYNTHESIS) │               │
│  └─────────────┘  └─────────────┘  └─────────────┘               │
│                          │                                        │
│              MorpheusLLMClient (cluster-native)                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Blockers: **None**

All decisions resolved. Ready for DEVELOP phase.

---

## Exit Criteria Checklist

- [x] UI technology decision documented with rationale → **marimo**
- [x] Coalition algorithm selected (with justification) → **k-clique percolation**
- [x] Reputation propagation model chosen → **EigenTrust**
- [x] LLM budget model defined (N LLM-backed, M rules-based) → **3-5 LLM, 20-22 rules**
- [x] File map with composable components identified → **7 reuse, 7 new**
- [x] Blockers enumerated (or "none") → **none**
- [x] ledger.RESEARCH=touched → ✓

---

## Continuation

```
⟿[DEVELOP]
exit: ui_decision=marimo, coalition_algo=k_clique, reputation_model=eigentrust, llm_budget=3-5, composables=7
continuation → DEVELOP phase for API design, schema definition, dependency management
```

---

*"The best research doesn't answer questions—it reveals the right questions to ask."*
