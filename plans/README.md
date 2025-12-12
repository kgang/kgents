# Plans: AGENTESE-Organized Implementation Roadmap

> *"The noun is a lie. There is only the rate of change."*

This directory contains implementation plans organized by AGENTESE context paths.

---

## Directory Structure

```
plans/
├── README.md                    # This file: overview + decision log
├── _status.md                   # Implementation status matrix
├── world/
│   └── k8-gents.md              # world.cluster.* (K8s infrastructure)
├── self/
│   ├── stream.md                # self.stream.* (Store Comonad, ContextProjector)
│   ├── memory.md                # self.memory.* (D-gent, Ghost cache)
│   ├── cli.md                   # self.cli.* (ResilientClient, hollowing)
│   └── interface.md             # self.interface.* (I-gent v2.5, Semantic Flux)
├── void/
│   ├── capital.md               # void.capital.* (Social capital, Fool's Bypass)
│   └── entropy.md               # void.entropy.* (Metabolism, tithe)
├── concept/
│   ├── creativity.md            # concept.blend.* + self.judgment.* (ICCC v2.5)
│   └── lattice.md               # concept.*.define (Genealogical typing)
├── agents/
│   ├── t-gent.md                # Testing agents (Types I-V)
│   └── u-gent.md                # Utility agents (Tool use)
└── _archive/                    # Superseded plans
```

---

## Decision Log

All major architectural decisions are recorded here with rationale.

| Date | Decision | Rationale | Plan Reference |
|------|----------|-----------|----------------|
| 2025-12-11 | **Reject Dapr** | K8s Operator IS the actor runtime; Dapr adds bloat without value. Keep stack hollow. | `world/k8-gents.md` |
| 2025-12-11 | **Store Comonad** | `ContextWindow` uses `(S -> A, S)` structure. `duplicate()` enables Modal Scope via Git branching. | `self/stream.md` |
| 2025-12-11 | **ContextProjector (not Lens)** | Lossy compression violates Get-Put law. Use Galois Connection semantics. | `self/stream.md` |
| 2025-12-11 | **Resource Accounting (not Linear Types)** | Python cannot enforce linearity at type level. Runtime token ledger instead. | `self/stream.md` |
| 2025-12-11 | **ResilientClient as LogosNode** | The client IS a node in the AGENTESE graph, not just a consumer. | `self/cli.md` |
| 2025-12-11 | **Capital Ledger (Fool's Bypass)** | Prevent bureaucratic gridlock. Agents spend earned trust to bypass safety checks. | `void/capital.md` |
| 2025-12-11 | **CLI Hollowing via gRPC** | CLI becomes "glass terminal"—parse, invoke, format. Business logic in Cortex daemon. | `self/cli.md` |
| 2025-12-11 | **Ghost Protocol** | Three-layer fallback (gRPC → Ghost cache → kubectl). Never blind. | `self/cli.md` |
| 2025-12-11 | **T-gent/U-gent separation** | T-gents are endofunctors (internal testing). U-gents are boundary morphisms (external tools). | `agents/t-gent.md`, `agents/u-gent.md` |
| 2025-12-11 | **Dual-lane pheromones** | Fast lane (logs) vs slow lane (CRDs). Avoid etcd hammer. | `self/stream.md` |
| 2025-12-11 | **Durable Execution: Temporal + CRD** | Temporal default for complex workflows; CRD state machine as lightweight fallback for simpler tasks. | `world/k8-gents.md` |
| 2025-12-11 | **Modal Scope: Git branches** | Git branches as native technology for counterfactuals. Overlap with Y-gent/D-gent at implementer discretion. | `self/stream.md` |
| 2025-12-11 | **Bypass Cost: Exponential** | High-risk bypasses become prohibitive. Protects against abuse. | `void/capital.md` |
| 2025-12-11 | **Capital Decay: Configurable (0.01 default)** | Kent needs data/experience before committing. Implement with configurable rate. | `void/capital.md` |
| 2025-12-11 | **Event-Sourced Ledger** | "The noun is a lie." Balance is derived projection, not stored state. Solves concurrency, provides audit trail. | `void/capital.md` |
| 2025-12-11 | **Token Lifecycle: Context Managers** | Pythonic linearity approximation. `with ledger.issue(...) as budget:` enforces scope via syntax. | `void/capital.md` |
| 2025-12-11 | **Capital as Capability (OCap)** | BypassToken is unforgeable object. Gate accepts token, not agent name. Satisfies "No View From Nowhere". | `void/capital.md` |
| 2025-12-11 | **Algebraic Cost Functions** | Composable cost factors: `COST = BASE + RISK_PREMIUM + JUDGMENT_DEFICIT`. Testable, transparent. | `void/capital.md` |
| 2025-12-11 | **Reject Phantom Types** | Fighting Python's type system violates Joy-Inducing. Use context managers instead. | `void/capital.md` |
| 2025-12-11 | **Ledger Dependency Injection** | Logos accepts specific Ledger instance. Enables test isolation. Default is ephemeral in-memory. | `void/capital.md` |
| 2025-12-11 | **I-gent v2.5: Semantic Flux** | Reject v1.0 (too poetic) AND v2.0 (server rack). Agents are currents, not rooms. Block elements for density. | `self/interface.md` |
| 2025-12-11 | **Textual Framework** | Use Textual (not pure Rich) for reactive programming and web deployment via `textual serve`. | `self/interface.md` |
| 2025-12-11 | **Glitch as Feature** | Errors/void.* render as Unicode corruption (Zalgo), not red boxes. Accursed Share made visible. | `self/interface.md` |
| 2025-12-11 | **AGENTESE HUD** | Typing paths draws visible morphism arrows. Category theory in real-time. | `self/interface.md` |
| 2025-12-11 | **W-gent Overlay Mode** | Hold `w` for wire overlay, release to return. Not separate spawn. | `self/interface.md` |
| 2025-12-11 | **Processing Waveforms** | Logical work = square wave; creative work = noisy wave. Texture visible. | `self/interface.md` |
| 2025-12-11 | **Deep Earth Color Palette** | Charcoal base, amber active, slate dormant, pink/purple accents. | `self/interface.md` |
| 2025-12-11 | **Single operator pod** | Sufficient for <100 agents; simpler than 3 separate pods. kopf handles multiplexing. | `world/k8-gents.md` |
| 2025-12-11 | **L-gent HTTP wrapper** | Pure library needs server for K8s deployment. HTTP over gRPC for simplicity. | `world/k8-gents.md` |
| 2025-12-11 | **Cognitive probes via ClaudeCLIRuntime** | LLM health != HTTP 200. Use existing `claude -p` runtime. | `world/k8-gents.md` |

---

## Decisions on the Horizon

These require Kent's input before implementation:

### 1. Temporal/CRD Division of Labor

**Question**: When does a workflow use Temporal vs. CRD state machine?

**Proposed Heuristic** (Heterarchical Principle—Dual Loop):
- **CRDs for Loop Mode (State)**: Represent current observed reality (`world.cluster.*`). Kubernetes controllers fit the Observe→Act homeostasis loop.
- **Temporal for Function Mode (Flow)**: Handle `A >> B >> C` composition where steps may take days or fail repeatedly. CRDs are poor at sequential orchestration.
- **Interface**: Operator (Loop mode) spawns Temporal workflow (Function mode) to effect change, updates CRD status on completion.

**Status**: Hybrid decided. Define step-count/duration threshold in implementation.

### 2. Y-gent / D-gent / Git Branch Layering

**Question**: How do Git branches integrate with Y-gent topology and D-gent state?

**Proposed Layering** (Puppet Construction Principle):

| Layer | Role | Analogy |
|-------|------|---------|
| **Git** | Puppet (Substrate) | Raw machinery for branching realities. Implementation of `time.*` |
| **D-gent** | Lens (Observer) | Reads/writes Git branch as coherent State. Enforces timeline isolation. |
| **Y-gent** | Weaver (Strategy) | Decides *when* to branch/merge. Governs the Dialectic. |

**Example**: Y-gent invokes `concept.strategy.fork` → uses Git puppet to create branch → spawns D-gent to observe new branch.

**Status**: Layering clarified. Document patterns as they emerge in implementation.

### 3. Capital Decay Model

**Question**: Time-based decay alone, or activity-based?

**Proposed Enhancement** (Accursed Share—Void Context):
- **Risk of static decay**: Too slow → oligarchs (violates Heterarchical). Too fast → trust can't accumulate.
- **Activity-Based Component**: Consider transactional decay—bypass cost scales with total system capital, forcing continuous value creation.
- **Starting Point**: 0.01 time-based + observe patterns before adding activity component.

**Status**: Start with configurable time-based (0.01). Revisit activity-based after collecting metrics.

### 4. JIT Observability (Forensic Trace)

**Question**: How to debug JIT-compiled Symbionts that may vanish after execution?

**Requirement** (Transparent Infrastructure):
- Every JIT-compiled agent must dump generated source to `time.trace.{hash}` *before* execution.
- Errors must reference this trace: "Error in generated agent [Hash]. Source at `time.trace.abc123`."
- Never let the magic hide the machinery when things break.

**Status**: Add to Phase 2 (Comonad) implementation requirements.

---

## Cross-References

| Plan | AGENTESE Context | Key Deliverables |
|------|------------------|------------------|
| `world/k8-gents.md` | `world.cluster.*` | CRDs, Operators, Terrarium TUI |
| `self/stream.md` | `self.stream.*` | Store Comonad, ContextProjector, Crystals |
| `self/memory.md` | `self.memory.*` | Ghost cache, D-gent state |
| `self/cli.md` | `self.cli.*` | ResilientClient, hollowed handlers |
| `self/interface.md` | `self.interface.*` | I-gent v2.5, Semantic Flux, AGENTESE HUD |
| `void/capital.md` | `void.capital.*` | Capital Ledger, Fool's Bypass |
| `void/entropy.md` | `void.entropy.*` | Metabolism, tithe, fever |
| `concept/lattice.md` | `concept.*.define` | Genealogical typing, lineage enforcement |
| `concept/creativity.md` | `concept.blend.*`, `self.judgment.*` | Blending, Wundt Curator, Critic's Loop |
| `agents/t-gent.md` | (internal) | Types I-V testing agents |
| `agents/u-gent.md` | (external) | Tool use, MCP integration |

---

## Principles Applied

All plans follow `spec/principles.md`:

| Principle | How Applied |
|-----------|-------------|
| **Tasteful** | Rejected Dapr; keep stack hollow |
| **Curated** | Tiered command hollowing; not everything gets hollowed |
| **Ethical** | Observer required for all invocations |
| **Joy-Inducing** | Fever Glitch in TUI; Observatory design |
| **Composable** | Store Comonad structure; Lenses compose |
| **Heterarchical** | Capital Ledger: authority is earned |
| **Generative** | Proto → stubs → handlers |
| **Transparent Infrastructure** | `[GHOST]` prefix; verbose mode |
| **Graceful Degradation** | Three-layer fallback |
| **Accursed Share** | Metabolism + tithe + fever |

---

*"Plans are worthless, but planning is everything." — Eisenhower*
